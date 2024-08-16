from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers

from users.models import Balance, Subscription

User = get_user_model()


class CustomUserSerializer(UserSerializer):
    """Сериализатор пользователей."""

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    """Сериализатор подписки."""

    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Subscription
        fields = (
            'user',
            'is_active',
            'course',
            'start_date',
            'end_date',
        )


class BalanceSerializer(serializers.ModelSerializer):
    """Сериализатор баланса."""

    class Meta:
        model = Balance
        fields = ['user', 'balance']
