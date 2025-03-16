from django.contrib import admin
from .models import Question, QuestionOption, UserAnswer, Instrument, InstrumentSuggestion

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'label')
    search_fields = ('text', 'label')

@admin.register(QuestionOption)
class QuestionOptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'value')
    list_filter = ('question',)
    search_fields = ('text',)

@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'question', 'response')
    list_filter = ('user', 'question')
    search_fields = ('response',)

@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(InstrumentSuggestion)
class InstrumentSuggestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'suggested_instrument', 'created_at')
    list_filter = ('user', 'suggested_instrument', 'created_at')
    search_fields = ('user__username', 'suggested_instrument__name')

