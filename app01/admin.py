from django.contrib import admin

from . import models

# Register your models here.

admin.site.register(models.Answer)
admin.site.register(models.Doctor)
admin.site.register(models.Admin)
admin.site.register(models.Question)
admin.site.register(models.Questionnaire)
admin.site.register(models.Option)
admin.site.register(models.Patient)
admin.site.register(models.Hospital)
admin.site.register(models.Part)
admin.site.register(models.Res)
