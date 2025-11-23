from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Load BASE fixtures (required types and initial data)"

    def handle(self, *args, **kwargs):
        fixtures = [
            "product_types",
            "prize_types",
            "raffle_types",
        ]

        self.stdout.write(self.style.WARNING("Loading BASE fixtures..."))

        for fx in fixtures:
            try:
                call_command("loaddata", fx)
                self.stdout.write(self.style.SUCCESS(f"Loaded {fx}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to load {fx}: {e}"))

        self.stdout.write(self.style.SUCCESS("Base fixtures loaded successfully!"))
