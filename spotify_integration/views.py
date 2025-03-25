import requests
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .utils import update_or_create_user_token, get_user_token, refresh_spotify_token, get_user_top_ui_genres
from .models import SpotifyToken


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def spotify_status(request):
    connected = SpotifyToken.objects.filter(user=request.user).exists()
    return Response({"connected": connected})


# Redirect user to Spotify's auth page
@api_view(["GET"])
def spotify_login(request):
    scopes = "user-read-email user-read-private user-top-read"
    jwt_token = request.auth
    url = (
        "https://accounts.spotify.com/authorize"
        f"?response_type=code"
        f"&client_id={settings.SPOTIFY_CLIENT_ID}"
        f"&redirect_uri={settings.SPOTIFY_REDIRECT_URI}"
        f"&scope={scopes}"
        f"&state={jwt_token}"
        f"&show_dialog=true"
    )
    return Response({"auth_url": url})


# Get the current Spotify user's profile
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_spotify_profile(request):
    token = get_user_token(request.user)

    if token is None:
        return Response({"error": "Spotify not connected"}, status=403)

    if token.is_expired():
        token = refresh_spotify_token(request.user)
        if token is None:
            return Response({"error": "Failed to refresh token"}, status=403)

    headers = {"Authorization": f"Bearer {token.access_token}"}
    res = requests.get("https://api.spotify.com/v1/me", headers=headers)

    return Response(res.json(), status=res.status_code)


# Refresh access token
@api_view(["GET"])
def refresh_spotify_token(request):
    refresh_token = request.session.get("spotify_refresh_token")
    if not refresh_token:
        return Response({"error": "No refresh token found"}, status=400)

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "client_secret": settings.SPOTIFY_CLIENT_SECRET,
    }

    res = requests.post("https://accounts.spotify.com/api/token", data=payload)
    data = res.json()

    if "access_token" in data:
        request.session["spotify_access_token"] = data["access_token"]
        request.session["spotify_token_expires"] = data["expires_in"]
        return Response({"message": "Token refreshed", "access_token": data["access_token"]})
    else:
        return Response({"error": "Failed to refresh token", "details": data}, status=400)


@api_view(["GET"])
def spotify_callback(request):
    code = request.GET.get("code")
    jwt_token = request.GET.get("state")
    if not code or not jwt_token:
        return Response({"error": "No code provided"}, status=400)

    try:
        validated_token = JWTAuthentication().get_validated_token(jwt_token)
        user = JWTAuthentication().get_user(validated_token)
    except AuthenticationFailed:
        return Response({"error": "Invalid or expired token"}, status=403)

    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "client_secret": settings.SPOTIFY_CLIENT_SECRET,
    }

    res = requests.post("https://accounts.spotify.com/api/token", data=payload)
    data = res.json()

    if "access_token" not in data:
        return Response({"error": "Token exchange failed", "details": data}, status=400)

    update_or_create_user_token(
        user=user,
        access_token=data["access_token"],
        refresh_token=data["refresh_token"],
        expires_in=data["expires_in"]
    )

    frontend_redirect_url = f"https://thearchet.com/more"

    return HttpResponseRedirect(frontend_redirect_url)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_top_genre(request):
    token = get_user_token(request.user)
    if not token:
        return Response({"error": "Spotify not connected"}, status=403)

    if token.is_expired():
        token = refresh_spotify_token(request.user)
        if not token:
            return Response({"error": "Token refresh failed"}, status=403)

    genres = get_user_top_ui_genres(token.access_token)
    return Response({"top_genres": genres})
