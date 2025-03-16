from django.contrib import admin
from django.contrib import messages
from .models import MatchingQuestion, MatchingQuestionOption, MatchingUserAnswer
from django.db import connection

def delete_table_data(modeladmin, request, queryset):
    """Deletes all records from the selected model"""
    queryset.delete()
    messages.success(request, "Selected records have been deleted.")

delete_table_data.short_description = "Delete selected records"

def drop_table(modeladmin, request, queryset):
    """Drops the table for the model (only works if the database supports it)"""
    model = modeladmin.model
    table_name = model._meta.db_table
    with connection.cursor() as cursor:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
    messages.success(request, f"Table '{table_name}' has been dropped. You may need to migrate again.")

drop_table.short_description = "Drop table (WARNING: Requires migration after)"

@admin.register(MatchingQuestion)
class MatchingQuestionAdmin(admin.ModelAdmin):
    list_display = ("text", "label", "type")
    search_fields = ("text", "label", "type")
    actions = [delete_table_data, drop_table]

@admin.register(MatchingQuestionOption)
class MatchingQuestionOptionAdmin(admin.ModelAdmin):
    list_display = ("question", "text")
    search_fields = ("text",)
    list_filter = ("question",)
    actions = [delete_table_data, drop_table]

@admin.register(MatchingUserAnswer)
class MatchingUserAnswerAdmin(admin.ModelAdmin):
    list_display = ("user", "question", "response")
    search_fields = ("user__username", "question__text", "response")
    list_filter = ("question", "user")
    actions = [delete_table_data, drop_table]
