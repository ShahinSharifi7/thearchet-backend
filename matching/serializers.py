from rest_framework import serializers
from .models import MatchingQuestionOption, MatchingQuestion


class MatchingQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MatchingQuestionOption
        fields = ['id', 'text']


class MatchingQuestionSerializer(serializers.ModelSerializer):
    options = MatchingQuestionOptionSerializer(many=True, source='matchingquestionoption_set')

    class Meta:
        model = MatchingQuestion
        fields = ['id', 'text', 'label', 'options', 'type']


class AnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    selected_option_value = serializers.IntegerField()