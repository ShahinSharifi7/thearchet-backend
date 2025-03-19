from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Message
from .pagination import MessagePagination
from .serializers import SendMessageSerializer, SentMessagesSerializer, ReceivedMessagesSerializer, \
    MessageDetailSerializer


class SendMessageAPIView(generics.CreateAPIView):
    queryset = Message.objects.all()
    serializer_class = SendMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class ReceivedMessagesAPIView(generics.ListAPIView):
    serializer_class = ReceivedMessagesSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MessagePagination

    def get_queryset(self):
        messages = Message.objects.filter(receiver=self.request.user, deleted_by_receiver=False).order_by('-id')
        page = self.paginate_queryset(messages)
        if page is not None:
            Message.objects.filter(id__in=[msg.id for msg in page]).update(seen=True)
            return page
        return messages


class SentMessagesAPIView(generics.ListAPIView):
    serializer_class = SentMessagesSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = MessagePagination

    def get_queryset(self):
        return Message.objects.filter(sender=self.request.user, deleted_by_sender=False).order_by('-id')


class DeleteMessageAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        message_id = request.data.get("id")

        if not message_id:
            return Response({"error": "Message ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            message = Message.objects.get(id=message_id)

            # Ensure the user is the sender or receiver
            if message.sender != request.user and message.receiver != request.user:
                return Response({"error": "You are not authorized to delete this message"},
                                status=status.HTTP_403_FORBIDDEN)

            # Soft delete for the requesting user
            message.delete_for_user(request.user)

            # If both sender and receiver have deleted the message, remove it from the database
            if message.deleted_by_sender and message.deleted_by_receiver:
                message.delete()

            return Response({"message": "Message deleted successfully for you"}, status=status.HTTP_200_OK)

        except Message.DoesNotExist:
            return Response({"error": "Message not found"}, status=status.HTTP_404_NOT_FOUND)


class MessageDetailAPIView(generics.RetrieveAPIView):
    serializer_class = MessageDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        message_id = self.kwargs.get('pk')  # Get message ID from the URL params
        # Ensure the user is either the sender or receiver of the message
        return Message.objects.filter(id=message_id,
                                      sender=self.request.user) | \
            Message.objects.filter(id=message_id,
                                   receiver=self.request.user)

    def get(self, request, *args, **kwargs):
        try:
            # Get the message object using the filtered queryset
            message = self.get_object()
            serializer = self.get_serializer(message)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Message.DoesNotExist:
            return Response({"error": "Message not found or unauthorized access"}, status=status.HTTP_404_NOT_FOUND)
