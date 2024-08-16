from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.permissions import IsStudentOrIsAdmin, ReadOnlyOrIsAdmin
from api.v1.serializers.course_serializer import (CourseSerializer,
                                                  CreateCourseSerializer,
                                                  CreateGroupSerializer,
                                                  CreateLessonSerializer,
                                                  GroupSerializer,
                                                  LessonSerializer,
                                                  PayCourseSerializer)
from api.v1.serializers.user_serializer import SubscriptionSerializer
from courses.models import Course, Group, UserCourse
from users.models import Balance, Subscription


class LessonViewSet(viewsets.ModelViewSet):
    """Уроки."""

    permission_classes = (IsStudentOrIsAdmin,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return LessonSerializer
        return CreateLessonSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return course.lessons.all()


class GroupViewSet(viewsets.ModelViewSet):
    """Группы."""

    permission_classes = (permissions.IsAdminUser,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return GroupSerializer
        return CreateGroupSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return course.groups.all()

    @action(
        methods=['get'],
        detail=True,
    )
    def groups(self, request, pk):
        course = get_object_or_404(Course, id=pk)
        groups = Group.objects.filter(course=course)
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data)


class CourseViewSet(viewsets.ModelViewSet):
    """Курсы """

    permission_classes = (ReadOnlyOrIsAdmin,)

    def get_queryset(self):
        user = self.request.user
        paid_courses = UserCourse.objects.filter(
            user=user, has_access=True
        ).values_list('course', flat=True)
        return Course.objects.filter(
            is_available=True
        ).exclude(id__in=paid_courses)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CourseSerializer
        return CreateCourseSerializer

    def assign_user_to_group(self, user, course):
        groups = Group.objects.get(course=course)
        group_min = groups.annotate(
            users_count=Count('users'),
        ).order_by('users_count').first()
        if group_min <= 10 and group_min.max_students < 30:
            group_min.users.add(user)

    @action(
        methods=['post'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def pay(self, request, pk):
        """Покупка доступа к курсу (подписка на курс)."""

        user = request.user
        serializer = PayCourseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = get_object_or_404(
            Course, id=serializer.validated_data['course_id']
        )
        if Subscription.objects.filter(
           user=user, course=course, is_active=True).exists():
            return Response(
                {'message': 'Вы уже подписаны на этот курс.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if UserCourse.objects.filter(
            user=user, course=course, has_access=True
        ).exists():
            return Response(
                {'message': 'Вы уже купили этот курс.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not Balance.objects.get(user=request.user).withdraw(course.price):
            return Response(
                {'message': 'Недостаточно бонусов на балансе'},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            UserCourse.objects.create(
                user=user,
                course=course,
                has_access=True
            )
            subscription = Subscription.objects.create(
                user=user,
                course=course
            )
            self.assign_user_to_group(user, course)
            return Response(
                SubscriptionSerializer(subscription).data,
                status=status.HTTP_201_CREATED
            )

    @action(detail=True, methods=['get'],)
    def courses(self, request, pk):
        """Получение доступных курсов."""

        courses = Course.objects.filter(is_available=True)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)
