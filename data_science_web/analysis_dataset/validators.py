from django.core.exceptions import ValidationError


def greater_zero(value): # todo MinValue validator is the same
    if value <= 0:
        raise ValidationError("must be greater zero")
