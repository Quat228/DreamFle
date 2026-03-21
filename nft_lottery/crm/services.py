from datetime import timedelta
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from lottery.models import Raffle
from tasks.models import ScheduledTask
from tasks.services import reschedule_task, create_scheduled_task


@transaction.atomic
def update_raffle_start_time(raffle, new_start_at):
    """
    Update raffle start time and reschedule associated tasks.
    
    This function:
    - Updates raffle.start_at to the new time
    - Finds and reschedules the ScheduledTask for winner selection (select_winner)
    - Finds and reschedules the ScheduledTask for notification (notify_starting) to run 5 minutes before new start_at
    - Creates notify_starting task if it doesn't exist (if new_notify_time is in the future)
    
    Args:
        raffle: Raffle instance to update
        new_start_at: New datetime for raffle.start_at (timezone-aware)
        
    Returns:
        dict: Contains updated raffle and rescheduled task info including:
            - task_info: Info about select_winner task rescheduling
            - notify_task_info: Info about notify_starting task rescheduling/creation
        
    Raises:
        ValueError: If raffle is finished, has no start_at, or new_start_at is not in the future
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
    
    # Find associated ScheduledTasks for this raffle
    raffle_content_type = ContentType.objects.get_for_model(Raffle)
    
    # Reschedule select_winner task
    select_winner_task = ScheduledTask.objects.filter(
        content_type=raffle_content_type,
        object_id=raffle.id,
        task_type='select_winner',
        status__in=('pending', 'scheduled')
    ).first()
    
    task_rescheduled = False
    task_info = None
    notify_task_info = None
    
    if select_winner_task:
        # Get the task function
        from lottery.tasks import select_raffle_winner
        
        # Reschedule the select_winner task
        reschedule_task(
            scheduled_task=select_winner_task,
            new_scheduled_for=new_start_at,
            celery_task_func=select_raffle_winner,
            task_args=[raffle.id]
        )
        task_rescheduled = True
        task_info = {
            'task_id': select_winner_task.id,
            'old_scheduled_for': old_start_at,
            'new_scheduled_for': new_start_at,
            'celery_task_id': select_winner_task.celery_task_id,
        }
    
    # Find and reschedule notify_starting task
    notify_starting_task = ScheduledTask.objects.filter(
        content_type=raffle_content_type,
        object_id=raffle.id,
        task_type='notify_starting',
        status__in=('pending', 'scheduled')
    ).first()
    
    # Calculate new notify time (5 minutes before new start_at)
    new_notify_time = new_start_at - timedelta(minutes=5)
    old_notify_time = old_start_at - timedelta(minutes=5) if old_start_at else None
    
    if notify_starting_task:
        # Reschedule existing notify_starting task
        from lottery.tasks import notify_raffle_starting
        
        try:
            reschedule_task(
                scheduled_task=notify_starting_task,
                new_scheduled_for=new_notify_time,
                celery_task_func=notify_raffle_starting,
                task_args=[raffle.id]
            )
            notify_task_info = {
                'task_id': notify_starting_task.id,
                'old_scheduled_for': old_notify_time,
                'new_scheduled_for': new_notify_time,
                'celery_task_id': notify_starting_task.celery_task_id,
                'rescheduled': True,
            }
        except ValueError:
            # Task might not be reschedulable (already running/completed)
            # Create a new one if the time is in the future
            if new_notify_time > now:
                create_scheduled_task(
                    related_object=raffle,
                    task_type='notify_starting',
                    scheduled_for=new_notify_time,
                    celery_task_func=notify_raffle_starting,
                    task_args=[raffle.id]
                )
                notify_task_info = {
                    'task_id': None,
                    'old_scheduled_for': old_notify_time,
                    'new_scheduled_for': new_notify_time,
                    'rescheduled': False,
                    'created_new': True,
                }
    elif new_notify_time > now:
        # No notify_starting task exists, create one if time is in the future
        from lottery.tasks import notify_raffle_starting
        
        create_scheduled_task(
            related_object=raffle,
            task_type='notify_starting',
            scheduled_for=new_notify_time,
            celery_task_func=notify_raffle_starting,
            task_args=[raffle.id]
        )
        notify_task_info = {
            'task_id': None,
            'old_scheduled_for': old_notify_time,
            'new_scheduled_for': new_notify_time,
            'rescheduled': False,
            'created_new': True,
        }
    
    return {
        'raffle': raffle,
        'old_start_at': old_start_at,
        'new_start_at': new_start_at,
        'task_rescheduled': task_rescheduled,
        'task_info': task_info,
        'notify_task_info': notify_task_info,
    }




