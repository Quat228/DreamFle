from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from lottery.models import Raffle
from tasks.models import ScheduledTask
from tasks.services import reschedule_task


@transaction.atomic
def update_raffle_start_time(raffle, new_start_at):
    """
    Update raffle start time and reschedule associated task.
    
    This function:
    - Updates raffle.start_at to the new time
    - Finds the associated ScheduledTask for winner selection
    - Reschedules the task to run at the new time
    
    Args:
        raffle: Raffle instance to update
        new_start_at: New datetime for raffle.start_at (timezone-aware)
        
    Returns:
        dict: Contains updated raffle and rescheduled task info
        
    Raises:
        ValueError: If raffle is finished, has no start_at, or task cannot be rescheduled
    """
    # Validate raffle state
    if raffle.is_finished:
        raise ValueError("Cannot update start time for finished raffle")
    
    if not raffle.start_at:
        raise ValueError("Raffle does not have a start_at time set")
    
    # Validate new time is in the future
    now = timezone.now()
    if new_start_at <= now:
        raise ValueError("New start time must be in the future")
    
    # Update raffle start_at
    old_start_at = raffle.start_at
    raffle.start_at = new_start_at
    raffle.save(update_fields=['start_at'])
    
    # Find associated ScheduledTask for this raffle
    raffle_content_type = ContentType.objects.get_for_model(Raffle)
    scheduled_task = ScheduledTask.objects.filter(
        content_type=raffle_content_type,
        object_id=raffle.id,
        task_type='select_winner',
        status__in=('pending', 'scheduled')
    ).first()
    
    task_rescheduled = False
    task_info = None
    
    if scheduled_task:
        # Get the task function
        from lottery.tasks import select_raffle_winner
        
        # Reschedule the task
        reschedule_task(
            scheduled_task=scheduled_task,
            new_scheduled_for=new_start_at,
            celery_task_func=select_raffle_winner,
            task_args=[raffle.id]
        )
        task_rescheduled = True
        task_info = {
            'task_id': scheduled_task.id,
            'old_scheduled_for': old_start_at,
            'new_scheduled_for': new_start_at,
            'celery_task_id': scheduled_task.celery_task_id,
        }
    else:
        # No scheduled task found - might have already run or been cancelled
        # This is not an error, just informational
        pass
    
    return {
        'raffle': raffle,
        'old_start_at': old_start_at,
        'new_start_at': new_start_at,
        'task_rescheduled': task_rescheduled,
        'task_info': task_info,
    }

