from datetime import timedelta
import hashlib
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone

from payments.models import UserCoupon, Coupon
from tasks.services import create_scheduled_task

from .models import Winner


def is_raffle_has_min_entries(raffle):
    return raffle.type.code == "unlockable" and raffle.min_entries_to_unlock


def check_raffle_min_entries(raffle):
    created_task = None
    if is_raffle_has_min_entries(raffle):
        # Refresh raffle to get updated entry count (sum of quantities)
        raffle.refresh_from_db()
        total_entries = raffle.entries.aggregate(total=Sum('quantity'))['total'] or 0

        # If we just reached the threshold and not already unlocked
        if total_entries >= raffle.min_entries_to_unlock and not raffle.unlocked_at:
            now = timezone.now()
            raffle.unlocked_at = now
            # Set start_at to unlocked_at + draw_delay_days
            raffle.start_at = now + timedelta(days=raffle.draw_delay_days)
            raffle.save(update_fields=['unlocked_at', 'start_at'])

            # Import here to avoid circular import at module load time
            from lottery.tasks import select_raffle_winner, notify_raffle_starting

            # Create ScheduledTask and schedule Celery task for winner selection
            created_task = create_scheduled_task(
                related_object=raffle,
                task_type="select_winner",
                scheduled_for=raffle.start_at,
                celery_task_func=select_raffle_winner,
                task_args=[raffle.id],
            )

            # Schedule notification task 5 minutes before start_at
            notify_time = raffle.start_at - timedelta(minutes=5)
            if notify_time > now:
                create_scheduled_task(
                    related_object=raffle,
                    task_type="notify_starting",
                    scheduled_for=notify_time,
                    celery_task_func=notify_raffle_starting,
                    task_args=[raffle.id],
                )

    return created_task, created_task is not None


@transaction.atomic
def select_winner(raffle):
    """
    Select a winner for a raffle using transparent hash-based selection.
    
    This function:
    - Validates raffle is ready (start_at has passed, not finished, has entries)
    - Generates transparent random selection using hash of entries + seed
    - Creates Winner record
    - Marks raffle as finished
    - Stores selection details for transparency
    
    Args:
        raffle: The raffle to select winner for
        
    Returns:
        dict: Contains winner entry and selection details
        
    Raises:
        ValueError: If raffle is not ready for winner selection
    """
    # Validate raffle is ready
    if raffle.is_finished:
        raise ValueError("Raffle is already finished")
    
    if not raffle.start_at:
        raise ValueError("Raffle has no start_at date set")
    
    now = timezone.now()
    if raffle.start_at > now:
        raise ValueError(f"Raffle draw date has not arrived yet (starts at {raffle.start_at})")
    
    # Get all entries with their quantities
    entries = list(raffle.entries.all())
    if not entries:
        raise ValueError("Raffle has no entries")
    
    # Use existing seed (should have been generated when the raffle was created)
    if not raffle.winner_selection_seed:
        raise ValueError("Winner selection seed not found. This should have been generated when the raffle was created.")
    
    # Build weighted entry list: expand entries by their quantity
    # Each quantity unit = one chance in the draw
    weighted_entries = []
    entry_metadata = []  # Track which original entry each weighted entry belongs to
    
    for entry in entries:

        for _ in range(entry.quantity):
            weighted_entries.append(entry)
            entry_metadata.append({
                'original_entry_id': entry.id,
                'user_id': entry.user.id,
            })

        for _ in range(entry.quantity_bonus):
            weighted_entries.append(entry)
            entry_metadata.append({
                'original_entry_id': entry.id,
                'user_id': entry.user.id,
            })
    
    if not weighted_entries:
        raise ValueError("Raffle has no valid entries (all quantities are zero)")
    
    # Sort entry IDs for consistent ordering (use original entry IDs, not weighted list)
    entry_ids = sorted([str(entry.id) for entry in entries])
    entry_ids_string = ",".join(entry_ids)
    
    # Combine seed + entry IDs + quantities (including bonus) for transparency
    quantities_info = ",".join([f"{e.id}:{e.quantity}:{e.quantity_bonus}" for e in entries])
    combined_string = f"{raffle.winner_selection_seed}:{entry_ids_string}:{quantities_info}"
    
    # Generate SHA256 hash
    selection_hash = hashlib.sha256(combined_string.encode('utf-8')).hexdigest()
    
    # Convert hash to integer and select winner from weighted entries
    selection_index = int(selection_hash, 16) % len(weighted_entries)
    winning_entry = weighted_entries[selection_index]
    
    # Create Winner record
    winner = Winner.objects.create(
        raffle=raffle,
        user=winning_entry.user,
        entry=winning_entry
    )
    
    # Update raffle with selection details
    raffle.is_active = False
    raffle.is_finished = True
    raffle.status = "FINISHING"  # Will be set to FINISHED by the task
    raffle.end_at = now
    raffle.winner_selection_hash = selection_hash
    raffle.winner_selection_timestamp = now
    raffle.save(update_fields=['is_active', 'is_finished', 'status', 'end_at', 'winner_selection_hash',
                               'winner_selection_timestamp', 'winner_selection_seed'])

    # WebSocket removed - using polling instead

    # Give coupon bonus for all participants except for winner
    coupon = Coupon.objects.get(type="lost")
    objects_to_create = [
        UserCoupon(coupon=coupon, user=entry.user)
        for entry in entries
        if entry is not winning_entry
    ]

    UserCoupon.objects.bulk_create(objects_to_create)
    
    # Calculate total entries (sum of quantities + bonus entries)
    total_entries_count = sum(entry.quantity + entry.quantity_bonus for entry in entries)
    
    return {
        "winner": winner,
        "selection_seed": raffle.winner_selection_seed,
        "selection_hash": selection_hash,
        "entry_ids": entry_ids,
        "selection_index": selection_index,
        "total_entries": total_entries_count,
        "total_entry_records": len(entries),
        "entry_quantities": {str(e.id): e.quantity + e.quantity_bonus for e in entries},
    }


