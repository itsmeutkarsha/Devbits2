from django.db import models
from django.conf import settings
from users.models import User
from datetime import timedelta


# class Contest(models.Model):
#     title = models.CharField(max_length =255)
#     description =models.TextField()
#     duration = models.IntegerField()
#     start_time = models.DateTimeField()
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE)
#     participants = models.ManyToManyField(User, related_name='contests')

# class Problem(models.Model):
#     contest= models.ForeignKey(Contest, on_delete=models.CASCADE)
#     codeforces_id =models.CharField(max_length=50)
#     difficulty = models.CharField(max_length=10)



class Contest(models.Model):
    name = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    creator = models.ForeignKey(User, on_delete=models.CASCADE)

    problems = models.ManyToManyField('ContestProblem', related_name='contests', blank=True)  # ✅ Contest Problems
    participants = models.ManyToManyField(User, related_name='contests', blank=True)  # ✅ Individual Participants
    teams = models.ManyToManyField('Team', related_name='contests', blank=True)  # ✅ Teams

    def __str__(self):
        return self.name

    


class ContestProblem(models.Model):
    codeforces_id = models.IntegerField(null=True, blank=True)  # ✅ Codeforces Contest ID
    index = models.CharField(max_length=10, null=True, blank=True)   # ✅ Problem Index
    contest = models.ManyToManyField(Contest, blank=True)  # ✅ Allow multiple contests
    problem_name = models.CharField(max_length=255, null=True, blank=True)  # ✅ Problem Name

    def get_submission_url(self):
        return f"https://codeforces.com/contest/{self.codeforces_id}/problem/{self.index}"

    def __str__(self):
        return f"{self.codeforces_id}{self.index} - {self.problem_name}"

class Team(models.Model):
    name = models.CharField(max_length=255, unique=True)
    members = models.ManyToManyField(User, related_name='teams')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    


class ContestInvitation(models.Model):
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    invited_user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10, choices=[("Pending", "Pending"), ("Accepted", "Accepted")], default="Pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.invited_user.username} - {self.contest.name} ({self.status})"



# class ContestProblem(models.Model):
#     contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
#     codeforces_id = models.IntegerField(null=True, blank=True)  # ✅ Now optional
#     index = models.CharField(max_length=10, null=True, blank=True)

#     def get_submission_url(self):
#         return f"https://codeforces.com/contest/{self.codeforces_id}/problem/{self.index}"  # ✅ Generates submission URL

#     def fetch_problem_name(self):
#         """Fetch problem name dynamically from Codeforces API."""
#         import requests
        
#         url = "https://codeforces.com/api/problemset.problems"
#         response = requests.get(url)

#         if response.status_code == 200:
#             data = response.json()
#             problems = data["result"]["problems"]
#             for problem in problems:
#                 if problem.get("contestId") == self.codeforces_id and problem.get("index") == self.index:
#                     return problem.get("name", "Unknown")  # ✅ Return problem name if found
#         return "Unknown"  # ✅ If not found, return "Unknown"

#     def __str__(self):
#         return f"{self.codeforces_id}{self.index} - {self.fetch_problem_name()}"  # ✅ Show fetched name dynamically


