from datetime import datetime

import pytz
from dateutil.parser import parse as parse_date

from my_libs.composite_data_base import SingletonMeta


script_spp_base = """
"host" === Добрый день, вы записаны на проект {ProjectWorld}, подскажите актуальна ли запись?

"актуальность" === Добрый день!) Подскажите что решили по проекту? Как по срокам?

"сборка" === Добрый день!) У вас была сборка кухни, подскажите как все прошло?
"""


class TimeHelper:
    """Класс позволяющий работать со временем"""

    def __init__(self, time):
        self._time = parse_date(time)

    def get_data(self):
        return self._convert_timezone()

    # Нет смысла приводить к МСК, т.к это разница, она одинаковая всегда
    def delta_in_minutes(self, second_time):
        time = self._convert_timezone()
        time2 = TimeHelper(second_time)._convert_timezone()
        delta = time - time2
        difference_in_minutes = delta.total_seconds() / 60
        return int(difference_in_minutes)

    # Сюда уже приходит правильное время потому, что в URL запросе есть time_zone
    def one_hour_convert(self):
        formatted_time = self._time.strftime("%H")
        return int(formatted_time)

    def datetime_to_str(self, dig):
        # strftime dt -> str
        # strptime str -> dt
        self._time = self._convert_timezone()

        time_format = None
        if dig == 3:
            time_format = "%H-%M-%S"
        if dig == 5:
            time_format = "%Y-%m-%d-%H-%M"

        if isinstance(self._time, datetime):
            return self._time.strftime(time_format)


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


class Task:
    def __init__(self, title, deal_id, phone):
        self.title = title
        self.deal_id = deal_id
        self.phone = phone
        self.status = None
        self.type = None

    def __repr__(self):
        return f"{self.title}-{self.deal_id}"


class CompositeData(metaclass=SingletonMeta):
    def __init__(self):
        self.tasks = []
        self.ldap = None
        self.request_verification_token = None
        self.messages = None
        self.schedule = None
        self.tasks_types = {
            "актуальность": None,
            "проверить замер": None,
            "проверить заказ": None,
            "посмотреть ответ": None,
            "как прошла сборка": None,
            "host": None,
        }

    def set_request_verification_token(self, request_verification_token):
        self.request_verification_token = request_verification_token

    def add_task(self, task):
        self.tasks.append(task)
