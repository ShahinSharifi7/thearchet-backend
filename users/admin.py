from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("username", "email", "phone_number", "birth_date", "gender", "display_matched_users", "is_premium")
    search_fields = ("username", "email", "phone_number")
    list_filter = ("gender", "birth_date", "province", "city")
    filter_horizontal = ("matched_users",)  # Enables a multi-select widget for ManyToManyField in admin

    fieldsets = UserAdmin.fieldsets + (
        ("Profile Information", {"fields": (
            "phone_number", "profile_picture", "birth_date", "gender", "province", "city",
            "personality_social", "personality_detail", "decision_making", "planning_style",
            "level_of_expertise", "favorite_genre", "available_time", "own_song",
            "academic_knowledge", "preferred_instrument", "preferred_clothing", "matched_users"
        )}),
    )

    def display_matched_users(self, obj):
        """Display matched users as a comma-separated list"""
        return ", ".join([user.username for user in obj.matched_users.all()])

    display_matched_users.short_description = "Matched Users"


admin.site.register(User, CustomUserAdmin)
