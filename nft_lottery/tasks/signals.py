from celery.signals import task_prerun, task_postrun, task_failure
from django.dispatch import receiver
from django.utils import timezone
from .models import ScheduledTask


@receiver(task_prerun)
def task_prerun_handler(sender=None, task_id=None, **kwargs):
    """Update status to 'running' when task starts"""
    try:
        ScheduledTask.objects.filter(celery_task_id=task_id).update(
            status='running',
            started_at=timezone.now()
        )
    except Exception:
        # Task might not have ScheduledTask record (e.g., periodic tasks)
        pass


@receiver(task_postrun)
def task_postrun_handler(sender=None, task_id=None, state=None, retval=None, **kwargs):
    """Update status to 'completed' when task finishes successfully and store result"""
    try:
        scheduled_task = ScheduledTask.objects.filter(celery_task_id=task_id).first()
        if scheduled_task:
            # Get existing task_data or create new dict
            task_data = scheduled_task.task_data or {}
            
            # Store the return value in task_data["result"]
            # Try to serialize retval to JSON-compatible format
            try:
                # If retval is already JSON-serializable (dict, list, str, int, etc.), use it directly
                if isinstance(retval, (dict, list, str, int, float, bool, type(None))):
                    task_data["result"] = retval
                else:
                    # For other types, convert to string representation
                    task_data["result"] = str(retval)
            except Exception as e:
                # If serialization fails, store as string
                task_data["result"] = f"<Unable to serialize result: {str(e)}>"
            
            scheduled_task.task_data = task_data
            scheduled_task.status = 'completed'
            scheduled_task.completed_at = timezone.now()
            scheduled_task.save(update_fields=['status', 'completed_at', 'task_data'])
    except Exception:
        pass


@receiver(task_failure)
def task_failure_handler(sender=None, task_id=None, exception=None, **kwargs):
    """Update status to 'failed' when task fails and store error in task_data"""
    try:
        scheduled_task = ScheduledTask.objects.filter(celery_task_id=task_id).first()
        if scheduled_task:
            # Get existing task_data or create new dict
            task_data = scheduled_task.task_data or {}
            
            # Store error information in task_data
            task_data["result"] = {
                "status": "failed",
                "error": str(exception),
                "error_type": type(exception).__name__ if exception else None
            }
            
            scheduled_task.task_data = task_data
            scheduled_task.status = 'failed'
            scheduled_task.error_message = str(exception)
            scheduled_task.completed_at = timezone.now()
            scheduled_task.save(update_fields=['status', 'error_message', 'completed_at', 'task_data'])
    except Exception:
        pass


