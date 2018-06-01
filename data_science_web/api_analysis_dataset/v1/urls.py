from django.urls import path, include

urlpatterns = [  # todo
    path("auth/", include("api_analysis_dataset.v1.auth.urls"), name="api_v1_auth"),
    path("analysis/", include("api_analysis_dataset.v1.analysis.urls"), name="api_v1_analysis")
]
