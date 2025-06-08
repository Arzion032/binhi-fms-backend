from django.core.management.base import BaseCommand
from users.models import CustomUser, Association

class Command(BaseCommand):
    help = 'Creates an association and assigns it to the vendor'

    def handle(self, *args, **kwargs):
        # Create the association
        association, created = Association.objects.get_or_create(
            name='Macamot Farmers Association',
            defaults={
                'description': 'Macamot Farmers Association'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Successfully created association'))
        else:
            self.stdout.write(self.style.SUCCESS('Association already exists'))

        # Get the vendor
        try:
            vendor = CustomUser.objects.get(id='d3004d02-d2f7-4980-968b-860691790486')
            vendor.association = association
            vendor.save()
            self.stdout.write(self.style.SUCCESS('Successfully assigned association to vendor'))
        except CustomUser.DoesNotExist:
            self.stdout.write(self.style.ERROR('Vendor not found')) 