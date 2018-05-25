from rest_framework import generics
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
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

