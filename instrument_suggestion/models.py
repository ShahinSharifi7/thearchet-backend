from django.db import models
from users.models import User


class Question(models.Model):
    text = models.TextField()
    label = models.TextField()

    def __str__(self):
        return self.text


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    text = models.TextField()
    value = models.IntegerField()


class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    response = models.TextField()


class Instrument(models.Model):
    name = models.CharField(max_length=255)


class InstrumentSuggestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    suggested_instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
