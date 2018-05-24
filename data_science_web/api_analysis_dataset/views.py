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


class AnalysisDetail(generics.RetrieveUpdateDestroyAPIView):  # todo add calculation and zip construct
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

    def download(self, request, *args, **kwargs):
        obj = self.get_object()
        serializer = self.get_serializer(obj)

        filename = getattr(self, 'filename', self.get_view_name())
        extension = self.get_content_negotiator().select_renderer(
            request, self.renderer_classes
        )[0].format

        return Response(
            data=serializer.data, status=HTTP_200_OK,
            headers={
                'content-disposition': (
                    'attachment; filename="{}.{}"'.format(filename, extension)
                )
            }
        )

    def get(self, request, *args, **kwargs):
        return self.download(request, *args, **kwargs)
