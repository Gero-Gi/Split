from django.core.management.base import BaseCommand, CommandError
from fake_db import FakeDB


class Command(BaseCommand):
    help = 'Fill database with fake data'

    def handle(self, *args, **options):
        FakeDB().populate()
