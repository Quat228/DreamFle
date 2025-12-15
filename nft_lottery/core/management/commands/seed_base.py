from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
import json
import os
from django.conf import settings


class Command(BaseCommand):
    help = "Load BASE fixtures (required types and initial data) - uses get_or_create to avoid overwriting"

    def handle(self, *args, **kwargs):
        fixtures = [
            ("product_types", "products"),
            ("prize_types", "products"),
            ("raffle_types", "lottery"),
            ("coupons", "payments"),
        ]

        self.stdout.write(self.style.WARNING("Loading BASE fixtures (safe mode - won't overwrite existing data)..."))

        for fx_name, app_name in fixtures:
            try:
                # Load fixture file
                fixture_path = os.path.join(settings.BASE_DIR, app_name, "fixtures", f"{fx_name}.json")
                
                if not os.path.exists(fixture_path):
                    self.stdout.write(self.style.WARNING(f"Fixture {fx_name} not found at {fixture_path}, skipping..."))
                    continue
                
                with open(fixture_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Import models dynamically
                if app_name == "products":
                    if fx_name == "product_types":
                        from products.models import ProductType as Model
                    elif fx_name == "prize_types":
                        from products.models import PrizeType as Model
                elif app_name == "lottery":
                    from lottery.models import RaffleType as Model
                elif app_name == "payments":
                    if fx_name == "coupons":
                        from payments.models import Coupon as Model
                
                # Use get_or_create to avoid overwriting
                created_count = 0
                skipped_count = 0
                for item in data:
                    fields = item.get("fields", {}).copy()
                    pk = item.get("pk")
                    
                    # Try to get by unique field (code) first, then by pk
                    lookup_field = "code" if "code" in fields else None
                    
                    if lookup_field:
                        # Use code as unique identifier
                        try:
                            obj = Model.objects.get(code=fields["code"])
                            # Object exists, skip to avoid overwriting
                            skipped_count += 1
                            continue
                        except Model.DoesNotExist:
                            pass
                    else:
                        # Try by pk
                        try:
                            obj = Model.objects.get(pk=pk)
                            skipped_count += 1
                            continue
                        except Model.DoesNotExist:
                            pass
                    
                    # Create new object
                    obj = Model.objects.create(pk=pk, **fields)
                    created_count += 1
                
                self.stdout.write(self.style.SUCCESS(
                    f"Processed {fx_name}: {created_count} created, {skipped_count} skipped (already exist)"
                ))
                
                # Fix PostgreSQL sequences after creating objects with explicit PKs
                # This prevents primary key conflicts when creating new objects in admin
                # Always fix sequence to ensure it's in sync
                self._fix_sequence_for_model(Model)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to load {fx_name}: {e}"))

        self.stdout.write(self.style.SUCCESS("Base fixtures loaded successfully!"))
    
    def _fix_sequence_for_model(self, model):
        """Reset PostgreSQL sequence to the maximum ID in the table"""
        table_name = model._meta.db_table
        sequence_name = f"{table_name}_id_seq"
        
        try:
            with connection.cursor() as cursor:
                # Get the maximum ID from the table
                cursor.execute(f"SELECT COALESCE(MAX(id), 0) FROM {table_name}")
                max_id = cursor.fetchone()[0]
                
                # Reset the sequence to max_id + 1
                # Use false to prevent the next value from being the one we set
                cursor.execute(f"SELECT setval('{sequence_name}', {max_id + 1}, false)")
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Fixed sequence {sequence_name} for {table_name} (set to {max_id + 1})"
                    )
                )
        except Exception as e:
            # If sequence doesn't exist or there's an error, log it but don't fail
            self.stdout.write(
                self.style.WARNING(
                    f"Could not fix sequence {sequence_name} for {table_name}: {e}"
                )
            )
