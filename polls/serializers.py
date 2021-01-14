from typing import List, Optional

from rest_framework import serializers
from .models import *


class PollSerializer(serializers.ModelSerializer):
    """Сериализуем опросики"""
    questions = serializers.SerializerMethodField("get_questions")

    def get_questions(self, poll: Poll) -> List[int]:
        """Получаем список вопросов для текущего опроса"""
        questions = Question.objects.filter(poll=poll.id)
        return [q.id for q in questions]

    class Meta:
        model = Poll
        fields = [
            "id",
            "name",
            "start",
            "end",
            "description",
            "questions"
        ]


class QuestionSerializer(serializers.ModelSerializer):
    """Сериализуем вопросы"""
    options = serializers.SerializerMethodField("get_options")

    def get_options(self, question: Question) -> Optional[List[int]]:
        """Получаем список вариантов ответа для вопроса"""
        if question.answer_type == 0:
            return

        options = Option.objects.filter(question=question.id)
        return [opt.id for opt in options]


    class Meta:
        model = Question
        fields = ["id", "text", "answer_type", "poll", "options"]


class OptionSerializer(serializers.ModelSerializer):
    """Сериализуем опции для вопросов"""
    class Meta:
        model = Option
        fields = ["id", "text", "question"]
