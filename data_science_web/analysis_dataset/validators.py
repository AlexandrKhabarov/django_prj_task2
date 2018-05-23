from django.core.exceptions import ValidationError


def greater_zero(value):
    if value <= 0:
        raise ValidationError("must be greater zero")
