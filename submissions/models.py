from django.db import models
from django.contrib.auth.models import User

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score_ideal = models.FloatField(default=1000)
    score_disturbances = models.FloatField(default=1000)
    score_noise = models.FloatField(default=1000)
    submission_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.score_ideal}"
