from django import forms
from .models import Analysis


class EditForm(forms.ModelForm):
    signal_speed = forms.IntegerField(label="Signal Speed", widget=forms.NumberInput(attrs={
        "min": 1,
        "max": 4,
        "type": "number",
        "class": "form-control"
    }))
    signal_direction = forms.IntegerField(label="Signal Direction", widget=forms.NumberInput(attrs={
        "min": 1,
        "max": 4,
        "type": "number",
        "class": "form-control"
    }))
    step_group = forms.IntegerField(label="Step Group", widget=forms.NumberInput(attrs={
        "type": "number",
        "class": "form-control"
    }))
    start_sector_direction = forms.IntegerField(label="Start Sector Direction", widget=forms.NumberInput(attrs={
        "min": 0,
        "max": 360,
        "type": "number",
        "class": "col form-group"
    }))
    end_sector_direction = forms.IntegerField(label="End Sector Direction", widget=forms.NumberInput(attrs={
        "min": 0,
        "max": 360,
        "type": "number",
        "class": "col form-group"
    }))
    start_sector_speed = forms.IntegerField(label="End Sector Direction", widget=forms.NumberInput(attrs={
        "type": "number",
        "class": "col form-group"
    }))
    end_sector_speed = forms.IntegerField(label="End Sector Direction", widget=forms.NumberInput(attrs={
        "type": "number",
        "class": "col form-group"
    }))

    def clean(self):
        cleaned_data = super().clean()
        signal_speed = cleaned_data.get("signal_speed")
        signal_direction = cleaned_data.get("signal_direction")
        start_sector_direction = cleaned_data.get("start_sector_direction")
        end_sector_direction = cleaned_data.get("end_sector_direction")
        if signal_speed > 4 or signal_speed < 1:
            raise forms.ValidationError("Signal Speed must be in [1, 4]")
        if signal_direction > 4 or signal_direction < 1:
            raise forms.ValidationError("Signal Direction must be in [1, 4]")
        if start_sector_direction > 360 or start_sector_direction < 0:
            raise forms.ValidationError("Start Sector of Direction must be in [0, 360]")
        if end_sector_direction > 360 or end_sector_direction < 0:
            raise forms.ValidationError("End Sector Direction must be in [0, 360]")
        return cleaned_data

    class Meta:
        model = Analysis
        exclude = ["date_create", "date_modification", "user", "data_set", "name"]


class ConstantsForm(EditForm):
    name = forms.CharField(label="Name", widget=forms.TextInput(attrs={
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
