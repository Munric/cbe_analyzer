from django.db import models
from learners.models import Learner


class Subject(models.Model):

    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
       
      

    name = models.CharField(
        max_length=100
    )

    def __str__(self):
        return self.name


class Exam(models.Model):

    school = models.ForeignKey(
        'schools.School',
        on_delete=models.CASCADE,
        blank=True
    )

    name = models.CharField(
        max_length=100
    )

    term = models.CharField(
        max_length=20
    )

    year = models.IntegerField()

    def __str__(self):
        return self.name


class Result(models.Model):

    learner = models.ForeignKey(
        Learner,
        on_delete=models.CASCADE
    )

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    marks = models.IntegerField()

    grade = models.CharField(
        max_length=10,
        blank=True,
    )

    def __str__(self):
        return (
            f"{self.learner} - "
            f"{self.subject}"
        )