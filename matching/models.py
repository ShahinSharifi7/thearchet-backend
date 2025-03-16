from django.db import models
from users.models import User


class MatchingQuestion(models.Model):
    text = models.TextField()
    label = models.TextField()
    type = models.CharField(max_length=20)

    def __str__(self):
        return self.text


class MatchingQuestionOption(models.Model):
    question = models.ForeignKey(MatchingQuestion, on_delete=models.CASCADE)
    text = models.TextField()


class MatchingUserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(MatchingQuestion, on_delete=models.CASCADE)
    response = models.TextField()
