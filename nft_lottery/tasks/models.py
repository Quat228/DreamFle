from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class ScheduledTask(models.Model):
    TASK_TYPES = (
        ('select_winner', 'Select Winner'),
        # Add more task types as needed in the future
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )
    
    # Generic relation - can point to any model (Raffle, Product, User, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    related_object = GenericForeignKey('content_type', 'object_id')
    
    task_type = models.CharField(max_length=50, choices=TASK_TYPES)
    celery_task_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    scheduled_for = models.DateTimeField(help_text="When the task should run")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    task_data = models.JSONField(null=True, blank=True, help_text="Additional task-specific data")
    
    class Meta:
        ordering = ['scheduled_for']
        indexes = [
            models.Index(fields=['status', 'scheduled_for']),
            models.Index(fields=['content_type', 'object_id', 'task_type']),
        ]
    
    def __str__(self):
        obj_name = str(self.related_object) if self.related_object else f"{self.content_type} #{self.object_id}"
        return f"{self.get_task_type_display()} for {obj_name} - {self.status}"
