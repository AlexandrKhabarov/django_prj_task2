from django.urls import path
from .views import UserPage, RegisterPage, SignInPage, LogOut, AnalysisPage, DetailsPage, EditPage, \
    SuccessEditPage, DownloadZip, DeleteAnalysis, CreateAnalysis, CalculateAnalysis
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('register/', RegisterPage.as_view(), name="register"),
    path("sign-in/", SignInPage.as_view(), name="sign-in"),
    path('user/', login_required(UserPage.as_view()), name="user"),
    path("user/logout/", login_required(LogOut.as_view()), name="log-out"),
    path("user/analysis/", login_required(AnalysisPage.as_view()), name="analysis"),
    path("user/analysis/create/", login_required(CreateAnalysis.as_view()), name="create"),
    path("user/analysis/<str:name>/", login_required(DetailsPage.as_view()), name="details"),
    path("user/analysis/<str:name>/calculate/", login_required(CalculateAnalysis.as_view()), name="calculate"),
    path("user/analysis/<str:name>/delete", login_required(DeleteAnalysis.as_view()), name="delete"),
    path("user/analysis/<str:name>/download-zip", login_required(DownloadZip.as_view()), name="download-zip"),
    path("user/analysis/<str:name>/edit/", login_required(EditPage.as_view()), name="edit"),
    path("user/analysis/<str:name>/edit/success/", login_required(SuccessEditPage.as_view()), name="success-edit"),
]
