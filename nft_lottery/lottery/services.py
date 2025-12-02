from datetime import timedelta
import hashlib
from django.db import transaction
from django.db.models import F, Sum
from django.utils import timezone

from tasks.services import create_scheduled_task

from .models import Entry, Winner


def is_raffle_has_min_entries(raffle):
    return raffle.type.code == "unlockable" and raffle.min_entries_to_unlock


@transaction.atomic
def enter_raffle(user, raffle, quantity=1):
    """
    Manually add entries to a raffle for a user (admin/manual entry creation).
    
    This function is primarily for admin use or manual entry creation.
    Regular entries should come from product purchases.
    
    Args:
        user: The user to add entries for
        raffle: The raffle to enter
        quantity: Number of entries to add (default: 1)
        
    Returns:
        dict: Contains entry with updated quantity
        
    Raises:
        ValueError: If raffle is not active or already finished
    """
    # Validate raffle status
    if not raffle.is_active:
        raise ValueError("Raffle is not active")
    
    if raffle.is_finished:
        raise ValueError("Raffle is already finished")
    
    # Get or create entry for this user+raffle combination
    entry, created = Entry.objects.get_or_create(
        user=user,
        raffle=raffle,
        defaults={'quantity': quantity}
    )
    
    if not created:
        # Atomically increment quantity
        Entry.objects.filter(id=entry.id).update(
            quantity=F('quantity') + quantity
        )
        entry.refresh_from_db()
    
    # Check if unlockable raffle has reached min_entries
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

            from lottery.tasks import select_raffle_winner

            # Create ScheduledTask and schedule Celery task
            create_scheduled_task(
                related_object=raffle,
                task_type="select_winner",
                scheduled_for=raffle.start_at,
                celery_task_func=select_raffle_winner,
                task_args=[raffle.id],
            )
    
    return {
        "entry": entry,
        "quantity_added": quantity,
        "total_entries": entry.quantity,
    }


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
    
    if not weighted_entries:
        raise ValueError("Raffle has no valid entries (all quantities are zero)")
    
    # Sort entry IDs for consistent ordering (use original entry IDs, not weighted list)
    entry_ids = sorted([str(entry.id) for entry in entries])
    entry_ids_string = ",".join(entry_ids)
    
    # Combine seed + entry IDs + quantities for transparency
    quantities_info = ",".join([f"{e.id}:{e.quantity}" for e in entries])
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
    raffle.end_at = now
    raffle.winner_selection_hash = selection_hash
    raffle.winner_selection_timestamp = now
    raffle.save(update_fields=['is_active', 'is_finished', 'end_at', 'winner_selection_hash',
                               'winner_selection_timestamp', 'winner_selection_seed'])
    
    # Calculate total entries (sum of quantities)
    total_entries_count = sum(entry.quantity for entry in entries)
    
    return {
        "winner": winner,
        "selection_seed": raffle.winner_selection_seed,
        "selection_hash": selection_hash,
        "entry_ids": entry_ids,
        "selection_index": selection_index,
        "total_entries": total_entries_count,
        "total_entry_records": len(entries),
        "entry_quantities": {str(e.id): e.quantity for e in entries},
    }


