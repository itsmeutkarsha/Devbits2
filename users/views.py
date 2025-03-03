from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from .models import User
from .serializers import UserSerializer
from django.contrib.auth import authenticate, get_user_model
import requests
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
import re 
class JWTLoginView(TokenObtainPairView):
    pass


User = get_user_model()

class RegisterUser(APIView):
    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")
        codeforces_handle = request.data.get("codeforces_handle")  # Get handle

        print(f"Received data: username={username}, email={email}, password={password}, codeforces_handle={codeforces_handle}")

        # ✅ 1. Check if all fields are provided
        if not username or not password or not codeforces_handle or not email:
            return Response({"error": "Username, password, email, and Codeforces handle are required"}, status=400)

        # ✅ 2. Validate Email Format (Must be Gmail)
        email_pattern = r"^[a-zA-Z0-9._%+-]+@gmail\.com$"
        if not re.match(email_pattern, email):
            return Response({"error": "Invalid email format. Only Gmail accounts are allowed"}, status=400)

        # ✅ 3. Check if email is already registered
        if User.objects.filter(email=email).exists():
            return Response({"error": "This email is already registered"}, status=400)

        # ✅ 4. Check if Codeforces handle already exists
        if User.objects.filter(codeforces_handle=codeforces_handle).exists():
            return Response({"error": "This Codeforces handle is already registered"}, status=400)

        # ✅ 5. Validate Codeforces Handle
        cf_url = f"https://codeforces.com/api/user.info?handles={codeforces_handle}"
        try:
            cf_response = requests.get(cf_url, timeout=5)
            if cf_response.status_code != 200:
                return Response({"error": "Invalid Codeforces handle"}, status=400)

            # ✅ Ensure the response contains valid user data
            cf_data = cf_response.json()
            if "result" not in cf_data or not cf_data["result"]:
                return Response({"error": "Invalid Codeforces handle"}, status=400)

        except requests.exceptions.RequestException as e:
            return Response({"error": f"Failed to verify Codeforces handle: {str(e)}"}, status=500)

        # ✅ 6. Create the User
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                codeforces_handle=codeforces_handle  # Save handle
            )
            print(f"User created: {user}")

            return Response({"message": "User registered successfully!", "user": UserSerializer(user).data})
        except Exception as e:
            print(f"Error creating user: {e}")
            return Response({"error": str(e)}, status=500)
    


class LoginUser(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)  # ✅ Generate or get token
            return Response({
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "codeforces_handle": getattr(user, "codeforces_handle", None)
                },
                "token": token.key  # ✅ Now token is included in the response
            })
        return Response({"error": "Invalid credentials"}, status=400)




class CodeforcesUserInfo(APIView):
    def get(self, request):
        handle = request.GET.get("handle")  # Get handle from query parameters
        if not handle:
            return Response({"error": "Handle is required"}, status=400)

        url = f"https://codeforces.com/api/user.info?handles={handle}"
        
        try:
            response = requests.get(url, timeout=5)  # Timeout added
            if response.status_code == 200:
                data = response.json().get("result", [])
                if data:
                    return Response(data[0])  # Return user details
                else:
                    return Response({"error": "User not found"}, status=404)
            else:
                return Response({"error": f"Codeforces API error {response.status_code}"}, status=500)

        except requests.exceptions.RequestException as e:
            return Response({"error": f"Request failed: {str(e)}"}, status=500)
        


class CodeforcesSubmissions(APIView):
    def get(self, request):
        handle = request.GET.get("handle")  # Get user's Codeforces handle
        if not handle:
            return Response({"error": "Handle is required"}, status=400)

        url = f"https://codeforces.com/api/user.status?handle={handle}&from=1&count=20"
        response = requests.get(url)

        if response.status_code == 200:
            submissions = response.json()["result"]
            submission_data = []

            for sub in submissions:
                submission_data.append({
                    "problem": sub["problem"]["name"],
                    "verdict": sub["verdict"],  # "OK" means accepted
                    "submitted_at": sub["creationTimeSeconds"]
                })

            return Response(submission_data)
        else:
            return Response({"error": "Failed to fetch submissions"}, status=500)



class CodeforcesUserProfile(APIView):
    permission_classes = [IsAuthenticated]  # ✅ Require authentication

    def get(self, request):
        # ✅ Fetch Codeforces handle from the logged-in user
        handle = getattr(request.user, "codeforces_handle", None)

        if not handle:
            return Response({"error": "No Codeforces handle linked to your account"}, status=400)

        # API URLs for user info and rating changes
        user_info_url = f"https://codeforces.com/api/user.info?handles={handle}"
        rating_url = f"https://codeforces.com/api/user.rating?handle={handle}"

        try:
            # Fetch user profile data
            user_info_response = requests.get(user_info_url, timeout=5)
            rating_response = requests.get(rating_url, timeout=5)

            if user_info_response.status_code != 200:
                return Response({"error": "Failed to fetch user info"}, status=500)

            user_data = user_info_response.json().get("result", [])[0]

            # Fetch rating history
            rating_data = []
            if rating_response.status_code == 200:
                rating_history = rating_response.json().get("result", [])
                for entry in rating_history:
                    rating_data.append({
                        "contest_id": entry["contestId"],
                        "contest_name": entry["contestName"],
                        "rank": entry["rank"],
                        "old_rating": entry["oldRating"],
                        "new_rating": entry["newRating"]
                    })

            # Prepare the final response
            profile_data = {
                "handle": user_data["handle"],
                "rating": user_data.get("rating", "N/A"),
                "max_rating": user_data.get("maxRating", "N/A"),
                "rank": user_data.get("rank", "N/A"),
                "max_rank": user_data.get("maxRank", "N/A"),
                "friend_of_count": user_data.get("friendOfCount", 0),
                "contest_history": rating_data  # List of past contests & performance
            }

            return Response(profile_data)

        except requests.exceptions.RequestException as e:
            return Response({"error": str(e)}, status=500)


User = get_user_model()

class UserListView(APIView):
    permission_classes = [IsAuthenticated]  # ✅ Only logged-in users can see user list

    def get(self, request):
        users = User.objects.all()  # ✅ Fetch all users
        user_data = [{"id": user.id, "username": user.username, "codeforces_handle": user.codeforces_handle} for user in users]
        
        return Response({"users": user_data})