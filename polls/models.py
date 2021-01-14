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

    @classmethod
    def from_db(cls, db, field_names, values):
        """Костылим примером из доков, чтобы запретить изменение старта"""
        if len(values) != len(cls._meta.concrete_fields):
            values = list(values)
            values.reverse()
            values = [
                values.pop() if f.attname in field_names else DEFERRED
                for f in cls._meta.concrete_fields
            ]

        instance = cls(*values)
        instance._state.adding = False
        instance._state.db = db

        instance._loaded_values = dict(zip(field_names, values))
        return instance

    def save(self, *args, **kwargs):
        """Перегружаем базовый метод, чтобы защитить start от изменения"""
        if not self._state.adding and (self.start != self._loaded_values["start"]):
            raise ValueError("Нельзя обновить значение start")

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Перегружаем преобразование в строку"""
        return self.name


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

    def __str__(self) -> str:
        """Перегружаем преобразование в строку"""
        return self.text


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

    def __str__(self) -> str:
        """Перегружаем преобразование в строку"""
        return self.text


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
