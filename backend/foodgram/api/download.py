from datetime import datetime
from django.http import HttpResponse


def download_txt(queryset):
    today = datetime.today()
    shopping_list = (
        f'Date: {today:%d-%m-%Y}\n\n'
    )
    shopping_list += '\n'.join([
        f'- {ingredient["ingredient__name"]}: '
        f'{ingredient["amount"]}'
        f'({ingredient["ingredient__measurement_unit"]})'
        for ingredient in queryset
    ])
    shopping_list += f'\n\nFoodgram - your product assistant ({today:%Y})'

    filename = f'{today:%d-%m-%Y}_shopping_list.txt'
    response = HttpResponse(shopping_list, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response
