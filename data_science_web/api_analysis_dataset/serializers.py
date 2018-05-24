from django.utils.timezone import now
from rest_framework import serializers
from analysis_dataset.models import Analysis, ZipArchive
from .exceptions import CustomHTTPException


class SerializerAnalysisDetail(serializers.ModelSerializer):
    date_modification = serializers.ReadOnlyField()

    def is_valid(self, raise_exception=False):
        for analysis_option in self.initial_data.keys():
            if analysis_option not in self.Meta.fields:
                raise CustomHTTPException
            return super().is_valid(raise_exception)
        else:
            raise CustomHTTPException

    def update(self, instance, validated_data):
        validated_data["date_modification"] = now()
        return super(SerializerAnalysisDetail, self).update(instance, validated_data)

    class Meta:
        lookup_field = "name"
        model = Analysis
        fields = [
            "date_modification",
            "step_group",
            "signal_speed",
            "signal_direction",
            "start_sector_direction",
            "start_sector_speed",
            "end_sector_direction",
            "end_sector_speed"
        ]


class SerializerAnalysis(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    date_create = serializers.ReadOnlyField()
    date_modification = serializers.ReadOnlyField()
    user = serializers.ReadOnlyField(source="user.username")

    def create(self, validated_data):
        validated_data["date_create"] = now()
        validated_data["date_modification"] = now()
        validated_data["user"] = self.context['request'].user
        return super().create(validated_data)

    class Meta:
        lookup_field = "name"
        model = Analysis
        fields = '__all__'


class DownloadZipSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZipArchive
        lookup_field = "name"
        fields = ["zip_file"]


class DownloadAllZipSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZipArchive
        fields = ["zip_file"]
        lookup_field = "name"
