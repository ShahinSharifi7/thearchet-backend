from django.urls import path
from . import views

urlpatterns = [
    path('nearby-events/', views.NearbyEventsView.as_view(), name='nearby-events'),
]

