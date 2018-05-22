from .serializers import SerializerAnalysis, SerializerAnalysisDetail
from rest_framework import generics
from analysis_dataset.models import Analysis


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


class AnalysisDownload(generics.ListAPIView):
    queryset = Analysis.objects.all()



class AnalysisDownloadDetail(generics.ListAPIView):
    pass
