from django.contrib import admin
from .models import Subject, Exam, Result


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "term", "year"]


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = [
        "learner",
        "subject",
        "exam",
        "marks",
        "grade"
    ]

    list_filter = [
        "subject",
        "exam",
        "grade"
    ]

    search_fields = [
        "learner__first_name",
        "learner__last_name",
        "learner__assessment_no"
    ]