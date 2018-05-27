from django import forms
from .models import Analysis


class EditForm(forms.ModelForm):
    signal_speed = forms.IntegerField(label="Signal Speed", max_value=4, min_value=1, widget=forms.NumberInput(attrs={
        "min": 1,
        "max": 4,
        "type": "number",
        "class": "form-control"
    }))
    signal_direction = forms.IntegerField(label="Signal Direction", max_value=4, min_value=1, widget=forms.NumberInput(attrs={
        "min": 1,
        "max": 4,
        "type": "number",
        "class": "form-control"
    }))
    step_group = forms.IntegerField(label="Step Group", widget=forms.NumberInput(attrs={
        "type": "number",
        "class": "form-control"
    }))
    start_sector_direction = forms.IntegerField(label="Start Sector Direction", min_value=0, max_value=360, widget=forms.NumberInput(attrs={
        "min": 0,
        "max": 360,
        "type": "number",
        "class": "col form-group"
    }))
    end_sector_direction = forms.IntegerField(label="End Sector Direction", min_value=0, max_value=360, widget=forms.NumberInput(attrs={
        "min": 0,
        "max": 360,
        "type": "number",
        "class": "col form-group"
    }))
    start_sector_speed = forms.IntegerField(label="End Sector Direction", min_value=0, widget=forms.NumberInput(attrs={
        "type": "number",
        "class": "col form-group"
    }))
    end_sector_speed = forms.IntegerField(label="End Sector Direction", widget=forms.NumberInput(attrs={
        "type": "number",
        "class": "col form-group"
    }))

    class Meta:
        model = Analysis
        exclude = ["date_create", "date_modification", "user", "data_set", "name", "result_analysis"]


class CreateAnalysisForm(EditForm):
    name = forms.CharField(label="Name", max_length=30, widget=forms.TextInput(attrs={
        "class": "form-control"
    }))

    data_set = forms.FileField(label="Dataset", widget=forms.ClearableFileInput(attrs={
        "class": "form-control"
    }))

    class Meta:
        model = Analysis
        exclude = ["date_create", "date_modification", "user"]


class SearchForm(forms.Form):
    search_field = forms.CharField(max_length=30, required=False)
