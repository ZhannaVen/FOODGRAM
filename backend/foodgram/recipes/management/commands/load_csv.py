from csv import DictReader

from django.conf import settings
from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """Loading data into the database from the corresponding csv
    files is performed by the python manage.py load_csv command.
    """
    def handle(self, *args, **kwargs):
        data_path = settings.BASE_DIR
        try:
            with open(
                f'{data_path}/data/ingredients.csv',
                'r',
                encoding='utf-8'
            ) as csv_data:
                reader = DictReader(csv_data)
                Ingredient.objects.bulk_create(
                    Ingredient(**data) for data in reader)
                csv_data.close()
            self.stdout.write(self.style.SUCCESS('All data is loaded'))
        except Exception as error:
            self.stdout.write(
                self.style.ERROR(
                    f'There is an error in loading data: {error}'))
