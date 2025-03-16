from django.urls import path
from .views import QuestionListView, MatchingView

urlpatterns = [
    path('questions/', QuestionListView.as_view(), name='questions'),
    path('submit/', MatchingView.as_view(), name='matching'),
]
