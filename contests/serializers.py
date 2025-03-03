from rest_framework import serializers
from .models import Contest, ContestProblem

class ProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContestProblem
        fields = '__all__'

class ContestProblemSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()  # ✅ Fetch name dynamically
    submission_url = serializers.SerializerMethodField()

    class Meta:
        model = ContestProblem
        fields = ['codeforces_id', 'index', 'name', 'submission_url']

    def get_name(self, obj):
        return obj.fetch_problem_name()  # ✅ Fetch name dynamically

    def get_submission_url(self, obj):
        return obj.get_submission_url()  # ✅ Fetch submission link



class ContestSerializer(serializers.ModelSerializer):
    problems = ProblemSerializer(many=True, read_only=True)

    class Meta:
        model = Contest
        fields = '__all__'
