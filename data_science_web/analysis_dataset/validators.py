from django.core.exceptions import ValidationError


def greater_zero(value):  # MinValue validator don't the same because he validates value of greater or equal
    if value <= 0:
        raise ValidationError("must be greater zero")
