from django.db import models

from users.models import CustomUser


class Course(models.Model):
    """Модель продукта - курса."""

    author = models.CharField(
        max_length=250,
        verbose_name='Автор',
    )
    title = models.CharField(
        max_length=250,
        verbose_name='Название',
    )
    start_date = models.DateTimeField(
        auto_now=False,
        auto_now_add=False,
        verbose_name='Дата и время начала курса'
    )
    price = models.IntegerField(
        verbose_name='Цена',
    )
    is_available = models.BooleanField(
        default=True,
        verbose_name='Доступен',
    )

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ('-id',)

    def __str__(self):
        return self.title


class Lesson(models.Model):
    """Модель урока."""

    title = models.CharField(
        max_length=250,
        verbose_name='Название',
    )
    link = models.URLField(
        max_length=250,
        verbose_name='Ссылка',
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Курс',
    )

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ('id',)

    def __str__(self):
        return self.title


class Group(models.Model):
    """Модель группы."""

    users = models.ForeignKey(
        CustomUser,
        default=None,
        on_delete=models.CASCADE,
        verbose_name='Пользователи',
    )

    group_number = models.IntegerField(
        verbose_name='Номер группы',
        unique=True,
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='groups',
        verbose_name='Курс',
    )
    max_students = models.IntegerField(
        verbose_name='Максимальное количество студентов',
        default=30
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ('-id',)


class UserCourse(models.Model):
    """Модель пользователя - курса."""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='courses',
        verbose_name='Пользователь',
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='users',
        verbose_name='Курс',
    )
    has_access = models.BooleanField(
        default=False,
        verbose_name='Есть доступ',
    )

    class Meta:
        verbose_name = 'Пользователь - курс'
        verbose_name_plural = 'Пользователи - курсы'
        default_related_name = 'users_courses'
        unique_together = ('user', 'course')
        ordering = ('-id',)

    def __str__(self):
        return f'{self.user} - {self.course.title}'
