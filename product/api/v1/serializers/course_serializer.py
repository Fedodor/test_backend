from django.contrib.auth import get_user_model
from django.db.models import Avg, Count
from rest_framework import serializers

from courses.models import Course, Group, Lesson, UserCourse
from users.models import CustomUser

User = get_user_model()


class LessonSerializer(serializers.ModelSerializer):
    """Список уроков."""

    course = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Lesson
        fields = (
            'title',
            'link',
            'course'
        )


class CreateLessonSerializer(serializers.ModelSerializer):
    """Создание уроков."""

    class Meta:
        model = Lesson
        fields = (
            'title',
            'link',
            'course'
        )


class StudentSerializer(serializers.ModelSerializer):
    """Студенты курса."""

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
        )


class GroupSerializer(serializers.ModelSerializer):
    """Список групп."""

    course = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Group
        fields = (
            'group_number',
            'course',
        )


class CreateGroupSerializer(serializers.ModelSerializer):
    """Создание групп."""

    class Meta:
        model = Group
        fields = (
            'group_number',
            'course',
        )


class MiniLessonSerializer(serializers.ModelSerializer):
    """Список названий уроков для списка курсов."""

    class Meta:
        model = Lesson
        fields = (
            'title',
        )


class CourseSerializer(serializers.ModelSerializer):
    """Список курсов."""

    lessons = MiniLessonSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField(read_only=True)
    students_count = serializers.SerializerMethodField(read_only=True)
    groups_filled_percent = serializers.SerializerMethodField(read_only=True)
    demand_course_percent = serializers.SerializerMethodField(read_only=True)

    def get_lessons_count(self, obj):
        """Количество уроков в курсе."""

        return Lesson.objects.filter(course=obj).count()

    def get_students_count(self, obj):
        """Общее количество студентов на курсе."""

        return UserCourse.objects.filter(course=obj, has_access=True).count()

    def get_groups_filled_percent(self, obj):
        """Процент заполнения групп, если в группе максимум 30 чел.."""
        groups = obj.groups.all()
        if not groups.exists():
            return 0
        avg = groups.annotate(
            filled=Count('students')
        ).aggregate(Avg('filled'))['filled__avg']
        return (avg / 30) * 100 if avg else 0

    def get_demand_course_percent(self, obj):
        """Процент приобретения курса."""

        total_users = CustomUser.objects.all().exclude(is_staff=True).count()
        accessed_users = UserCourse.objects.filter(
            course=obj, has_access=True
        ).count()

        return (accessed_users / total_users) * 100

    class Meta:
        model = Course
        fields = (
            'id',
            'author',
            'title',
            'start_date',
            'price',
            'lessons_count',
            'lessons',
            'demand_course_percent',
            'students_count',
            'groups_filled_percent',
        )


class CreateCourseSerializer(serializers.ModelSerializer):
    """Создание курсов."""

    class Meta:
        model = Course
        fields = (
            'author',
            'title',
            'start_date',
            'price',
            'is_available',
        )


class PayCourseSerializer(serializers.Serializer):
    """Покупка курса."""

    course_id = serializers.IntegerField()

    def validate_course_id(self, value):
        """Проверка наличия курса."""

        try:
            course = Course.objects.get(id=value)
        except Course.DoesNotExist:
            raise serializers.ValidationError('Курс не найден')

        if not course.is_available:
            raise serializers.ValidationError('Курс недоступен')

        return value
