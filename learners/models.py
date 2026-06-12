from django.db import models
from schools.models import School


class Learner(models.Model):

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="learners"
    )

    assessment_no = models.CharField(
        max_length=50
    )

    upi_number = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    first_name = models.CharField(
        max_length=100
    )

    last_name = models.CharField(
        max_length=100,
        blank=True
    )

    grade = models.CharField(
        max_length=50
    )

    photo = models.ImageField(
        upload_to="learners/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = [
            "grade",
            "first_name",
            "last_name"
        ]
        unique_together = ('school', 'assessment_no')

    def __str__(self):
        return f"{self.assessment_no} - {self.first_name} {self.last_name}"
