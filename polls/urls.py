from django.urls import path

from . import views

urlpatterns = [
    path("active", views.active, name="active"),
    path("poll/<int:poll_id>", views.poll, name="poll"),
    path("question/<int:question_id>", views.question, name="question"),
    path("answer", views.answer, name="answer"),
    path("answers/<int:user_id>", views.answers, name="answers")
]
