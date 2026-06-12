from exams.models import Result
from django.db.models import Avg

def class_average(exam):
    return Result.objects.filter(
        exam=exam
    ).aggregate(Avg('marks'))