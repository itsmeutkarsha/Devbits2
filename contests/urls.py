from django.urls import path
from .views import AddMemberToTeamView, ContestListCreate, CreateTeamView, FetchCodeforcesProblems, InviteToContestView, JoinContestView, ContestTeamsView, DeleteTeamByNameView, ContestParticipantsView, MyContestsView, AcceptInviteView, GetInvitesView, CreateTeamView

urlpatterns = [
    path('', ContestListCreate.as_view()),  # List & Create contests
    path('fetch-problems/', FetchCodeforcesProblems.as_view()),  # Fetch CF problems
    path('<int:contest_id>/join/', JoinContestView.as_view(), name='join-contest'),
    path('<int:contest_id>/invite/', InviteToContestView.as_view(), name='invite-contest'),
    path('teams/create/', CreateTeamView.as_view(), name='create-team'),
    path('teams/<int:team_id>/add_member/', AddMemberToTeamView.as_view(), name='add-member-to-team'),
    path('teams/', ContestTeamsView.as_view(), name="contest-teams"),
    path("teams/<str:team_name>/", DeleteTeamByNameView.as_view(), name="delete-team-by-name"),
    path('<int:contest_id>/participants/', ContestParticipantsView.as_view(), name='contest-participants'),
    path('my-contests/', MyContestsView.as_view(), name='my-contests'),
    path('<int:contest_id>/invite/', InviteToContestView.as_view(), name='invite-contest'),  # ✅ Send invite
    path('<int:contest_id>/accept-invite/', AcceptInviteView.as_view(), name='accept-invite'),  # ✅ Accept invite
    path('<int:contest_id>/invites/', GetInvitesView.as_view(), name='get-invites'),  # ✅ See accepted & pending invites
    
]
