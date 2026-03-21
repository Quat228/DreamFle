from celery import shared_task
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum

from tasks.services import create_scheduled_task

from .models import Raffle
from .services import select_winner


@shared_task
def check_unlocked_raffles():
    """
    Periodic task to check for unlockable raffles that reached min_entries
    but don't have unlocked_at set yet.
    This handles cases where entries were added outside of purchase_product() or
    if the unlock check failed during entry creation.
    """
    from datetime import timedelta
    
    unlockable_raffles = Raffle.objects.filter(
        type__code="unlockable",
        min_entries_to_unlock__isnull=False,
        unlocked_at__isnull=True,
        is_active=True,
        is_finished=False
    ).select_related('type')
    
    updated_count = 0
    for raffle in unlockable_raffles:
        # Sum quantities instead of counting Entry objects
        total_entries = raffle.entries.aggregate(total=Sum('quantity'))['total'] or 0
        if total_entries >= raffle.min_entries_to_unlock:
            now = timezone.now()
            with transaction.atomic():
                raffle.unlocked_at = now
                raffle.start_at = now + timedelta(days=raffle.draw_delay_days)
                raffle.save(update_fields=['unlocked_at', 'start_at'])
                
                # Create ScheduledTask and schedule Celery task for winner selection
                create_scheduled_task(
                    related_object=raffle,
                    task_type='select_winner',
                    scheduled_for=raffle.start_at,
                    celery_task_func=select_raffle_winner,
                    task_args=[raffle.id]
                )
                
                # Schedule notification task 5 minutes before start_at
                notify_time = raffle.start_at - timedelta(minutes=5)
                if notify_time > now:
                    create_scheduled_task(
                        related_object=raffle,
                        task_type='notify_starting',
                        scheduled_for=notify_time,
                        celery_task_func=notify_raffle_starting,
                        task_args=[raffle.id]
                    )
                
                updated_count += 1
    
    return f"Checked {unlockable_raffles.count()} raffles, unlocked {updated_count}"


@shared_task
def notify_raffle_starting(raffle_id):
    """
    Task that runs 5 minutes before raffle start_at.
    Sets raffle status to COUNTDOWN.
    This task is idempotent - safe to run multiple times.
    
    Args:
        raffle_id: The ID of the raffle that's starting soon
    """
    try:
        raffle = Raffle.objects.get(id=raffle_id)
        
        # Only update if still in OPEN status (idempotent)
        if raffle.status == "OPEN" and not raffle.is_finished:
            raffle.status = "COUNTDOWN"
            raffle.save(update_fields=['status'])
        
        return {
            "raffle_id": raffle.id,
            "raffle_name": raffle.name,
            "status": "success",
            "message": f"Raffle {raffle.name} status set to COUNTDOWN",
        }
    except Raffle.DoesNotExist:
        return {
            "raffle_id": raffle_id,
            "status": "error",
            "error": "Raffle not found",
        }
    except Exception as e:
        return {
            "raffle_id": raffle_id,
            "status": "error",
            "error": str(e),
        }


@shared_task
def select_raffle_winner(raffle_id):
    """
    Task to select winner for a specific raffle.
    This is scheduled to run at raffle.start_at time.
    Sets status to FINISHING, then selects winner.
    This task is idempotent - safe to run multiple times.
    
    Args:
        raffle_id: The ID of the raffle to select winner for
    """
    try:
        raffle = Raffle.objects.get(id=raffle_id)
        
        # If already finished, return success (idempotent)
        if raffle.is_finished:
            return {
                "raffle_id": raffle.id,
                "raffle_name": raffle.name,
                "status": "success",
                "message": "Raffle already finished",
            }
        
        # Set status to FINISHING before selecting winner
        if raffle.status != "FINISHING":
            raffle.status = "FINISHING"
            raffle.save(update_fields=['status'])
        
        # Select winner (this will also set is_finished=True)
        result = select_winner(raffle)
        
        # Set status to FINISHED after winner is selected
        raffle.refresh_from_db()
        raffle.status = "FINISHED"
        raffle.save(update_fields=['status'])
        
        # Schedule task to keep FINISHED status for 60 seconds, then cleanup
        from tasks.services import create_scheduled_task
        from datetime import timedelta
        finish_time = timezone.now() + timedelta(seconds=60)
        create_scheduled_task(
            related_object=raffle,
            task_type='cleanup_finished',
            scheduled_for=finish_time,
            celery_task_func=cleanup_finished_raffle,
            task_args=[raffle.id]
        )
        
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


@shared_task
def cleanup_finished_raffle(raffle_id):
    """
    Task that runs 60 seconds after raffle is finished.
    Can be used for cleanup or redirect logic.
    This task is idempotent.
    
    Args:
        raffle_id: The ID of the finished raffle
    """
    try:
        raffle = Raffle.objects.get(id=raffle_id)
        # Status remains FINISHED, this is just for tracking/logging
        return {
            "raffle_id": raffle.id,
            "raffle_name": raffle.name,
            "status": "success",
            "message": f"Raffle {raffle.name} cleanup completed",
        }
    except Raffle.DoesNotExist:
        return {
            "raffle_id": raffle_id,
            "status": "error",
            "error": "Raffle not found",
        }
    except Exception as e:
        return {
            "raffle_id": raffle_id,
            "status": "error",
            "error": str(e),
        }

