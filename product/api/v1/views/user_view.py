from django.contrib.auth import get_user_model
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.serializers.user_serializer import (
    BalanceSerializer, CustomUserSerializer
)
from users.models import Balance

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    http_method_names = ["get", "head", "options"]
    permission_classes = (permissions.IsAdminUser,)


class BalanceViewSet(viewsets.ModelViewSet):
    queryset = Balance.objects.all()
    serializer_class = BalanceSerializer
    permission_classes = (permissions.IsAdminUser,)

    @action(detail=True, methods=["post"])
    def increase(self, request, pk):
        balance = self.get_object()
        amount = request.data.get("amount")
        return Response(
            {"status": "Баланс пополнен", "balance": balance.increase(amount)}
        )

    @action(detail=True, methods=["post"])
    def decrease(self, request, pk):
        balance = self.get_object()
        amount = request.data.get("amount")
        try:
            balance.decrease(amount)
            return Response(
                {"status": "Баланс списан",
                 "balance": balance.decrease(amount)}
            )
        except ValueError:
            return Response(
                {"status": "Ошибка. Недостаточно средств на балансе",
                 "message": "Недостаточно средств на балансе"},
                status=status.HTTP_400_BAD_REQUEST
            )
