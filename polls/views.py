from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request

from .models import *
from .serializers import *


@api_view(["GET"])
def active(request: HttpRequest) -> Response:
    """Получаем список активных опросов"""
    now = timezone.now()
    active_polls = Poll.objects.filter(start__lte=now, end__gte=now)
    serializer = PollSerializer(active_polls, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def poll(request: HttpRequest, poll_id: int) -> Response:
    """Получаем список вопросов для данного опроса"""
    try:
        poll = Poll.objects.get(id=poll_id)

    except Poll.DoesNotExist:
        return Response("Does not exist", status=400)

    now = timezone.now()

    # Если опрос неактивен, то вернем ошибку
    if not (poll.end > now > poll.start):
        return Response("Poll is inactive", status=400)

    questions = Question.objects.filter(poll=poll_id)
    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def question(request: HttpRequest, question_id: int) -> Response:
    """Получаем список вариантов ответа для вопроса"""
    try:
        question = Question.objects.get(id=question_id)

    except Question.DoesNotExist:
        return Response("Does not exist", status=400)

    if question.answer_type == 0:
        return Response("Text answers only", status=400)

    options = Option.objects.filter(question=question.id)
    serializer = OptionSerializer(options, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def answer(request: Request) -> Response:
    """Получаем и обрабатываем ответы"""
    data = request.data

    errors = []

    poll_id = None
    user_id = None
    answers = None

    if "id" not in data:
        errors.append("User id")

    if "poll" not in data:
        errors.append("Poll id")

    if "answers" not in data:
        errors.append("Answers")

    if errors:
        error = ", ".join(errors)
        return Response(f"{error} must be provided", status=400)

    user_id = int(data["id"])
    poll_id = int(data["poll"])
    answers = data["answers"]

    now = timezone.now()

    poll = Poll.objects.get(id=poll_id)

    if not (poll.end > now > poll.start):
        return Response("Poll is inactive", status=400)

    response = {
        "id": user_id,
        "poll": poll_id,
        "answers": []
    }

    for answer in answers:
        try:
            question_id = answer["question"]
            question = Question.objects.get(id=question_id)

        # Если в объекте нет id вопроса, то пропустим объект
        except KeyError:
            continue

        # Если вопроса не существует, то запишем в ошибки и пропустим
        except Question.DoesNotExist:
            response["answers"].append({
                "question": question_id,
                "error": "Question does not exist"
            })
            continue

        if question.poll.id != poll_id:
            response["answers"].append({
                "question": question_id,
                "error": "This poll does not have such answer"
            })
            continue

        if "answer" not in answer:
            response["answers"].append({
                "question": question_id,
                "error": "Answer is missing"
            })
            continue

        answer_exists = Answer.objects.filter(
            user=user_id,
            question=question
        ).count() > 0

        if answer_exists and question.answer_type < 2:
            response["answers"].append({
                "question": question_id,
                "error": "Already answered"
            })
            continue

        if question.answer_type == 0:
            try:
                answer = Answer(
                    user=user_id,
                    question=question,
                    text=answer["answer"]
                )
                answer.save()

            except:
                response["answers"].append({
                    "question": question_id,
                    "error": "Wrong answer format"
                })
                continue

        elif question.answer_type == 1:
            try:
                option_id = answer["answer"]
                option = Option.objects.get(id=option_id)

                if option.question.id != question_id:
                    response["answers"].append({
                        "question": question_id,
                        "error": "This question does not have such option"
                    })
                    continue

                answer = Answer(
                    user=user_id,
                    question=question,
                    option=option
                )
                answer.save()

            except Option.DoesNotExist:
                response["answers"].append({
                    "question": question_id,
                    "error": f"Option {option_id} does not exist"
                })
                continue

            except:
                response["answers"].append({
                    "question": question_id,
                    "error": "Wrong answer format"
                })
                continue

        elif question.answer_type == 2:
            for option_id in answer["answer"]:
                try:
                    option = Option.objects.get(id=option_id)

                except Option.DoesNotExist:
                    response["answers"].append({
                        "question": question_id,
                        "error": f"Option {option_id} does not exist"
                    })
                    continue

                if option.question.id != question.id:
                    response["answers"].append({
                        "question": question_id,
                        "error": "This question does not have such option"
                    })
                    continue

                option_answered = Answer.objects.filter(
                    user=user_id,
                    question=question,
                    option=option
                ).count() > 0

                if option_answered:
                    response["answers"].append({
                        "question": question_id,
                        "error": f"Option {option_id} had been already chosen"
                    })
                    continue

                answer = Answer(
                    user=user_id,
                    question=question,
                    option=option
                )
                answer.save()

    return Response(response)


@api_view(["GET"])
def answers(request: HttpRequest, user_id: int) -> Response:
    """Возвращаем результаты опросов для пользователя по его id"""
    answers = Answer.objects.filter(user=user_id)

    if answers.count() == 0:
        return Response([])

    questions = Question.objects.filter(pk__in=[
        answer.question.id for answer in answers
    ])

    polls = Poll.objects.filter(pk__in=[
        question.poll.id for question in questions
    ])

    results = []

    for poll in polls:
        poll_data = {
            "poll_id": poll.id,
            "questions": []
        }

        for question in questions:
            if question.poll != poll:
                continue

            answered = []

            for answer in answers:
                if answer.question != question:
                    continue

                if answer.text is None:
                    answered.append({
                        "option_id": answer.option.id
                    })
                else:
                    answered.append({
                        "text": answer.text
                    })

            if answered:
                if question.answer_type < 2:
                    poll_data["questions"].append({
                        "question_id": question.id,
                        "answer": answered[0]
                    })

                else:
                    poll_data["questions"].append({
                        "question_id": question.id,
                        "answers": answered
                    })

    return Response(poll_data)
