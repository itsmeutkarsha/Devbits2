from django.urls import path
from .views import ContestLeaderboard

urlpatterns = [
    path('<int:contest_id>/', ContestLeaderboard.as_view()),  # Get leaderboard for a contest
]
