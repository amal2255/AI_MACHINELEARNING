from django.db import models

class JobDescription(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title
    

from django.db import models
from django.utils import timezone

class CandidateInterview(models.Model):
    name = models.CharField(max_length=100)
    score = models.FloatField()
    feedback = models.TextField()

    

    # Add any other fields you need