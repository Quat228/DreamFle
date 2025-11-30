from django.contrib import admin
from django.contrib import messages
import json
from .models import ScheduledTask
from .services import reschedule_task


@admin.register(ScheduledTask)
class ScheduledTaskAdmin(admin.ModelAdmin):
    list_display = (
        'task_type',
        'display_related_object',
        'status',
        'scheduled_for',
        'started_at',
        'completed_at',
        'retry_count',
    )
    list_filter = ('status', 'task_type', 'scheduled_for')
    search_fields = ('celery_task_id',)
    readonly_fields = (
        'content_type',
        'display_related_object',
        'object_id',
        'celery_task_id',
        'created_at',
        'started_at',
        'completed_at',
        'retry_count',
        'display_result',
    )
    
    fieldsets = (
        ('Task Information', {
            'fields': ('task_type', 'display_related_object', 'status', 'scheduled_for')
        }),
        ('Celery Details', {
            'fields': ('celery_task_id', 'task_data')
        }),
        ('Task Result', {
            'fields': ('display_result',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'started_at', 'completed_at')
        }),
        ('Error Handling', {
            'fields': ('error_message', 'retry_count'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('content_type')

    def display_related_object(self, obj):
        """Read-only display of the generic related object."""
        return str(obj.related_object) if obj.related_object else "-"

    display_related_object.short_description = "Related object"
    
    def display_result(self, obj):
        """Display the task result from task_data in a readable format."""
        if not obj.task_data or "result" not in obj.task_data:
            return "-"
        
        result = obj.task_data["result"]
        
        # Format the result nicely
        if isinstance(result, dict):
            # Pretty print dictionary
            return json.dumps(result, indent=2, ensure_ascii=False)
        elif isinstance(result, (list, tuple)):
            # Pretty print list
            return json.dumps(result, indent=2, ensure_ascii=False)
        else:
            # For other types, just convert to string
            return str(result)
    
    display_result.short_description = "Task Result"
    
    def save_model(self, request, obj, form, change):
        """Override save to reschedule if scheduled_for changed."""
        if change and 'scheduled_for' in form.changed_data:
            # scheduled_for was changed, need to reschedule
            old_scheduled_for = form.initial.get('scheduled_for')
            new_scheduled_for = obj.scheduled_for
            
            if old_scheduled_for != new_scheduled_for and obj.status in ('pending', 'scheduled'):
                # Get the task function based on task_type
                try:
                    celery_task_func = self._get_task_function(obj.task_type)
                    task_data = obj.task_data or {}
                    
                    reschedule_task(
                        scheduled_task=obj,
                        new_scheduled_for=new_scheduled_for,
                        celery_task_func=celery_task_func,
                        task_args=task_data.get('args'),
                        task_kwargs=task_data.get('kwargs')
                    )
                    messages.success(request, f"Task rescheduled to {new_scheduled_for}")
                except Exception as e:
                    messages.error(request, f"Failed to reschedule task: {str(e)}")
        
        super().save_model(request, obj, form, change)
    
    def _get_task_function(self, task_type):
        """Get the Celery task function for a given task type."""
        if task_type == 'select_winner':
            from lottery.tasks import select_raffle_winner
            return select_raffle_winner
        # Add more task types as needed
        raise ValueError(f"Unknown task type: {task_type}")
