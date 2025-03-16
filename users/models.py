from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date


class User(AbstractUser):
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, null=True, blank=True)
    province = models.CharField(max_length=40, null=True, blank=True)
    city = models.CharField(max_length=60, null=True, blank=True)
    personality_social = models.CharField(max_length=1, null=True, blank=True)
    personality_detail = models.CharField(max_length=1, null=True, blank=True)
    decision_making = models.CharField(max_length=1, null=True, blank=True)
    planning_style = models.CharField(max_length=1, null=True, blank=True)
    level_of_expertise = models.TextField(max_length=100, null=True, blank=True)
    favorite_genre = models.CharField(max_length=30, null=True, blank=True)
    available_time = models.TextField(null=True, blank=True)
    own_song = models.CharField(max_length=3, null=True, blank=True)
    academic_knowledge = models.CharField(max_length=3, null=True, blank=True)
    preferred_instrument = models.CharField(max_length=30, null=True, blank=True)
    preferred_clothing = models.CharField(max_length=30, null=True, blank=True)
    instagram = models.TextField(max_length=1000, null=True, blank=True)
    spotify = models.TextField(max_length=1000, null=True, blank=True)
    soundcloud = models.TextField(max_length=1000, null=True, blank=True)
    youtube = models.TextField(max_length=1000, null=True, blank=True)
    apple_music = models.TextField(max_length=1000, null=True, blank=True)
    is_premium = models.BooleanField(default=False)

    matched_users = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return self.username

    @property
    def age(self):
        if self.birth_date:
            today = date.today()
            return today.year - self.birth_date.year - (
                        (today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None  # Return None if birth_date is not set

