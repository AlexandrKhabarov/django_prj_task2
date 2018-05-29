from django.urls import path
from api_analysis_dataset.v1.analysis import views

urlpatterns = [
    path('', views.AnalysisList.as_view()),
    path('<str:name>/', views.AnalysisDetail.as_view()),
    path('<str:name>/download/', views.AnalysisDownloadDetail.as_view()),
]
