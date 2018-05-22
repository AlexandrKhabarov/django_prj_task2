from django.utils.timezone import now
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from analysis_dataset.models import Analysis
from .exceptions import CustomHTTPException


class SerializerAnalysisDetail(serializers.ModelSerializer):
    date_modification = serializers.ReadOnlyField()
    end_sector_direction = serializers.IntegerField(max_value=360, min_value=0, required=True)
    end_sector_speed = serializers.IntegerField(min_value=0, required=True)
    start_sector_speed = serializers.IntegerField(min_value=0, required=True)
    start_sector_direction = serializers.IntegerField(min_value=0, max_value=360, required=True)
    signal_speed = serializers.IntegerField(min_value=1, max_value=4, required=True)
    signal_direction = serializers.IntegerField(min_value=1, max_value=4, required=True)

    def validate_step_group(self, value):
        if value <= 0:
            raise ValidationError("step_group must be > 0")
        return value

    def is_valid(self, raise_exception=False):
        for analysis_option in self.initial_data.keys():
            if analysis_option not in self.Meta.fields:
                raise CustomHTTPException
        return super().is_valid(raise_exception)

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


class SerializerAnalysis(SerializerAnalysisDetail):
    id = serializers.ReadOnlyField()
    date_create = serializers.ReadOnlyField()
    date_modification = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=30, min_length=3, required=True)
    data_set = serializers.FileField(required=True)
    user = serializers.ReadOnlyField(source="user.username")

    def create(self, validated_data):
        validated_data["date_create"] = now()
        validated_data["date_modification"] = now()
        validated_data["user"] = self.context['request'].user
        return super().create(validated_data)

    def validate_name(self, value):
        if self.Meta.model.objects.filter(name=value, user=self.context["request"].user):
            raise ValidationError("Analysis with same name already exist")
        return value

    class Meta:
        lookup_field = "name"
        model = Analysis
        fields = '__all__'
