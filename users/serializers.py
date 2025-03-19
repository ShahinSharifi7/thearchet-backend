from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "phone_number"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user


class ProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    age = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ["email", "phone_number", "profile_picture", "first_name", "last_name", "birth_date", "gender", "city",
                  "province", "personality_social", "personality_detail", "decision_making",
                  "planning_style", "level_of_expertise", "favorite_genre", "available_time", "own_song",
                  "academic_knowledge", "preferred_instrument", "preferred_clothing", "age", "username", "is_premium",
                  "instagram", "spotify", "soundcloud", "youtube", "apple_music"]

    def get_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.profile_picture and hasattr(obj.profile_picture, 'url'):
            return request.build_absolute_uri(obj.profile_picture.url) if request else obj.profile_picture.url
        return None


class MessageProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["username", "profile_picture"]

    def get_profile_picture(self, obj):
        request = self.context.get('request')
        if obj.profile_picture and hasattr(obj.profile_picture, 'url'):
            return request.build_absolute_uri(obj.profile_picture.url) if request else obj.profile_picture.url
        return None


class ProfileCompletionSerializer(serializers.ModelSerializer):
    is_profile_complete = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["profile_picture", "phone_number", "first_name", "last_name", "birth_date", "gender", "city",
                  "province", "personality_social", "personality_detail", "decision_making",
                  "planning_style", "level_of_expertise", "favorite_genre", "available_time", "own_song",
                  "academic_knowledge", "preferred_instrument", "preferred_clothing", "is_profile_complete",
                  "instagram", "spotify", "soundcloud", "youtube", "apple_music"]

    def get_is_profile_complete(self, obj):
        required_fields = ["birth_date", "gender", "personality_social", "personality_detail", "decision_making",
                           "planning_style", "city", "province"]
        return all(getattr(obj, field) for field in required_fields)
