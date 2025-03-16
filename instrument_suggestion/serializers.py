from rest_framework import serializers
from .models import Question, QuestionOption, InstrumentSuggestion, Instrument


class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ['id', 'text', 'value']


class QuestionSerializer(serializers.ModelSerializer):
    options = QuestionOptionSerializer(many=True, source='questionoption_set')

    class Meta:
        model = Question
        fields = ['id', 'text', 'label', 'options']


class AnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    selected_option_value = serializers.IntegerField()


class InstrumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instrument
        fields = ['name']


class InstrumentSuggestionSerializer(serializers.Serializer):
    suggested_instrument = InstrumentSerializer()

    class Meta:
        model = InstrumentSuggestion
        fields = ['suggested_instrument', 'created_at']

