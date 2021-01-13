from rest_framework import serializers
from .models import *


class PollSerializer(serializers.ModelSerializer):
    """Сериализуем опросики"""
    class Meta:
        model = Poll
        fields = ["id", "name", "start", "end", "description"]
