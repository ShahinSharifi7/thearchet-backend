from django.db import models
from users.models import User


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='message_sender', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='message_receiver', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    text = models.TextField()
    subject = models.TextField()
    seen = models.BooleanField(default=False)
    deleted_by_sender = models.BooleanField(default=False)
    deleted_by_receiver = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def delete_for_user(self, user):
        if self.sender == user:
            self.deleted_by_sender = True
        elif self.receiver == user:
            self.deleted_by_receiver = True
        self.save()

    def is_visible_to(self, user):
        if self.sender == user and not self.deleted_by_sender:
            return True
        if self.receiver == user and not self.deleted_by_receiver:
            return True
        return False
