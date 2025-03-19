from django.urls import path
from .views import SendMessageAPIView, ReceivedMessagesAPIView, SentMessagesAPIView, DeleteMessageAPIView, \
    MessageDetailAPIView

urlpatterns = [
    path('send-message/', SendMessageAPIView.as_view(), name='send-message'),
    path('received-messages/', ReceivedMessagesAPIView.as_view(), name='received-messages'),
    path('sent-messages/', SentMessagesAPIView.as_view(), name='sent-messages'),
    path('delete-message/', DeleteMessageAPIView.as_view(), name='sent-messages'),
    path('<int:pk>/', MessageDetailAPIView.as_view(), name='message-detail'),
]
