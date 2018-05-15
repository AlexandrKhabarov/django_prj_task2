from django.contrib import admin
from .models import Analysis, ResultAnalysis, ZipArchive

# Register your models here.

admin.site.register(Analysis)
admin.site.register(ResultAnalysis)
admin.site.register(ZipArchive)
