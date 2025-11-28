from decimal import Decimal
from django.db import transaction
from payments.models import CreditTransaction, TokenTransaction


@transaction.atomic
def purchase_product(user, product):
    """
    Purchase a product for a user.
    
    This function handles the entire purchase process atomically:
    - Validates sufficient credits
    - Deducts credits from user balance
    - Adds reward tokens to user balance
    - Creates transaction records
    
    Args:
        user: The user making the purchase
        product: The product to purchase
        
    Returns:
        dict: Contains new_credit_balance and new_token_balance
        
    Raises:
        ValueError: If user has insufficient credits
    """
    price = Decimal(str(product.price_credits))
    reward_tokens = Decimal(str(product.reward_tokens))
    
    # Validate sufficient credits
    if user.credit_balance < price:
        raise ValueError("Insufficient credits")
    
    # Deduct credits and add tokens
    user.credit_balance -= price
    user.token_balance += reward_tokens
    user.save(update_fields=['credit_balance', 'token_balance'])
    
    # Create transaction records
    CreditTransaction.objects.create(
        user=user,
        amount=price,
        type="spend"
    )
    
    TokenTransaction.objects.create(
        user=user,
        amount=reward_tokens,
        type="reward"
    )
    
    return {
        "new_credit_balance": str(user.credit_balance),
        "new_token_balance": str(user.token_balance),
    }


