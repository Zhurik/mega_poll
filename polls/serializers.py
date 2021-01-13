from rest_framework import serializers
from .models import *


class PollSerializer(serializers.ModelSerializer):
    """Сериализуем опросики"""
    class Meta:
        model = Poll
        fields = ["id", "name", "start", "end", "description"]


class QuestionSerializer(serializers.ModelSerializer):
    """Сериализуем вопросы"""
    class Meta:
        model = Question
        fields = ["id", "text", "answer_type", "poll"]


class OptionSerializer(serializers.ModelSerializer):
    """Сериализуем опции для вопросов"""
    class Meta:
        model = Option
        fields = ["id", "text", "question"]
