import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from energy.models import EnergyUsage
from water.models import WaterUsage
from waste.models import WasteRecord

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with random records for demonstration'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        # 1. Create Users
        admin, created = User.objects.get_or_create(username='admin', defaults={'role': 'ADMIN'})
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS('Created admin: admin/admin123'))
        
        staff, created = User.objects.get_or_create(username='staff', defaults={'role': 'STAFF'})
        if created:
            staff.set_password('staff123')
            staff.save()
            self.stdout.write(self.style.SUCCESS('Created staff: staff/staff123'))

        # 2. Seed Records
        buildings = ['Main Library', 'Science Block', 'Admin Building', 'Sports Complex', 'Engineering Hub', 'Arts Center']
        waste_types = ['DRY', 'WET', 'PLASTIC', 'E_WASTE']
        
        # Energy (Monthly records for the last year)
        start_date = datetime(2023, 1, 1)
        for i in range(12):
            month_date = (start_date + timedelta(days=31 * i)).replace(day=1)
            for building in buildings:
                EnergyUsage.objects.get_or_create(
                    building_name=building,
                    month=month_date,
                    defaults={
                        'units_consumed': random.uniform(500, 2500),
                        'created_by': admin
                    }
                )

        # Water (Daily/Weekly records)
        for _ in range(100):
            days_ago = random.randint(0, 365)
            record_date = datetime.now().date() - timedelta(days=days_ago)
            WaterUsage.objects.create(
                building_name=random.choice(buildings),
                litres_consumed=random.uniform(100, 1000),
                date=record_date,
                created_by=staff
            )

        # Waste (Daily/Weekly records)
        for _ in range(100):
            days_ago = random.randint(0, 365)
            record_date = datetime.now().date() - timedelta(days=days_ago)
            WasteRecord.objects.create(
                waste_type=random.choice(waste_types),
                quantity_kg=random.uniform(5, 50),
                date=record_date,
                created_by=staff
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded demonstration data!'))
