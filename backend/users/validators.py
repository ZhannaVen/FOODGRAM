import re

from django.core.exceptions import ValidationError


def validate_username(value):
    if value == 'me':
        raise ValidationError(
            ('The username <me> is reserved by the system. '
             'Please use a different name.'),
            params={'value': value},
        )
    if re.search(r'^[\w.@+-]+$', value) is None:
        raise ValidationError(
            (f'Invalid characters in username -> {value}! '
             f'Letters, digits and @/./+/-/_ only'),
            params={'value': value},
        )
