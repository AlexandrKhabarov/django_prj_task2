from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, MinLengthValidator
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import os
import shutil
import logging
from .validators import greater_zero
from .analysis_tools.managers import ApplicationManager
from .help_functions import compress_zip, get_all_abs_paths


# Create your models here.

class Analysis(models.Model):
    name = models.CharField(max_length=30, unique=True, validators=[MinLengthValidator(3)])
    date_create = models.DateField(auto_now_add=True)
    date_modification = models.DateField(auto_now=True)
    data_set = models.FileField(upload_to="data_sets/")
    signal_speed = models.IntegerField(validators=[MaxValueValidator(4), MinValueValidator(1)])
    signal_direction = models.IntegerField(validators=[MaxValueValidator(4), MinValueValidator(1)])
    step_group = models.IntegerField(validators=[greater_zero])
    start_sector_direction = models.IntegerField(
        validators=[MaxValueValidator(360), MinValueValidator(0)]
    )
    end_sector_direction = models.IntegerField(
        validators=[MaxValueValidator(360), MinValueValidator(0)]
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
        shutil.rmtree(self.result_analysis)
        self.data_set.delete(save=False)
        super(Analysis, self).delete(using, keep_parents)

    def delete_results_analysis(self):
        if os.path.exists(self.result_analysis):
            for analysis_file in os.listdir(self.result_analysis):
                os.remove(os.path.join(self.result_analysis, analysis_file))
        logging.warning(f"Path does not exists {self.result_analysis}")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        is_new = self.pk is None
        self.calculate_analysis()
        if is_new:
            self.result_analysis = os.path.join(settings.MEDIA_ROOT, self.name)
        super().save(force_insert, force_update, using, update_fields)

    def calculate_analysis(self):
        try:
            ApplicationManager().go(
                self,
                settings.MEDIA_ROOT,
            )
        except Exception as e:
            shutil.rmtree(os.path.join(settings.MEDIA_ROOT, self.name))
            raise ValidationError(e)

    def create_archive(self):
        file_name = "{}_{}.zip".format(self.name, self.date_modification)
        base_name_dir = "zip_files"
        abs_path_dir = os.path.join(settings.MEDIA_ROOT, base_name_dir)
        if not os.path.exists(abs_path_dir):
            os.mkdir(abs_path_dir)
        compress_zip(os.path.join(abs_path_dir, file_name), get_all_abs_paths(self.result_analysis))
        archive = ZipArchive()
        archive.name = self.name
        archive.zip_file = os.path.join(base_name_dir, file_name)
        archive.analysis = self
        archive.save()
        return archive


class ZipArchive(models.Model):
    name = models.CharField(max_length=30)
    zip_file = models.FileField(upload_to="zip_files/")
    analysis = models.OneToOneField(Analysis, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("name",)

    def delete(self, using=None, keep_parents=False):
        self.zip_file.delete()
        super(ZipArchive, self).delete(using, keep_parents)
