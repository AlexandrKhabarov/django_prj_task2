from django.urls import path, include

urlpatterns = [
    path("v1/auth/", include("api_analysis_dataset.v1.auth.urls"), name="api_v1_auth"),
    path("v1/analysis/", include("api_analysis_dataset.v1.analysis.urls"), name="api_v1_analysis")
]
