import operator
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


# Create your models here.

class Analysis(models.Model):
    name = models.CharField(max_length=30, unique=True)
    date_create = models.DateField(default=now)
    date_modification = models.DateField(default=now)
    data_set = models.FileField(upload_to="data_sets/")
    signal_speed = models.IntegerField()
    signal_direction = models.IntegerField()
    step_group = models.IntegerField()
    start_sector_direction = models.IntegerField()
    end_sector_direction = models.IntegerField()
    start_sector_speed = models.IntegerField()
    end_sector_speed = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["date_modification"]

    def delete(self, using=None, keep_parents=False):
        self.data_set.delete()
        super(Analysis, self).delete(using, keep_parents)


class ResultAnalysis(models.Model):
    group_data_frame = models.FileField(upload_to="group_data_frame/")
    with_density = models.FileField(upload_to="with_density/")
    dot_graph = models.ImageField(upload_to="dot_graphs/")
    rose_graph = models.ImageField(upload_to="rose_graph/")
    hist_graph = models.ImageField(upload_to="hist_graph/")
    density_graph = models.ImageField(upload_to="density_graph/")

    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE)

    def __str__(self):
        return self.analysis.name

    def delete(self, using=None, keep_parents=False):
        for file_name in self.__dict__.keys():
            try:
                operator.attrgetter(file_name)(self).delete()
            except Exception:
                pass
        super(ResultAnalysis, self).delete(using, keep_parents)


class ZipArchive(models.Model):
    name = models.CharField(max_length=30)
    zip_file = models.FileField(upload_to="zip_files/")
    analysis = models.OneToOneField(ResultAnalysis, on_delete=models.CASCADE)

    class Meta:
        unique_together = (("name", "analysis"),)

    def delete(self, using=None, keep_parents=False):
        self.zip_file.delete()
        super(ZipArchive, self).delete(using, keep_parents)
