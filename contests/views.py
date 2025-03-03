from django.core.mail import send_mail
from django.conf import settings

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from users.models import User
from .models import Contest, ContestProblem, Team, ContestInvitation
from .serializers import ContestSerializer, ContestProblemSerializer
import requests

# class ContestListCreate(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         contests = Contest.objects.all()
#         data = []
#         for contest in contests:
#             problems = ContestProblem.objects.filter(contest=contest)
#             problem_serializer = ContestProblemSerializer(problems, many=True)

#             contest_data = {
#                 "name": contest.name,
#                 "start_time": contest.start_time,
#                 "end_time": contest.end_time,
#                 "is_private": contest.is_private,
#                 "problems": problem_serializer.data,  # ✅ Include problems with submission links
#             }
#             data.append(contest_data)

#         return Response(data)

    
class ContestListCreate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        contest = Contest.objects.create(
            name=request.data['name'],
            start_time=request.data['start_time'],
            end_time=request.data['end_time'],
            creator=request.user
        )

        # ✅ Allow users to select multiple problems
        problem_ids = request.data.get('problems', [])  # Expecting a list of problem IDs
        for problem_id in problem_ids:
            problem = ContestProblem.objects.get(id=problem_id)
            contest.problems.add(problem)  # ✅ Add each problem to the contest

        return Response(ContestSerializer(contest).data)



class FetchCodeforcesProblems(APIView):
    def get(self, request):
        url = "https://codeforces.com/api/problemset.problems"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            problems = data["result"]["problems"]

            # Get filters from request
            tag_filter = request.GET.get("tag", "").lower()  
            rating_filter = request.GET.get("rating")

            formatted_problems = []

            for problem in problems:
                problem_tags = [tag.lower() for tag in problem.get("tags", [])]  
                problem_rating = problem.get("rating", "Not rated")  
                contest_id = problem.get("contestId")
                index = problem.get("index")
                name = problem.get("name", "Unknown")  

                # Skip problems without a valid contest ID and index
                if not contest_id or not index:
                    continue

                # ✅ Filtering by tag (case insensitive)
                if tag_filter and tag_filter not in problem_tags:
                    continue  

                # ✅ Filtering by rating
                if rating_filter and str(problem_rating) != rating_filter:
                    continue

                problem_url = f"https://codeforces.com/contest/{contest_id}/problem/{index}"

                # ✅ Save to database (if needed)
                existing_problem, created = ContestProblem.objects.get_or_create(
                    codeforces_id=contest_id,
                    index=index,
                    defaults={"problem_name": name}  # ✅ Correct field name
                )

                formatted_problems.append({
                    "id": existing_problem.id,
                    "name": existing_problem.problem_name,  
                    "tags": problem_tags if problem_tags else ["No tags available"],  
                    "difficulty": problem_rating,  
                    "url": problem_url  
                })

            return Response(formatted_problems)
        else:
            return Response({"error": "Failed to fetch problems"}, status=500)






class JoinContestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, contest_id):
        contest = get_object_or_404(Contest, id=contest_id)
        
        # Check if joining as a team
        team_id = request.data.get("team_id")
        if team_id:
            team = get_object_or_404(Team, id=team_id)
            if request.user not in team.members.all():
                return Response({"error": "You are not a member of this team."}, status=403)
            contest.teams.add(team)  # ✅ Add team to contest
            return Response({"message": f"Team '{team.name}' joined the contest!"})

        # Otherwise, join as an individual
        contest.participants.add(request.user)
        return Response({"message": f"{request.user.username} joined the contest!"})




# class InviteToContestView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, contest_id):
#         contest = get_object_or_404(Contest, id=contest_id)
#         invited_username = request.data.get("username")
        
#         if not invited_username:
#             return Response({"error": "Username is required"}, status=400)

#         invited_user = get_object_or_404(User, username=invited_username)

#         if invited_user in contest.participants.all():
#             return Response({"error": "User is already in the contest."}, status=400)

#         contest.participants.add(invited_user)

#         # ✅ Send email notification
#         contest_link = f"http://127.0.0.1:8000/api/contests/{contest.id}/"
#         subject = f"You've been added to {contest.name}!"
#         message = f"Hello {invited_user.username},\n\nYou've been added to the contest '{contest.name}'.\nClick here to view: {contest_link}\n\nHappy Coding!"
#         from_email = settings.DEFAULT_FROM_EMAIL
#         recipient_list = [invited_user.email]

#         if invited_user.email:  # ✅ Ensure user has an email
#             send_mail(subject, message, from_email, recipient_list)

#         return Response({"message": f"User '{invited_username}' added and notified!"}, status=200)



class InviteToContestView(APIView):
    permission_classes = [IsAuthenticated]  # ✅ Only logged-in users can invite others

    def post(self, request, contest_id):
        contest = get_object_or_404(Contest, id=contest_id)
        invited_username = request.data.get("username")

        if not invited_username:
            return Response({"error": "Username is required"}, status=400)

        invited_user = get_object_or_404(User, username=invited_username)

        # ✅ Check if the user is already in the contest
        if invited_user in contest.participants.all():
            return Response({"error": "User is already in the contest."}, status=400)

        # ✅ Check if invite is already sent
        invite, created = ContestInvitation.objects.get_or_create(
            contest=contest, invited_user=invited_user
        )

        if not created:
            return Response({"error": "User is already invited."}, status=400)

        # ✅ Send email notification
        contest_link = f"http://127.0.0.1:8000/api/contests/{contest.id}/accept-invite/"
        subject = f"You have been invited to {contest.name}!"
        message = f"Hello {invited_user.username},\n\nYou've been invited to join the contest '{contest.name}'.\nClick here to accept: {contest_link}\n\nHappy Coding!"
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [invited_user.email]

        if invited_user.email:
            send_mail(subject, message, from_email, recipient_list)

        return Response({"message": f"Invitation sent to '{invited_username}'!"}, status=200)




User = get_user_model()  # ✅ Ensure we use the correct User model

class CreateTeamView(APIView):
    permission_classes = [IsAuthenticated]  # ✅ Only logged-in users can create teams

    def post(self, request):
        team_name = request.data.get("name")  # Get team name
        member_usernames = request.data.get("members", [])  # List of usernames

        if not team_name:
            return Response({"error": "Team name is required"}, status=400)

        # ✅ Check if team name is unique
        if Team.objects.filter(name=team_name).exists():
            return Response({"error": "Team name already exists"}, status=400)

        # ✅ Remove the logged-in user from members list (to avoid duplication)
        if request.user.username in member_usernames:
            member_usernames.remove(request.user.username)

        # ✅ Create the team and auto-add the creator
        team = Team.objects.create(name=team_name, created_by=request.user)
        team.members.add(request.user)  # ✅ Add creator to team members

        # ✅ Fetch users by their usernames and add them
        members = User.objects.filter(username__in=member_usernames)
        team.members.add(*members)

        return Response({
            "message": "Team created successfully",
            "team_id": team.id,
            "creator": request.user.username,
            "members": [user.username for user in team.members.all()]
        }, status=201)



class AddMemberToTeamView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, team_id):
        team = get_object_or_404(Team, id=team_id)
        
        if request.user != team.created_by:
            return Response({"error": "Only the team creator can add members."}, status=403)

        user_id = request.data.get("user_id")
        user = get_object_or_404(User, id=user_id)
        team.members.add(user)
        return Response({"message": f"{user.username} added to team '{team.name}'!"})


class ContestTeamsView(APIView):
    permission_classes = [IsAuthenticated]  # ✅ Only logged-in users can access

    def get(self, request):
        user = request.user  # ✅ Get the logged-in user
        teams = Team.objects.filter(members=user)  # ✅ Get teams where the user is a member
        team_data = [{"id": team.id, "name": team.name} for team in teams]  # ✅ Format response

        return Response({"user": user.username, "teams": team_data})
    




class DeleteTeamByNameView(APIView):
    permission_classes = [IsAuthenticated]  # ✅ Only logged-in users can delete teams

    def delete(self, request, team_name):
        user = request.user  # ✅ Get logged-in user

        try:
            team = Team.objects.get(name=team_name)

            # ✅ Check if the user is the creator of the team
            if team.created_by != user:
                return Response({"error": "You are not the creator of this team"}, status=403)

            team.delete()
            return Response({"message": f"Team '{team_name}' deleted successfully"}, status=200)

        except Team.DoesNotExist:
            return Response({"error": "Team not found"}, status=404)
        

class ContestParticipantsView(APIView):
    permission_classes = [IsAuthenticated]  # ✅ Only logged-in users can access

    def get(self, request, contest_id):
        contest = get_object_or_404(Contest, id=contest_id)

        # ✅ Ensure only the contest creator can view participants
        if contest.creator != request.user:
            return Response({"error": "You are not the creator of this contest."}, status=403)

        # ✅ Get all participants
        participants = contest.participants.all()
        participants_data = [{"id": user.id, "username": user.username, "email": user.email} for user in participants]

        return Response({"contest_name": contest.name, "participants": participants_data}, status=200)


class MyContestsView(APIView):
    permission_classes = [IsAuthenticated]  # ✅ Only logged-in users can access

    def get(self, request):
        user = request.user
        contests = Contest.objects.filter(participants=user)  # ✅ Get all contests user is part of

        contest_data = [
            {
                "id": contest.id,
                "name": contest.name,
                "start_time": contest.start_time,
                "end_time": contest.end_time,
                "creator": contest.creator.username
            }
            for contest in contests
        ]

        return Response({"contests": contest_data}, status=200)



class AcceptInviteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, contest_id):
        contest = get_object_or_404(Contest, id=contest_id)
        invite = get_object_or_404(
            ContestInvitation, contest=contest, invited_user=request.user, status="Pending"
        )

        # ✅ Accept invite
        invite.status = "Accepted"
        invite.save()
        contest.participants.add(request.user)  # ✅ Add user to contest

        return Response({"message": "You have joined the contest!"}, status=200)


class GetInvitesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, contest_id):
        contest = get_object_or_404(Contest, id=contest_id, creator=request.user)

        invites = ContestInvitation.objects.filter(contest=contest)
        invite_data = {
            "accepted": [invite.invited_user.username for invite in invites if invite.status == "Accepted"],
            "pending": [invite.invited_user.username for invite in invites if invite.status == "Pending"],
        }

        return Response(invite_data)
