from django.core.management.base import BaseCommand
from classrooms.models import Classroom


class Command(BaseCommand):
    help = 'Generate join keys for classrooms that do not have one'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Regenerate join keys for ALL classrooms',
        )

    def handle(self, *args, **kwargs):
        all_classrooms = kwargs.get('all', False)
        
        if all_classrooms:
            self.stdout.write(self.style.WARNING('Regenerating join keys for ALL classrooms...'))
            classrooms = Classroom.objects.all()
        else:
            self.stdout.write('Generating join keys for classrooms without one...')
            classrooms = Classroom.objects.filter(join_key='')
        
        count = 0
        for classroom in classrooms:
            old_key = classroom.join_key
            classroom.regenerate_join_key()
            count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ {classroom.name}: {classroom.join_key}'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully generated join keys for {count} classroom(s)!')
        )
