import os
import traceback
from django.utils.timezone import now
from django.conf import settings
from rest_framework import serializers
from rest_framework.utils import model_meta
from .exceptions import CustomHTTPException
from analysis_dataset.models import Analysis, ZipArchive
from analysis_dataset.analysis_tools import managers
from analysis_dataset.help_functions import get_all_abs_paths, compress_zip


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
        serializers.raise_errors_on_nested_writes('update', self, validated_data)
        info = model_meta.get_field_info(instance)

        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                field = getattr(instance, attr)
                field.set(value)
            else:
                setattr(instance, attr, value)

        try:
            managers.ApplicationManager().go(
                instance,
                settings.MEDIA_ROOT,
            )
        except Exception:
            raise CustomHTTPException

        instance.save()

        archive = ZipArchive.objects.filter(
            name=instance.name,
            analysis=instance
        )
        if archive:
            archive[0].delete()

        file_name = "{}_{}.zip".format(instance.name, instance.date_modification)
        base_name_dir = "zip_files"
        abs_path_dir = os.path.join(settings.MEDIA_ROOT, base_name_dir)
        if not os.path.exists(abs_path_dir):
            os.mkdir(abs_path_dir)
        compress_zip(os.path.join(abs_path_dir, file_name), get_all_abs_paths(instance.result_analysis))
        archive = ZipArchive()
        archive.name = instance.name
        archive.analysis = instance
        archive.zip_file = os.path.join(base_name_dir, file_name)
        archive.save()

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
        validated_data["date_create"] = now()
        validated_data["date_modification"] = now()
        validated_data["result_analysis"] = os.path.join(settings.MEDIA_ROOT, validated_data["name"])
        validated_data["user"] = self.context['request'].user

        serializers.raise_errors_on_nested_writes('create', self, validated_data)

        ModelClass = self.Meta.model

        info = model_meta.get_field_info(ModelClass)
        many_to_many = {}
        for field_name, relation_info in info.relations.items():
            if relation_info.to_many and (field_name in validated_data):
                many_to_many[field_name] = validated_data.pop(field_name)

        try:
            instance = ModelClass.objects.create(**validated_data)
        except TypeError:
            tb = traceback.format_exc()
            msg = (
                    'Got a `TypeError` when calling `%s.objects.create()`. '
                    'This may be because you have a writable field on the '
                    'serializer class that is not a valid argument to '
                    '`%s.objects.create()`. You may need to make the field '
                    'read-only, or override the %s.create() method to handle '
                    'this correctly.\nOriginal exception was:\n %s' %
                    (
                        ModelClass.__name__,
                        ModelClass.__name__,
                        self.__class__.__name__,
                        tb
                    )
            )
            raise TypeError(msg)

        if many_to_many:
            for field_name, value in many_to_many.items():
                field = getattr(instance, field_name)
                field.set(value)
        try:
            managers.ApplicationManager().go(
                instance,
                settings.MEDIA_ROOT,
            )
        except Exception:
            raise CustomHTTPException

        file_name = "{}_{}.zip".format(validated_data["name"], instance.date_modification)
        base_name_dir = "zip_files"
        abs_path_dir = os.path.join(settings.MEDIA_ROOT, base_name_dir)
        if not os.path.exists(abs_path_dir):
            os.mkdir(abs_path_dir)
        compress_zip(os.path.join(abs_path_dir, file_name), get_all_abs_paths(instance.result_analysis))
        archive = ZipArchive()
        archive.name = validated_data["name"]
        archive.analysis = instance
        archive.zip_file = os.path.join(base_name_dir, file_name)
        archive.save()
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
