from django.db import transaction
from django.db.models import F

from payments.models import ProductPurchase
from lottery.models import Entry, Raffle
from lottery.services import check_raffle_min_entries


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
    check_raffle_min_entries(raffle)

    ProductPurchase.objects.create(product=product, user=user, amount=product.price)
    
    return {
        "entry": entry,
        "entries_granted": product.entries_per_product,
        "total_entries": entry.quantity,
        "raffle_id": raffle.id,
        "raffle_name": raffle.name,
    }



