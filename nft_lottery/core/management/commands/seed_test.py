from django.core.management.base import BaseCommand
from django.db import connection
from django.core.files.base import ContentFile
import json
import os
from django.conf import settings
from django.utils import timezone


class Command(BaseCommand):
    help = "Load TEST fixtures (demo users, demo raffles, demo prizes) - uses get_or_create to avoid overwriting"

    def handle(self, *args, **kwargs):
        fixtures = [
            ("test_products", "products"),
            ("test_prizes", "products"),
            ("test_raffles", "lottery"),
            ("test_users", "users"),
        ]

        self.stdout.write(self.style.WARNING("Loading TEST fixtures (safe mode - won't overwrite existing data)..."))

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
                    if fx_name == "test_products":
                        from products.models import Product as Model
                        from products.models import ProductType
                    elif fx_name == "test_prizes":
                        from products.models import Prize as Model
                        from products.models import PrizeType
                elif app_name == "lottery":
                    from lottery.models import Raffle as Model
                    from lottery.models import RaffleType
                    from products.models import Prize
                elif app_name == "users":
                    from users.models import User as Model
                
                created_count = 0
                skipped_count = 0
                for item in data:
                    fields = item.get("fields", {}).copy()
                    pk = item.get("pk")
                    
                    # Handle foreign keys
                    if app_name == "products" and fx_name == "test_products":
                        if "type" in fields:
                            try:
                                fields["type"] = ProductType.objects.get(pk=fields["type"])
                            except ProductType.DoesNotExist:
                                self.stdout.write(self.style.WARNING(f"Skipping {fx_name} pk={pk}: ProductType {fields['type']} not found"))
                                skipped_count += 1
                                continue
                    elif app_name == "products" and fx_name == "test_prizes":
                        if "type" in fields:
                            try:
                                fields["type"] = PrizeType.objects.get(pk=fields["type"])
                            except PrizeType.DoesNotExist:
                                self.stdout.write(self.style.WARNING(f"Skipping {fx_name} pk={pk}: PrizeType {fields['type']} not found"))
                                skipped_count += 1
                                continue
                    elif app_name == "lottery":
                        if "type" in fields:
                            try:
                                fields["type"] = RaffleType.objects.get(pk=fields["type"])
                            except RaffleType.DoesNotExist:
                                self.stdout.write(self.style.WARNING(f"Skipping {fx_name} pk={pk}: RaffleType {fields['type']} not found"))
                                skipped_count += 1
                                continue
                        if "prize" in fields:
                            try:
                                fields["prize"] = Prize.objects.get(pk=fields["prize"])
                            except Prize.DoesNotExist:
                                self.stdout.write(self.style.WARNING(f"Skipping {fx_name} pk={pk}: Prize {fields['prize']} not found"))
                                skipped_count += 1
                                continue
                    
                    # Handle image file loading
                    if "image" in fields and fields["image"]:
                        image_path = fields["image"]
                        # If it's a relative path (starts with 'images/' or just a filename), resolve it
                        if not image_path.startswith("http") and not os.path.isabs(image_path):
                            # Relative path - resolve it relative to the fixture directory
                            fixture_dir = os.path.dirname(fixture_path)
                            full_image_path = os.path.join(fixture_dir, image_path)
                            if os.path.exists(full_image_path):
                                # Read the file content into memory and create ContentFile
                                with open(full_image_path, 'rb') as img_file:
                                    file_content = img_file.read()
                                fields["image"] = ContentFile(file_content, name=os.path.basename(image_path))
                            else:
                                self.stdout.write(self.style.WARNING(f"Image file not found: {full_image_path}, skipping image for {fx_name} pk={pk}"))
                                fields.pop("image", None)
                        # If it's a URL, skip it (ImageField doesn't accept URLs directly)
                        elif image_path.startswith("http"):
                            self.stdout.write(self.style.WARNING(f"Skipping URL image for {fx_name} pk={pk}: {image_path} (use local file path instead)"))
                            fields.pop("image", None)
                    
                    # Check if object exists (by pk, or by unique fields for users)
                    obj = None
                    if app_name == "users":
                        # For users, check by username or telegram_id first
                        if "username" in fields:
                            try:
                                obj = Model.objects.get(username=fields["username"])
                            except Model.DoesNotExist:
                                pass
                        if not obj and "telegram_id" in fields and fields["telegram_id"]:
                            try:
                                obj = Model.objects.get(telegram_id=fields["telegram_id"])
                            except Model.DoesNotExist:
                                pass
                    
                    # If not found by unique fields, try by pk
                    if not obj:
                        try:
                            obj = Model.objects.get(pk=pk)
                        except Model.DoesNotExist:
                            pass
                    
                    if obj:
                        # Object exists, skip to avoid overwriting
                        skipped_count += 1
                        continue
                    
                    # Create new object
                    # Remove fields that shouldn't be set directly
                    fields_to_remove = ["created_at"]  # auto_now_add fields
                    for field in fields_to_remove:
                        fields.pop(field, None)
                    
                    # Handle password for users
                    if app_name == "users" and "password" in fields:
                        password = fields.pop("password")
                        # Check if password is already hashed (starts with pbkdf2_)
                        if password.startswith("pbkdf2_"):
                            # Password is already hashed, set it directly
                            obj = Model.objects.create(pk=pk, **fields)
                            obj.password = password
                            obj.save()
                        else:
                            # Plain text password, hash it
                            obj = Model.objects.create(pk=pk, **fields)
                            obj.set_password(password)
                            obj.save()
                    else:
                        obj = Model.objects.create(pk=pk, **fields)
                    created_count += 1
                
                self.stdout.write(self.style.SUCCESS(
                    f"Processed {fx_name}: {created_count} created, {skipped_count} skipped (already exist)"
                ))
                
                # Fix PostgreSQL sequences after creating users with explicit PKs
                if app_name == "users" and fx_name == "test_users":
                    self._fix_sequence_for_model(Model)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to load {fx_name}: {e}"))
                import traceback
                self.stdout.write(self.style.ERROR(traceback.format_exc()))

        self.stdout.write(self.style.SUCCESS("Test fixtures loaded successfully!"))
    
    def _fix_sequence_for_model(self, model):
        """Reset PostgreSQL sequence to the maximum ID in the table"""
        table_name = model._meta.db_table
        sequence_name = f"{table_name}_id_seq"
        
        with connection.cursor() as cursor:
            # Get the maximum ID from the table
            cursor.execute(f"SELECT COALESCE(MAX(id), 0) FROM {table_name}")
            max_id = cursor.fetchone()[0]
            
            # Reset the sequence to max_id + 1
            cursor.execute(f"SELECT setval('{sequence_name}', {max_id + 1}, false)")
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Fixed sequence {sequence_name} for {table_name} (set to {max_id + 1})"
                )
            )
