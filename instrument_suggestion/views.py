from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Question, Instrument, InstrumentSuggestion
from .serializers import QuestionSerializer, AnswerSerializer, InstrumentSuggestionSerializer
from users.serializers import ProfileSerializer
import joblib
import numpy as np
import pandas as pd


class QuestionListView(APIView):
    def get(self, request):
        questions = Question.objects.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class InstrumentSuggestionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        personality_mapping = {'INFJ': '0', 'INFP': '0', 'ENFJ': '0', 'ENFP': '0',
                               'INTJ': '1', 'INTP': '1', 'ENTJ': '1', 'ENTP': '1',
                               'ISFJ': '2', 'ESFJ': '2', 'ISTJ': '2', 'ESTJ': '2',
                               'ISFP': '3', 'ESFP': '3', 'ISTP': '3', 'ESTP': '3'}

        responses = request.data.get("responses", {})
        user = request.user
        profile_data = ProfileSerializer(user).data
        personality_combined = ""
        personality_combined += profile_data["personality_social"]
        personality_combined += profile_data["personality_detail"]
        personality_combined += profile_data["decision_making"]
        personality_combined += profile_data["planning_style"]
        responses["Personality Type"] = personality_mapping.get(personality_combined, -1)

        responses["Gender"] = user.gender
        if user.age < 18:
            responses["Age"] = '0'
        elif 18 <= user.age < 26:
            responses["Age"] = '1'
        elif 26 <= user.age < 41:
            responses["Age"] = '2'
        else:
            responses["Age"] = '3'

        model = joblib.load("instrument_suggestion/machine_learning/modelelema.pkl")
        label_encoder = joblib.load("instrument_suggestion/machine_learning/label_encoder.pkl")
        training_columns = joblib.load("instrument_suggestion/machine_learning/training_columns.pkl")

        responses_df = pd.DataFrame([responses])

        final_features = [
            'Personality Type',
            'Difficulty Level',
            'Portability',
            'Preferred Sound',
            'Maintenance Effort',
            'Playing Purpose',
            'Smoke',
            'Age',
            'Genres',
            'Work Out',
            'Experience (Years)',
        ]
        # Convert responses to DataFrame
        responses_df = responses_df[final_features]

        encoded_responses = pd.get_dummies(responses_df)

        aligned_responses = encoded_responses.reindex(columns=training_columns, fill_value=0)

        input_array = aligned_responses.to_numpy()

        prediction = model.predict(input_array)

        predicted_instrument = label_encoder.inverse_transform([prediction[0]])[0]

        instrument_instance = Instrument.objects.get(name=predicted_instrument)
        InstrumentSuggestion.objects.update_or_create(user=user, suggested_instrument=instrument_instance)

        return Response({"name": predicted_instrument}, status=status.HTTP_200_OK)


class LastInstrumentSuggestionView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access

    def get(self, request):
        last_suggestion = InstrumentSuggestion.objects.filter(user=request.user).order_by('-created_at').first()

        if last_suggestion:
            serializer = InstrumentSuggestionSerializer(last_suggestion)
            return Response(serializer.data)

        return Response({}, status=200)
