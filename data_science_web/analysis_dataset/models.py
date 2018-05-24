import operator
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator, MinLengthValidator
from django.contrib.auth.models import User
import os
from django.utils.timezone import now
from .validators import greater_zero


# Create your models here.

class Analysis(models.Model):
    name = models.CharField(max_length=30, unique=True, validators=[MinLengthValidator(3)])
    date_create = models.DateField(default=now)
    date_modification = models.DateField(default=now)
    data_set = models.FileField(upload_to="data_sets/")
    signal_speed = models.IntegerField(validators=[MaxValueValidator(4), MinValueValidator(1)])
    signal_direction = models.IntegerField(validators=[MaxValueValidator(4), MinValueValidator(1)])
    step_group = models.IntegerField(validators=[greater_zero])
    start_sector_direction = models.IntegerField(
        validators=[MaxValueValidator(360), MinValueValidator(1)]
    )
    end_sector_direction = models.IntegerField(
        validators=[MaxValueValidator(360), MinValueValidator(1)]
    )
    start_sector_speed = models.IntegerField(validators=[MinValueValidator(0)])
    end_sector_speed = models.IntegerField(validators=[MinValueValidator(0)])
    result_analysis = models.FilePathField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["date_modification"]

    def delete(self, using=None, keep_parents=False):
        self.data_set.delete()
        self.delete_results_analysis()
        os.rmdir(self.result_analysis)
        super(Analysis, self).delete(using, keep_parents)

    def delete_results_analysis(self):
        for analysis_file in os.listdir(self.result_analysis):
            os.remove(os.path.join(self.result_analysis, analysis_file))


class ZipArchive(models.Model):
    name = models.CharField(max_length=30)
    zip_file = models.FileField(upload_to="zip_files/")
    analysis = models.OneToOneField(Analysis, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("name", "analysis"),)

    def delete(self, using=None, keep_parents=False):
        self.zip_file.delete()
        super(ZipArchive, self).delete(using, keep_parents)
