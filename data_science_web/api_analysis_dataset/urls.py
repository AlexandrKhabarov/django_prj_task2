from django.urls import path, include

urlpatterns = [  # todo
    path("v1/", include("api_analysis_dataset.v1.urls"), name="api_v1_auth"),
]
