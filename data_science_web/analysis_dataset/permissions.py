from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType

try:
    Permission.objects.create(
        codename="can_redirect_to_the_success_page",
        name="Can Redirect Success",
        content_type=ContentType.objects.get_for_model(User)
    )
except Exception:
    pass
