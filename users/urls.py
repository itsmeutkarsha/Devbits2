from django.urls import path
from .views import RegisterUser, LoginUser, CodeforcesUserInfo, CodeforcesSubmissions, CodeforcesUserProfile, UserListView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns=[
    path('register/',RegisterUser.as_view(), name='register'),
    path('login/',LoginUser.as_view(),name='Login'),
    path('codeforces/user/',CodeforcesUserInfo.as_view(),name='codeforces-user'),
    path('codeforces/submissions/',CodeforcesSubmissions.as_view(),name='codeforces-submissions'),
    path('codeforces/profile/',CodeforcesUserProfile.as_view(),name='codeforces-profile'),
    path('jwt/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("list/", UserListView.as_view(), name="list-users"),
]