from rest_framework import serializers
from .exceptions import CannotCreateAnalysis, CannotCreateArchive
from analysis_dataset.models import Analysis, ZipArchive
from analysis_dataset.exceptions import UnrecognizedFields




class SerializerAnalysisDetail(serializers.ModelSerializer):
    date_modification = serializers.ReadOnlyField()

    def is_valid(self, raise_exception=False):
        if not len(self.initial_data):
            raise UnrecognizedFields(detail="Non field")
        for analysis_option in self.initial_data.keys():
            if analysis_option not in self.Meta.fields:
                raise UnrecognizedFields(detail=f"Unrecognized field '{analysis_option}'")
        return super().is_valid(raise_exception)

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        try:
            instance.delete_archive()
            instance.create_archive()
        except Exception:
            raise CannotCreateArchive(detail="Cannot create archive")
        return instance

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
        validated_data["user"] = self.context['request'].user
        try:
            instance = super().create(validated_data)
        except Exception:
            raise CannotCreateAnalysis(detail="Cannot create analysis")
        try:
            instance.create_archive()
        except Exception:
            raise CannotCreateArchive(detail="Cannot create archive")
        return instance

    class Meta:
        lookup_field = "name"
        model = Analysis
        exclude = ["result_analysis"]


class DownloadZipSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZipArchive
        lookup_field = "name"
        fields = ["zip_file"]
