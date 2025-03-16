from django.urls import path
from .views import InstrumentSuggestionView, QuestionListView, LastInstrumentSuggestionView

urlpatterns = [
    path('questions/', QuestionListView.as_view(), name='questions'),
    path('suggest-instrument/', InstrumentSuggestionView.as_view(), name='suggest-instrument'),
    path('get-suggestion/', LastInstrumentSuggestionView.as_view(), name='get-suggestion'),
]
