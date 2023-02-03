from django.contrib import admin
from .models import Question,Answer
from import_export.admin import ImportExportModelAdmin
# Register your models here.
# admin.site.register(Question)
admin.site.register(Answer)
@admin.register(Question)
class QuestionAdmin(ImportExportModelAdmin):
    pass