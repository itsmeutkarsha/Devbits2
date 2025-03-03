from django.db import models
from users.models import User
from contests.models import Contest

class LeaderboardEntry(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    penalty = models.IntegerField(default=0)  # ICPC-style penalty
