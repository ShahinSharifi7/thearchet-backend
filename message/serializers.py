from rest_framework import serializers

from users.models import User
from .models import Message
from users.serializers import MessageProfileSerializer


class ReceivedMessagesSerializer(serializers.ModelSerializer):
    sender = MessageProfileSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'text', 'subject', 'seen', 'created_at']
        read_only_fields = ['created_at']


class SentMessagesSerializer(serializers.ModelSerializer):
    receiver = MessageProfileSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'receiver', 'subject', 'text', 'created_at']


class SendMessageSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Message.objects.all(), required=False, allow_null=True
    )
    receiver = serializers.CharField(write_only=True)

    class Meta:
        model = Message
        fields = ['receiver', 'subject', 'text', 'parent']

    def validate_receiver(self, value):
        """Validate that receiver is a valid username."""
        try:
            # Look up the User by the provided username
            receiver_user = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Receiver with the given username does not exist.")
        return receiver_user

    def create(self, validated_data):
        sender = self.context['request'].user
        parent = validated_data.pop('parent', None)

        # Set sender
        validated_data['sender'] = sender

        receiver = validated_data.pop('receiver')

        if parent:
            # Ensure reply has "RE:" only once
            subject = parent.subject
            if not subject.startswith("RE: "):
                subject = f"RE: {subject}"
            validated_data['subject'] = subject
            validated_data['receiver'] = parent.sender  # Reply goes back to the sender of the parent message

        validated_data['receiver'] = receiver
        return super().create(validated_data)
