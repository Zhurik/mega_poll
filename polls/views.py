from datetime import datetime

from django.http import HttpRequest, HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import *
from .serializers import *


@api_view(["GET"])
def active(request: HttpRequest) -> Response:
    """Получаем список активных опросов"""
    now = datetime.now()
    active_polls = Poll.objects.filter(start__lte=now, end__gte=now)
    serializer = PollSerializer(active_polls, many=True)
    return Response(serializer.data)
