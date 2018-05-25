from rest_framework.authtoken import views as token_view
from django.urls import path
from . import views

# todo  /api/v1/auth/api-token-auth
# todo /api/v1/analysis/
urlpatterns = [
    path('analysis/', views.AnalysisList.as_view()),
    path('analysis/<str:name>/', views.AnalysisDetail.as_view()),
    path('analysis/<str:name>/download/', views.AnalysisDownloadDetail.as_view()),
    path('api-token-auth/', token_view.obtain_auth_token),
]
