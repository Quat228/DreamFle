from datetime import timedelta

from django.db import transaction
from django.db.models import F
from django.utils import timezone

from tasks.services import create_scheduled_task
from lottery.models import Entry, Raffle
from lottery.services import is_raffle_has_min_entries


@transaction.atomic
def purchase_product(user, product, raffle_id):
    """
    Purchase a product for a user and grant entries to a raffle.
    
    This function handles the entire purchase process atomically:
    - Validates raffle exists and is active
    - Gets or creates an Entry for user+raffle
    - Atomically increments entry quantity by product.entries_per_product
    - Returns entry information
    
    Args:
        user: The user making the purchase
        product: The product to purchase
        raffle_id: The ID of the raffle to grant entries for
        
    Returns:
        dict: Contains entry with updated quantity and raffle info
        
    Raises:
        ValueError: If raffle not found, not active, or already finished
    """
    # Validate raffle exists and is active
    try:
        raffle = Raffle.objects.get(id=raffle_id)
    except Raffle.DoesNotExist:
        raise ValueError("Raffle not found")
    
    if not raffle.is_active:
        raise ValueError("Raffle is not active")
    
    if raffle.is_finished:
        raise ValueError("Raffle is already finished")
    
    # Get or create entry for this user+raffle combination
    entry, created = Entry.objects.get_or_create(
        user=user,
        raffle=raffle,
        defaults={'quantity': product.entries_per_product}
    )
    
    if not created:
        # Atomically increment quantity using F() expression to prevent race conditions
        Entry.objects.filter(id=entry.id).update(
            quantity=F('quantity') + product.entries_per_product
        )
        entry.refresh_from_db()
    
    # Check if unlockable raffle has reached min_entries
    if is_raffle_has_min_entries(raffle):
        # Refresh raffle to get updated entry count (sum of quantities)
        raffle.refresh_from_db()
        from django.db.models import Sum
        total_entries = raffle.entries.aggregate(total=Sum('quantity'))['total'] or 0
        
        # If we just reached the threshold and not already unlocked
        if total_entries >= raffle.min_entries_to_unlock and not raffle.unlocked_at:
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
        "entries_granted": product.entries_per_product,
        "total_entries": entry.quantity,
        "raffle_id": raffle.id,
        "raffle_name": raffle.name,
    }



