from rest_framework import generics
from rest_framework.exceptions import NotFound
from django.core.exceptions import ObjectDoesNotExist
from analysis_dataset.models import Analysis, ZipArchive
from .serializers import SerializerAnalysis, SerializerAnalysisDetail, DownloadZipSerializer


# Create your views here.

class AnalysisList(generics.ListCreateAPIView):
    queryset = Analysis.objects.all()
    serializer_class = SerializerAnalysis

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)


class AnalysisDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Analysis.objects.all()
    serializer_class = SerializerAnalysisDetail
    lookup_field = "name"

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user=self.request.user)

    def put(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)


class AnalysisDownloadDetail(generics.RetrieveAPIView):
    queryset = ZipArchive.objects.all()
    lookup_field = "name"
    serializer_class = DownloadZipSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        try:
            analysis = Analysis.objects.get(user=self.request.user, name=self.kwargs["name"])
        except ObjectDoesNotExist:
            raise NotFound
        return queryset.filter(analysis=analysis)

