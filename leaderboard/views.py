from rest_framework.views import APIView
from rest_framework.response import Response
from .models import LeaderboardEntry
from .serializers import LeaderboardSerializer
import requests

class ContestLeaderboard(APIView):
    def get(self, request, contest_id):
        url = f"https://codeforces.com/api/contest.standings?contestId={contest_id}&from=1&count=10"
        
        try:
            response = requests.get(url, timeout=5)  # Fetch from Codeforces
            if response.status_code == 200:
                standings = response.json().get("result", {}).get("rows", [])

                leaderboard_data = []
                for entry in standings:
                    leaderboard_data.append({
                        "rank": entry["rank"],
                        "handle": entry["party"]["members"][0]["handle"],
                        "score": entry["points"],
                        "penalty": entry["penalty"]
                    })

                return Response(leaderboard_data)  # Return formatted leaderboard

            else:
                return Response({"error": "Failed to fetch leaderboard from Codeforces"}, status=500)

        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=500)
