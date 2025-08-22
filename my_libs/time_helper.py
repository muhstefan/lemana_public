from datetime import datetime
from dateutil.parser import parse as parse
from dateutil import tz


class TimeHelper:
    """Класс для работы со временем с конвертацией в московский пояс"""

    russian_months = [
        "Январь",
        "Февраль",
        "Март",
        "Апрель",
        "Май",
        "Июнь",
        "Июль",
        "Август",
        "Сентябрь",
        "Октябрь",
        "Ноябрь",
        "Декабрь",
    ]

    @staticmethod
    def parse_time_return_dt(time):
        """Парсит время из строки или возвращает datetime"""
        return parse(time) if isinstance(time, str) else time

    @staticmethod
    def parse_time_return_date(time):
        """Парсит время из строки или возвращает date (без времени)"""
        if isinstance(time, str):
            return parse(time).date()  # Преобразует строку в datetime и берёт дату
        elif hasattr(time, "date"):  # Если это datetime или date
            return time.date()  # Возвращает дату
        return time  # Если это уже date или другой тип (на усмотрение)

    @staticmethod
    def parse_time_return_str(time, format_str="%Y-%m-%d%"):
        """Парсит время из строки или возвращает форматированную str"""
        time = TimeHelper.parse_time_return_dt(time)
        return time.strftime(format_str)

    @staticmethod
    def convert_timezone(time, target_tz="Europe/Moscow"):
        """Конвертирует время в указанный часовой пояс"""
        time = parse(time)
        if time.tzinfo is None:
            time = time.replace(tzinfo=tz.UTC)
        return time.astimezone(tz.gettz(target_tz))

    @staticmethod
    def get_current_time(format_str="%Y-%m-%d%H:%M:%S"):
        """Текущее время в Москве в заданном формате"""
        return datetime.now(tz.gettz("Europe/Moscow")).strftime(format_str)

    @staticmethod
    def format_time_convert_moskow(time, format_str="%H:%M"):
        """Форматирует время (в московском поясе)"""
        return TimeHelper.convert_timezone(time).strftime(format_str)
