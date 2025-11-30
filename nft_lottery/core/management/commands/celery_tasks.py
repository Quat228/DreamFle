from django.core.management.base import BaseCommand
from celery import current_app
from lottery.models import Raffle
from django.utils import timezone
from datetime import datetime


class Command(BaseCommand):
    help = 'Show scheduled Celery tasks and upcoming raffle draws'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed information about each task',
        )

    def handle(self, *args, **options):
        detailed = options['detailed']
        
        # Get Celery inspect object
        inspect = current_app.control.inspect()
        
        # Get scheduled tasks (tasks with ETA - your winner selection tasks)
        scheduled = inspect.scheduled()
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('CELERY TASKS STATUS'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
        
        # Scheduled tasks
        if scheduled:
            self.stdout.write(self.style.SUCCESS('=== Scheduled Tasks (with ETA) ==='))
            total_scheduled = 0
            for worker, tasks in scheduled.items():
                self.stdout.write(f'\nWorker: {self.style.WARNING(worker)}')
                for task in tasks:
                    total_scheduled += 1
                    task_name = task.get('request', {}).get('task', 'Unknown')
                    task_id = task.get('request', {}).get('id', 'Unknown')
                    eta = task.get('eta', 'Unknown')
                    args = task.get('request', {}).get('args', [])
                    
                    if detailed:
                        self.stdout.write(f"  [{total_scheduled}] Task: {self.style.SUCCESS(task_name)}")
                        self.stdout.write(f"      ID: {task_id}")
                        if eta and eta != 'Unknown':
                            try:
                                # Parse ETA timestamp
                                if isinstance(eta, str):
                                    eta_dt = datetime.fromisoformat(eta.replace('Z', '+00:00'))
                                else:
                                    eta_dt = eta
                                now = timezone.now()
                                if eta_dt.tzinfo is None:
                                    eta_dt = timezone.make_aware(eta_dt)
                                time_until = eta_dt - now
                                self.stdout.write(f"      ETA: {eta_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                                self.stdout.write(f"      Time until: {time_until}")
                            except Exception as e:
                                self.stdout.write(f"      ETA: {eta}")
                        else:
                            self.stdout.write(f"      ETA: {eta}")
                        if args:
                            self.stdout.write(f"      Args: {args}")
                    else:
                        # Compact view
                        eta_str = eta
                        if eta and eta != 'Unknown':
                            try:
                                if isinstance(eta, str):
                                    eta_dt = datetime.fromisoformat(eta.replace('Z', '+00:00'))
                                else:
                                    eta_dt = eta
                                if eta_dt.tzinfo is None:
                                    eta_dt = timezone.make_aware(eta_dt)
                                eta_str = eta_dt.strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                pass
                        self.stdout.write(f"  [{total_scheduled}] {task_name} | ETA: {eta_str} | Args: {args}")
                    self.stdout.write('')
            
            self.stdout.write(self.style.SUCCESS(f'\nTotal scheduled tasks: {total_scheduled}'))
        else:
            self.stdout.write(self.style.WARNING('No scheduled tasks found'))
        
        # Active tasks
        active = inspect.active()
        if active:
            self.stdout.write(self.style.SUCCESS('\n=== Active Tasks (currently running) ==='))
            total_active = 0
            for worker, tasks in active.items():
                total_active += sum(1 for _ in tasks)
            self.stdout.write(f'Total active tasks: {total_active}')
        else:
            self.stdout.write(self.style.SUCCESS('\n=== Active Tasks ==='))
            self.stdout.write('No active tasks')
        
        # Reserved tasks
        reserved = inspect.reserved()
        if reserved:
            self.stdout.write(self.style.SUCCESS('\n=== Reserved Tasks (queued, waiting) ==='))
            total_reserved = 0
            for worker, tasks in reserved.items():
                total_reserved += sum(1 for _ in tasks)
            self.stdout.write(f'Total reserved tasks: {total_reserved}')
        else:
            self.stdout.write(self.style.SUCCESS('\n=== Reserved Tasks ==='))
            self.stdout.write('No reserved tasks')
        
        # Raffles with scheduled draws
        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(self.style.SUCCESS('UPCOMING RAFFLE DRAWS'))
        self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
        
        upcoming_raffles = Raffle.objects.filter(
            start_at__gt=timezone.now(),
            is_finished=False,
            is_active=True
        ).order_by('start_at').select_related('type', 'prize')
        
        if upcoming_raffles.exists():
            for raffle in upcoming_raffles:
                time_until = raffle.start_at - timezone.now()
                days = time_until.days
                hours, remainder = divmod(time_until.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                
                self.stdout.write(f"  [{raffle.id}] {self.style.SUCCESS(raffle.name)}")
                self.stdout.write(f"      Type: {raffle.type.name}")
                self.stdout.write(f"      Prize: {raffle.prize.name if raffle.prize else 'N/A'}")
                self.stdout.write(f"      Draw at: {raffle.start_at.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                self.stdout.write(f"      Time until: {days} days, {hours} hours, {minutes} minutes")
                if raffle.unlocked_at:
                    self.stdout.write(f"      Unlocked at: {raffle.unlocked_at.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                self.stdout.write(f"      Entries: {raffle.entries.count()}")
                self.stdout.write('')
            
            self.stdout.write(self.style.SUCCESS(f'Total upcoming raffles: {upcoming_raffles.count()}'))
        else:
            self.stdout.write(self.style.WARNING('No upcoming raffle draws'))
        
        # Raffles that should have been drawn but haven't
        overdue_raffles = Raffle.objects.filter(
            start_at__lte=timezone.now(),
            is_finished=False,
            is_active=True
        ).order_by('start_at').select_related('type', 'prize')
        
        if overdue_raffles.exists():
            self.stdout.write(self.style.ERROR('\n' + '='*60))
            self.stdout.write(self.style.ERROR('OVERDUE RAFFLES (should have been drawn)'))
            self.stdout.write(self.style.ERROR('='*60 + '\n'))
            
            for raffle in overdue_raffles:
                overdue_by = timezone.now() - raffle.start_at
                days = overdue_by.days
                hours, remainder = divmod(overdue_by.seconds, 3600)
                minutes, _ = divmod(remainder, 60)
                
                self.stdout.write(self.style.ERROR(f"  [{raffle.id}] {raffle.name}"))
                self.stdout.write(f"      Should have been drawn: {raffle.start_at.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                self.stdout.write(f"      Overdue by: {days} days, {hours} hours, {minutes} minutes")
                self.stdout.write('')
            
            self.stdout.write(self.style.ERROR(f'Total overdue raffles: {overdue_raffles.count()}'))
            self.stdout.write(self.style.WARNING('⚠️  These raffles may need manual intervention!'))
        
        self.stdout.write('\n')


