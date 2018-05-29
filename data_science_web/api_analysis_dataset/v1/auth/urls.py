from rest_framework.authtoken import views as token_view
from django.urls import path

urlpatterns = [
    path('api-token-auth/', token_view.obtain_auth_token),
]
