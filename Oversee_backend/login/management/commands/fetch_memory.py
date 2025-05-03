from django.core.management.base import BaseCommand
from login.services.network_client import fetch_and_store_memory_stats

class Command(BaseCommand):
    help = 'Fetches memory stats from network devices'

    def handle(self, *args, **options):
        if fetch_and_store_memory_stats():
            self.stdout.write(self.style.SUCCESS('Successfully fetched memory stats'))
        else:
            self.stdout.write(self.style.ERROR('Failed to fetch data'))