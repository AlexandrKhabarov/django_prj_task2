from .serializers import SerializerAnalysis, SerializerAnalysisDetail, DownloadZipSerializer, DownloadAllZipSerializer
from rest_framework import generics
from django.db.models import QuerySet
from analysis_dataset.models import Analysis, ResultAnalysis, ZipArchive


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

from itertools import chain

class AnalysisDownload(generics.ListAPIView):
    queryset = ZipArchive.objects.all()
    serializer_class = DownloadAllZipSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        result_queryset = ZipArchive.objects.none()
        result_list = []
        analysis = Analysis.objects.filter(user=self.request.user)
        for one_analysis in analysis:
            result_analysis = ResultAnalysis.objects.get(analysis=one_analysis)
            result_list.append(queryset.filter(analysis=result_analysis)[0])
        return list(chain(result_queryset, result_list))


class AnalysisDownloadDetail(generics.RetrieveAPIView):
    queryset = ZipArchive.objects.all()
    lookup_field = "name"
    serializer_class = DownloadZipSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        analysis = Analysis.objects.filter(user=self.request.user)
        result_analysis = ResultAnalysis.objects.filter(analysis=analysis[0])
        return queryset.filter(analysis=result_analysis[0])[0]

