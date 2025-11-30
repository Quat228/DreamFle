from decimal import Decimal
from datetime import timedelta
import hashlib
from django.db import transaction
from django.utils import timezone

from payments.models import TokenTransaction
from tasks.services import create_scheduled_task

from .models import Entry, Winner


@transaction.atomic
def enter_raffle(user, raffle, cost=None):
    """
    Enter a user into a raffle.
    
    This function handles the entire raffle entry process atomically:
    - Validates raffle is active and not finished
    - Validates sufficient tokens
    - Deducts tokens from user balance
    - Creates entry record
    - Creates transaction record
    
    Args:
        user: The user entering the raffle
        raffle: The raffle to enter
        cost: The cost of the raffle (optional)
        
    Returns:
        dict: Contains entry and new_token_balance
        
    Raises:
        ValueError: If raffle is not active, already finished, or user has insufficient tokens
    """
    # Validate raffle status
    if not raffle.is_active:
        raise ValueError("Raffle is not active")
    
    if raffle.is_finished:
        raise ValueError("Raffle is already finished")

    cost_tokens = cost if cost else Decimal(str(raffle.cost_tokens))
    
    # Validate sufficient tokens
    if user.token_balance < cost_tokens:
        raise ValueError("Insufficient tokens")
    
    # Deduct tokens
    user.token_balance -= cost_tokens
    user.save(update_fields=['token_balance'])
    
    # Create entry
    entry = Entry.objects.create(
        user=user,
        raffle=raffle,
        cost_tokens=cost_tokens
    )
    
    # Create transaction record
    TokenTransaction.objects.create(
        user=user,
        amount=cost_tokens,
        type="spend",
    )
    
    # Check if unlockable raffle has reached min_participants
    if raffle.type.code == "unlockable" and raffle.min_participants_to_unlock:
        # Refresh raffle to get updated entry count
        raffle.refresh_from_db()
        entry_count = raffle.entries.count()
        
        # If we just reached the threshold and not already unlocked
        if entry_count >= raffle.min_participants_to_unlock and not raffle.unlocked_at:
            now = timezone.now()
            raffle.unlocked_at = now
            # Set start_at to unlocked_at + draw_delay_days
            raffle.start_at = now + timedelta(days=raffle.draw_delay_days)
            raffle.save(update_fields=['unlocked_at', 'start_at'])

            # Import here to avoid circular import at module load time
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
        "new_token_balance": str(user.token_balance),
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
    
    # Get all entries
    entries = list(raffle.entries.all())
    if not entries:
        raise ValueError("Raffle has no entries")
    
    # Use existing seed (should have been generated when raffle was created)
    if not raffle.winner_selection_seed:
        raise ValueError("Winner selection seed not found. This should have been generated when the raffle was created.")
    
    # Sort entry IDs for consistent ordering
    entry_ids = sorted([str(entry.id) for entry in entries])
    entry_ids_string = ",".join(entry_ids)
    
    # Combine seed + entry IDs
    combined_string = f"{raffle.winner_selection_seed}:{entry_ids_string}"
    
    # Generate SHA256 hash
    selection_hash = hashlib.sha256(combined_string.encode('utf-8')).hexdigest()
    
    # Convert hash to integer and select winner
    selection_index = int(selection_hash, 16) % len(entries)
    winning_entry = entries[selection_index]
    
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
    
    return {
        "winner": winner,
        "selection_seed": raffle.winner_selection_seed,
        "selection_hash": selection_hash,
        "entry_ids": entry_ids,
        "selection_index": selection_index,
        "total_entries": len(entries),
    }


