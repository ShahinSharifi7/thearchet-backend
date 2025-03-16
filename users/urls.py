from django.urls import path
from .views import UserProfileView, RegisterView, LoginView, UpdateProfileView, ProfileCompletionView, GetAllView, \
    HasMatchesAPIView, GetMatchesAPIView, UserProfileByUsernameAPIView, RemovePremiumAPIView, UpgradeToPremiumAPIView

urlpatterns = [
    path('all/', GetAllView.as_view(), name='all-users'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/update/', UpdateProfileView.as_view(), name='user-profile-update'),
    path('profile/completion/', ProfileCompletionView.as_view(), name='user-profile-update'),
    path('profile/<str:username>/', UserProfileByUsernameAPIView.as_view(), name='user-profile-by-username'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path("has_matches/", HasMatchesAPIView.as_view(), name="has-matches"),
    path("get_matches/", GetMatchesAPIView.as_view(), name="get-matches"),
    path('upgrade-premium/', UpgradeToPremiumAPIView.as_view(), name='upgrade-premium'),
    path('remove-premium/', RemovePremiumAPIView.as_view(), name='remove-premium'),
]
