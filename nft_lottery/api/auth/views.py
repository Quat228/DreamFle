import json
import logging
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from core.telegram_auth import parse_and_validate_init_data
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()
logger = logging.getLogger(__name__)


class TelegramAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info("Telegram auth request received")
        # Debug: log all headers
        logger.info(f"Request headers: {dict(request.headers)}")
        # Вытаскиваем Authorization header
        auth_header = request.headers.get("Authorization", "")
        logger.info(f"Authorization header received: '{auth_header[:50]}...' (length: {len(auth_header)})")
        if not auth_header.startswith("tma "):
            logger.warning(f"Invalid Authorization header format. Received: '{auth_header[:100]}'")
            return Response({"detail": "Authorization header missing or invalid. Expected format: 'tma <initData>'"}, status=400)

        init_data_raw = auth_header[4:]  # удаляем "tma "
        logger.debug("Processing initData for Telegram authentication")

        try:
            params = parse_and_validate_init_data(init_data_raw)
        except Exception as e:
            logger.error(f"Telegram initData validation failed: {str(e)}")
            return Response({"detail": str(e)}, status=400)

        # user параметр приходит как JSON строка
        user_json = params.get("user")
        if not user_json:
            logger.error("user parameter missing in initData")
            return Response({"detail": "user missing in initData"}, status=400)

        try:
            user_data = json.loads(user_json)
            telegram_id = user_data["id"]
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse user data from initData: {str(e)}")
            return Response({"detail": f"Invalid user data in initData: {str(e)}"}, status=400)

        # Ищем или создаём пользователя
        user, created = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                "username": user_data.get("username") or f"user_{telegram_id}"
            }
        )
        if created:
            logger.info(f"New user created: telegram_id={telegram_id}, username={user.username}")
        else:
            logger.info(f"Existing user authenticated: telegram_id={telegram_id}, username={user.username}")

        # Обновляем, если поменялся username
        if user.username != user_data.get("username") and user_data.get("username"):
            user.username = user_data["username"]
            user.save()
            logger.info(f"Updated username for user {telegram_id}")

        # Генерируем JWT
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        logger.info(f"JWT tokens generated for user {telegram_id}")

        return Response({
            "access": access,
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "token_balance": str(user.token_balance),
                "credit_balance": str(user.credit_balance),
            }
        })


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom token refresh view that handles errors gracefully,
    especially when user doesn't exist.
    """
    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except (InvalidToken, TokenError) as e:
            logger.warning(f"Token refresh failed: {str(e)}")
            # Return 401 instead of 500 for invalid/expired tokens
            return Response(
                {"detail": "Token is invalid or expired. Please re-authenticate."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            logger.error(f"Unexpected error during token refresh: {str(e)}")
            # Handle user not found or other errors gracefully
            return Response(
                {"detail": "Token refresh failed. Please re-authenticate."},
                status=status.HTTP_401_UNAUTHORIZED
            )
