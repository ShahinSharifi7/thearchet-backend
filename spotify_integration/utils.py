from .models import SpotifyToken
from django.utils import timezone
from datetime import timedelta
import requests
from django.conf import settings
from collections import defaultdict

def get_user_token(user):
    try:
        return SpotifyToken.objects.get(user=user)
    except SpotifyToken.DoesNotExist:
        return None

def update_or_create_user_token(user, access_token, refresh_token, expires_in):
    token, created = SpotifyToken.objects.update_or_create(
        user=user,
        defaults={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": expires_in,
            "created_at": timezone.now(),
        }
    )
    return token

def refresh_spotify_token(user):
    token = get_user_token(user)
    if not token or not token.refresh_token:
        return None

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": token.refresh_token,
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "client_secret": settings.SPOTIFY_CLIENT_SECRET,
    }

    res = requests.post("https://accounts.spotify.com/api/token", data=payload)
    data = res.json()

    if "access_token" in data:
        new_token = update_or_create_user_token(
            user,
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token", token.refresh_token),
            expires_in=data["expires_in"]
        )
        return new_token
    return None


GENRE_MAP = {
    "classical": [
        "classical", "baroque", "romantic", "contemporary classical", "piano classical", "orchestral", "chamber pop"
    ],
    "jazz / blues": [
        "jazz", "vocal jazz", "smooth jazz", "bebop", "soul jazz", "blues", "electric blues"
    ],
    "rock": [
        "rock", "alternative rock", "modern rock", "classic rock", "hard rock", "indie rock", "garage rock",
        "grunge", "punk", "alt-rock"
    ],
    "folk / traditional": [
        "folk", "traditional", "indie folk", "american folk", "celtic", "bluegrass", "world", "ethno", "acoustic"
    ],
    "country": [
        "country", "modern country", "country rock", "americana", "red dirt"
    ],
    "latin": [
        "latin", "reggaeton", "salsa", "bachata", "latin pop", "latin rock", "tropical", "cumbia"
    ],
    "pop": [
        "pop", "dance pop", "indie pop", "electropop", "synthpop", "k-pop", "teen pop"
    ]
}

GENRE_VALUES = {
    "classical": 0,
    "jazz / blues": 1,
    "rock": 2,
    "folk / traditional": 3,
    "country": 4,
    "latin": 5,
    "pop": 6,
}


def map_genre(raw_genre):
    raw_genre = raw_genre.lower()
    for main_genre, synonyms in GENRE_MAP.items():
        if raw_genre in synonyms:
            return main_genre
    return None  # Unrecognized genres can be skipped or grouped as "other"


def get_user_top_ui_genres(access_token):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    res = requests.get(
        "https://api.spotify.com/v1/me/top/artists?limit=50&time_range=medium_term",
        headers=headers
    )

    if res.status_code != 200:
        return {"error": "Could not fetch top artists"}

    data = res.json()
    genre_count = defaultdict(int)

    for artist in data.get("items", []):
        for genre in artist.get("genres", []):
            mapped = map_genre(genre)
            if mapped:
                genre_count[mapped] += 1

    sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)

    # Only return genres that exist in your UI
    allowed_ui_genres = set(GENRE_MAP.keys())
    return [GENRE_VALUES[genre] for genre, _ in sorted_genres if genre in GENRE_VALUES][:3]
