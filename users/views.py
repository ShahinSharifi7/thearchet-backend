from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics
from django.contrib.auth import get_user_model, authenticate
from .serializers import UserSerializer, RegisterSerializer, ProfileSerializer, ProfileCompletionSerializer
from .utils import get_tokens_for_user

User = get_user_model()


class GetAllView(APIView):
    def get(self, request):
        all_users = User.objects.all()
        serializer = ProfileSerializer(all_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user:
            tokens = get_tokens_for_user(user)
            return Response(tokens, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)  # Generate tokens for the new user
            return Response({
                "message": "User registered successfully",
                "user": serializer.data,
                "tokens": tokens
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserProfileByUsernameAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        serializer = ProfileSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateProfileView(generics.GenericAPIView):
    serializer_class = ProfileCompletionSerializer  # Used for updating the profile
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # Allows handling profile_picture uploads

    def post(self, request, *args, **kwargs):
        user = request.user

        # Use ProfileCompletionSerializer to update profile
        update_serializer = self.get_serializer(user, data=request.data, partial=True)

        if update_serializer.is_valid():
            update_serializer.save()

            # Use ProfileSerializer to return the updated profile
            response_serializer = ProfileSerializer(user, context={"request": request})
            return Response(response_serializer.data, status=status.HTTP_200_OK)

        return Response(update_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileCompletionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = ProfileCompletionSerializer(request.user)
        return Response({"is_profile_complete": serializer.data["is_profile_complete"]})


class HasMatchesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        has_matches = request.user.matched_users.exists()
        return Response({"has_matches": has_matches})


class GetMatchesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        matches = User.objects.filter(id__in=request.user.matched_users.all())
        if matches.exists():
            serializer = ProfileSerializer(matches, many=True)
            return Response(serializer.data, status.HTTP_200_OK)
        else:
            return Response([], status.HTTP_200_OK)


class UpgradeToPremiumAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.is_premium = True
        user.save()
        return Response({"message": "User upgraded to premium successfully"}, status=status.HTTP_200_OK)


class RemovePremiumAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        user.is_premium = False
        user.save()
        return Response({"message": "Premium removed successfully"}, status=status.HTTP_200_OK)

