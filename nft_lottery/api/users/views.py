from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated

from users.models import User
from .serializers import UserMeSerializer, ReferralUserSerializer


class MeAPIView(RetrieveAPIView):
    """
    GET /api/users/me/
    Возвращает данные текущего пользователя.
    """
    serializer_class = UserMeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserReferralsAPIView(ListAPIView):
    """
    GET /api/users/referrals/
    Выдаёт список пользователей, которые указали текущего юзера как referred_by.
    """
    serializer_class = ReferralUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(referred_by=self.request.user)
