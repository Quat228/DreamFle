import hmac
import hashlib
import time
from urllib.parse import parse_qsl, unquote

from django.conf import settings


class TelegramInitDataError(Exception):
    """Базовая ошибка для initData."""
    pass


class TelegramInitDataInvalidSignature(TelegramInitDataError):
    """Подпись initData невалидна."""
    pass


class TelegramInitDataExpired(TelegramInitDataError):
    """initData слишком старое (auth_date истёк)."""
    pass


def parse_and_validate_init_data(init_data_raw: str, max_age_seconds: int = 600):
    """
    Валидирует initData по алгоритму Telegram (вариант с BOT TOKEN + hash).
    Возвращает dict с разобранными параметрами (user, auth_date и т.д.), если всё ок.
    Поднимает исключения, если что-то не так.
    """

    bot_token = settings.TELEGRAM_BOT_TOKEN
    if not bot_token:
        raise TelegramInitDataError("TELEGRAM_BOT_TOKEN не задан в настройках")

    # 1) Парсим query-string в список key-value
    # init_data_raw приходит таким: "query_id=...&user=%7B...%7D&auth_date=...&hash=..."
    # parse_qsl его раскодирует.
    params = dict(parse_qsl(init_data_raw, keep_blank_values=True))

    # Достаём hash, он нам нужен для финального сравнения
    received_hash = params.pop("hash", None)
    if not received_hash:
        raise TelegramInitDataInvalidSignature("Отсутствует параметр 'hash' в initData")

    # 2) Формируем data-check-string: key=value по алфавиту, join с '\n'
    # Важный момент: значения должны быть в именно таком виде, как вернул parse_qsl
    # (то есть уже URL-декодированные).
    data_check_array = []
    for key, value in params.items():
        # user приходит как JSON-строка, уже декодированная ({"id":...})
        data_check_array.append(f"{key}={value}")

    data_check_array.sort()  # сортировка по ключу, так как строка начинается с key=
    data_check_string = "\n".join(data_check_array)  # join с переносами строк

    # 3) HMAC-SHA256 от bot_token с ключом "WebAppData" → секретный ключ
    secret_key = hmac.new(
        key=b"WebAppData",
        msg=bot_token.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()

    # 4) HMAC-SHA256 от data_check_string с ключом → сравниваем с hash
    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    if calculated_hash != received_hash:
        raise TelegramInitDataInvalidSignature("Неверная подпись initData (hash не совпал)")

    # 5) Проверяем срок годности через auth_date
    auth_date = params.get("auth_date")
    if not auth_date:
        raise TelegramInitDataError("Отсутствует auth_date в initData")

    try:
        auth_date = int(auth_date)
    except ValueError:
        raise TelegramInitDataError("auth_date не является числом")

    now = int(time.time())
    if now - auth_date > max_age_seconds:
        raise TelegramInitDataExpired("initData просрочен (auth_date слишком старый)")

    # Если всё ок — возвращаем разобранные параметры
    # user там — JSON-строка, её будем парсить уже в view/serializer
    return params
