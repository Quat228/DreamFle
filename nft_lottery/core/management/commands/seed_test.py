from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Load TEST fixtures (demo users, demo raffles, demo prizes)"

    def handle(self, *args, **kwargs):
        fixtures = [
            "token_pack_products",
            "test_prizes",
            "test_raffles",
            "test_users",
        ]

        self.stdout.write(self.style.WARNING("Loading TEST fixtures..."))

        for fx in fixtures:
            try:
                call_command("loaddata", fx)
                self.stdout.write(self.style.SUCCESS(f"Loaded {fx}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to load {fx}: {e}"))

        self.stdout.write(self.style.SUCCESS("Test fixtures loaded successfully!"))
