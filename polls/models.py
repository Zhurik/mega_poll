from django.db import models


class Poll(models.Model):
    """Опрос"""
    name = models.CharField(
        max_length=256,
        verbose_name="Название опроса"
    )

    start = models.DateTimeField(
        verbose_name="Дата и время начала опроса"
    )

    end = models.DateTimeField(
        verbose_name="Дата и время окончания опроса"
    )

    description = models.CharField(
        max_length=1024,
        default=""
    )

    def save(self, *args, **kwargs):
        """Перегружаем базовый метод, чтобы защитить start от изменения"""
        if not self._state.adding and (self.start != self._loaded_values["start"]):
            raise ValueError("Нельзя обновить значение start")

        super().save(*args, **kwargs)



TEXT = 0
SINGLE = 1
MULTIPLE = 2

ANSWER_TYPES = [
    (TEXT, "Текстовый ответ"),
    (SINGLE, "Один вариант"),
    (MULTIPLE, "Несколько вариантов")
]


class Question(models.Model):
    """Вопрос в опросе"""
    text = models.CharField(
        max_length=256,
        verbose_name="Текст вопроса"
    )

    answer_type = models.PositiveSmallIntegerField(
        verbose_name="Тип ответа: текст, один вариант, несколько вариантов",
        choices=ANSWER_TYPES
    )

    poll = models.ForeignKey(
        Poll,
        on_delete=models.CASCADE
    )


class Option(models.Model):
    """Вариант ответа в вопросе"""
    text = models.CharField(
        max_length=256,
        verbose_name="Текст варианта"
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )


class Answer(models.Model):
    """Введенный или выбранный пользователем ответ"""
    user = models.IntegerField(
        verbose_name="Id пользователя, который отвечал на вопрос"
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )

    text = models.CharField(
        max_length=1024,
        verbose_name="Ответ на текстовый вопрос",
        blank=True,
        null=True
    )

    option = models.ForeignKey(
        Option,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
