from django.db import migrations

from matching.models import MatchingQuestion, MatchingQuestionOption


def populate_static_data(apps, schema_editor):
    Question = apps.get_model('instrument_suggestion', 'Question')
    QuestionOption = apps.get_model('instrument_suggestion', 'QuestionOption')

    questions = [
        {"text": "Do you prefer to match with someone who has academic knowledge?", "label": "Academic Knowledge",
         "type": "Choice"},
        {"text": "Do you prefer to match with which kind of artist?", "label": "Instrument", "type": "Choice"},
        {"text": "Do you prefer to match with a male or female?", "label": "Gender", "type": "Choice"},
        {"text": "Do you prefer to match with someone who has their own song?", "label": "Own Song", "type": "Choice"},
        {"text": "Do you prefer to match with someone with a specific clothing style?", "label": "Clothing Style", "type": "Choice"},
        {"text": "Enter your preferred maximum distance for matching (km)", "label": "Preferred Distance",
         "type": "Text"},
    ]

    question_options = [
        {"label": "Academic Knowledge", "text": "Yes"},
        {"label": "Academic Knowledge", "text": "No"},
        {"label": "Academic Knowledge", "text": "Never mind"},
        {"label": "Instrument", "text": "Electric Guitar"},
        {"label": "Instrument", "text": "Saxophone"},
        {"label": "Instrument", "text": "Drums and Percussion"},
        {"label": "Instrument", "text": "Violin"},
        {"label": "Instrument", "text": "Acoustic Guitar"},
        {"label": "Instrument", "text": "Piano"},
        {"label": "Instrument", "text": "Cello"},
        {"label": "Instrument", "text": "Flute"},
        {"label": "Gender", "text": "Male"},
        {"label": "Gender", "text": "Female"},
        {"label": "Gender", "text": "Never mind"},
        {"label": "Own Song", "text": "Yes"},
        {"label": "Own Song", "text": "No"},
        {"label": "Own Song", "text": "Never mind"},
        {"label": "Clothing Style", "text": "Classic and Formal"},
        {"label": "Clothing Style", "text": "Vintage-Inspired"},
        {"label": "Clothing Style", "text": "Sporty and Active"},
        {"label": "Clothing Style", "text": "Urban and Street Style"},
        {"label": "Clothing Style", "text": "Dark and Gothic"},
        {"label": "Clothing Style", "text": "Never mind"},
    ]
    for question in questions:
        created_question, _ = MatchingQuestion.objects.get_or_create(**question)
        # Add static questions options
        filtered_options = [option for option in question_options if option["label"] == created_question.label]
        for option in filtered_options:
            MatchingQuestionOption.objects.get_or_create(question=created_question, text=option["text"])


def remove_static_data(apps, schema_editor):
    MatchingQuestion.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('matching', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_static_data),
    ]
