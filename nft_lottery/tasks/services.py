from celery import current_app
from .models import ScheduledTask


def create_scheduled_task(related_object, task_type, scheduled_for, celery_task_func, task_args=None, task_kwargs=None, task_data=None):
    """
    Helper function to create a ScheduledTask and schedule the Celery task.
    
    Args:
        related_object: The object this task is related to (Raffle, Product, etc.)
        task_type: Type of task (e.g., 'select_winner')
        scheduled_for: When the task should run
        celery_task_func: The Celery task function to schedule
        task_args: Arguments to pass to the Celery task
        task_kwargs: Keyword arguments to pass to the Celery task
        task_data: Optional JSON data for the task
    
    Returns:
        tuple: (ScheduledTask instance, Celery AsyncResult)
    """
    # Store task args/kwargs in task_data for rescheduling
    if task_data is None:
        task_data = {}
    if task_args:
        task_data['args'] = task_args
    if task_kwargs:
        task_data['kwargs'] = task_kwargs
    
    # Create ScheduledTask record
    scheduled_task = ScheduledTask.objects.create(
        related_object=related_object,
        task_type=task_type,
        scheduled_for=scheduled_for,
        status='scheduled',
        task_data=task_data
    )
    
    # Schedule the Celery task
    task_args = task_args or []
    task_kwargs = task_kwargs or {}
    result = celery_task_func.apply_async(
        args=task_args,
        kwargs=task_kwargs,
        eta=scheduled_for
    )
    
    # Store Celery task ID
    scheduled_task.celery_task_id = result.id
    scheduled_task.save(update_fields=['celery_task_id'])
    
    return scheduled_task, result


def cancel_scheduled_task(scheduled_task):
    """
    Cancel a scheduled task.
    
    Args:
        scheduled_task: ScheduledTask instance to cancel
    """
    if scheduled_task.celery_task_id:
        try:
            current_app.control.revoke(scheduled_task.celery_task_id, terminate=True)
        except Exception:
            pass  # Task might already be running or completed
    scheduled_task.status = 'cancelled'
    scheduled_task.save(update_fields=['status'])


def reschedule_task(scheduled_task, new_scheduled_for, celery_task_func, task_args=None, task_kwargs=None):
    """
    Reschedule a task to a new time.
    
    Args:
        scheduled_task: ScheduledTask instance to reschedule
        new_scheduled_for: New datetime when the task should run
        celery_task_func: The Celery task function to schedule
        task_args: Arguments to pass to the Celery task (if None, uses task_data)
        task_kwargs: Keyword arguments to pass to the Celery task (if None, uses task_data)
    
    Returns:
        tuple: (ScheduledTask instance, Celery AsyncResult)
    
    Raises:
        ValueError: If task cannot be rescheduled (wrong status)
    """
    # Only reschedule if task is still pending/scheduled
    if scheduled_task.status not in ('pending', 'scheduled'):
        raise ValueError(f"Cannot reschedule task with status '{scheduled_task.status}'")
    
    # Cancel the old Celery task if it exists
    if scheduled_task.celery_task_id:
        try:
            current_app.control.revoke(scheduled_task.celery_task_id, terminate=True)
        except Exception:
            pass  # Task might already be running or completed
    
    # Get task args/kwargs from task_data if not provided
    if task_args is None or task_kwargs is None:
        task_data = scheduled_task.task_data or {}
        if task_args is None:
            task_args = task_data.get('args', [])
        if task_kwargs is None:
            task_kwargs = task_data.get('kwargs', {})
    
    # Schedule new Celery task
    result = celery_task_func.apply_async(
        args=task_args,
        kwargs=task_kwargs,
        eta=new_scheduled_for
    )
    
    # Update with new Celery task ID and time
    scheduled_task.scheduled_for = new_scheduled_for
    scheduled_task.status = 'scheduled'
    scheduled_task.celery_task_id = result.id
    scheduled_task.save(update_fields=['scheduled_for', 'status', 'celery_task_id'])
    
    return scheduled_task, result

