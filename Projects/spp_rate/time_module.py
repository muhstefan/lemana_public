from datetime import datetime, timedelta, date

from my_libs import TimeHelper


class SppRateTime(TimeHelper):

    yesterday_date = (datetime.now() - timedelta(days=1)).date()
    yesterday = yesterday_date.strftime("%Y-%m-%d")
    yesterday_as_letters = yesterday_date.strftime("%A").upper()

    @staticmethod
    def get_russian_month():
        month_of_yest_day = datetime.now() - timedelta(days=1)
        month_name_ru = TimeHelper.russian_months[month_of_yest_day.month - 1]
        return month_name_ru

    @classmethod
    def delta_in_minutes(cls, time1, time2):
        """Разница между временами в минутах"""
        time1 = cls.parse_time_return_dt(time1)
        time2 = cls.parse_time_return_dt(time2)
        return int((time1 - time2).total_seconds() / 60)

    @classmethod
    def check_time_before_may_2025(cls, time):
        # Парсим входное время
        parsed_time = cls.parse_time_return_dt(time)
        parsed_time = parsed_time.date()
        may_first_2025 = date(year=2025, month=5, day=1)

        # Если переданное время раньше 1 мая 2025 — возвращаем время, иначе True
        if parsed_time < may_first_2025:
            return True
        else:
            return False
