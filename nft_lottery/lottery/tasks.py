from celery import shared_task
from django.utils import timezone
from django.db import transaction
from .models import Raffle
from .services import select_winner


@shared_task
def check_unlocked_raffles():
    """
    Periodic task to check for unlockable raffles that reached min_participants
    but don't have unlocked_at set yet.
    This handles cases where entries were added outside of enter_raffle() or
    if the unlock check failed during entry creation.
    """
    from datetime import timedelta
    
    unlockable_raffles = Raffle.objects.filter(
        type__code="unlockable",
        min_participants_to_unlock__isnull=False,
        unlocked_at__isnull=True,
        is_active=True,
        is_finished=False
    ).select_related('type')
    
    updated_count = 0
    for raffle in unlockable_raffles:
        entry_count = raffle.entries.count()
        if entry_count >= raffle.min_participants_to_unlock:
            now = timezone.now()
            with transaction.atomic():
                raffle.unlocked_at = now
                raffle.start_at = now + timedelta(days=raffle.draw_delay_days)
                raffle.save(update_fields=['unlocked_at', 'start_at'])
                updated_count += 1
    
    return f"Checked {unlockable_raffles.count()} raffles, unlocked {updated_count}"


@shared_task
def select_raffle_winners():
    """
    Periodic task to select winners for raffles where start_at has passed
    and the raffle is not yet finished.
    """
    now = timezone.now()
    ready_raffles = Raffle.objects.filter(
        start_at__lte=now,
        is_finished=False,
        is_active=True
    ).select_related('type')
    
    results = []
    for raffle in ready_raffles:
        try:
            result = select_winner(raffle)
            results.append({
                "raffle_id": raffle.id,
                "raffle_name": raffle.name,
                "status": "success",
                "winner_user_id": result["winner"].user.id,
                "winner_username": result["winner"].user.username,
            })
        except ValueError as e:
            results.append({
                "raffle_id": raffle.id,
                "raffle_name": raffle.name,
                "status": "error",
                "error": str(e),
            })
        except Exception as e:
            results.append({
                "raffle_id": raffle.id,
                "raffle_name": raffle.name,
                "status": "error",
                "error": str(e),
            })
    
    return {
        "checked": ready_raffles.count(),
        "results": results,
    }

