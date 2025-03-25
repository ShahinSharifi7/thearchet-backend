from django.db import models
from users.models import User


# Create your models here.
class SpotifyToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    expires_in = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        from datetime import timedelta, timezone, datetime
        return self.created_at + timedelta(seconds=self.expires_in) < datetime.now(timezone.utc)