from celery import shared_task
from django.utils import timezone
from django.db import transaction

from tasks.services import create_scheduled_task

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
                
                # Create ScheduledTask and schedule Celery task
                create_scheduled_task(
                    related_object=raffle,
                    task_type='select_winner',
                    scheduled_for=raffle.start_at,
                    celery_task_func=select_raffle_winner,
                    task_args=[raffle.id]
                )
                
                updated_count += 1
    
    return f"Checked {unlockable_raffles.count()} raffles, unlocked {updated_count}"


@shared_task
def select_raffle_winner(raffle_id):
    """
    Task to select winner for a specific raffle.
    This is scheduled to run at raffle.start_at time.
    
    Args:
        raffle_id: The ID of the raffle to select winner for
    """
    try:
        raffle = Raffle.objects.get(id=raffle_id)
        result = select_winner(raffle)
        return {
            "raffle_id": raffle.id,
            "raffle_name": raffle.name,
            "status": "success",
            "winner_user_id": result["winner"].user.id,
            "winner_username": result["winner"].user.username,
        }
    except Raffle.DoesNotExist:
        return {
            "raffle_id": raffle_id,
            "status": "error",
            "error": "Raffle not found",
        }
    except ValueError as e:
        return {
            "raffle_id": raffle_id,
            "status": "error",
            "error": str(e),
        }
    except Exception as e:
        return {
            "raffle_id": raffle_id,
            "status": "error",
            "error": str(e),
        }

