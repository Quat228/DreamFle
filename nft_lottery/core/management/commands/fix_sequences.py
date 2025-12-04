from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps


class Command(BaseCommand):
    help = "Fix PostgreSQL sequences for all models to prevent primary key conflicts"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Fixing PostgreSQL sequences for all models..."))
        
        fixed_count = 0
        error_count = 0
        
        # Get all models from all apps
        for app_config in apps.get_app_configs():
            for model in app_config.get_models():
                # Only fix sequences for models with auto-incrementing primary keys
                if hasattr(model._meta, 'pk') and hasattr(model._meta.pk, 'auto_created'):
                    if model._meta.pk.auto_created:
                        try:
                            self._fix_sequence_for_model(model)
                            fixed_count += 1
                        except Exception as e:
                            error_count += 1
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Could not fix sequence for {model._meta.label}: {e}"
                                )
                            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Sequence fix complete: {fixed_count} fixed, {error_count} errors"
            )
        )
    
    def _fix_sequence_for_model(self, model):
        """Reset PostgreSQL sequence to the maximum ID in the table"""
        table_name = model._meta.db_table
        sequence_name = f"{table_name}_id_seq"
        
        with connection.cursor() as cursor:
            # Check if sequence exists
            cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM pg_sequences WHERE schemaname = 'public' AND sequencename = %s)",
                [sequence_name]
            )
            sequence_exists = cursor.fetchone()[0]
            
            if not sequence_exists:
                # Sequence doesn't exist, skip this model
                return
            
            # Get the maximum ID from the table
            cursor.execute(f"SELECT COALESCE(MAX(id), 0) FROM {table_name}")
            max_id = cursor.fetchone()[0]
            
            # Reset the sequence to max_id + 1
            # Use false to prevent the next value from being the one we set
            cursor.execute(f"SELECT setval('{sequence_name}', {max_id + 1}, false)")
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Fixed sequence {sequence_name} for {model._meta.label} (set to {max_id + 1})"
                )
            )

