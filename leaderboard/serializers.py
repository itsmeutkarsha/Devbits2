from rest_framework import serializers
from .models import LeaderboardEntry
from users.serializers import UserSerializer  # Import UserSerializer for user details

class LeaderboardSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Include user details

    class Meta:
        model = LeaderboardEntry
        fields = ['user', 'score', 'penalty']
