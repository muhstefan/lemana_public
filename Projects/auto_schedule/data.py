import calendar
import sys
from datetime import datetime, timedelta


from my_libs import SingletonMeta, TimeHelper


version = 1.0


class AutoScheduleTime(TimeHelper):
    """Класс позволяющий работать со временем"""

    now = datetime.now()  # Получаем текущую дату
    year = now.year
    month_ru = None  # month_check
    month_int = None
    num_days = None  # Количество дней в месяце

    @staticmethod
    def get_all_days(month_cur, start_day=1, end_day=None):
        now_ = datetime.now()
        year_cur = now_.year
        _, num_days_ = calendar.monthrange(year_cur, month_cur)

        end_day = min(end_day or num_days_, num_days_)  # Корректируем end_day
        start_day = max(start_day, 1)  # Корректируем start_day

        if end_day < start_day:
            return []  # пустой список, если интервал некорректен

        start_date = datetime(year_cur, month_cur, start_day)
        return [
            (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range(end_day - start_day + 1)
        ]

    @staticmethod
    def create_key_data(key):
        first_part = f"{AutoScheduleTime.year}-{AutoScheduleTime.month_int:02d}"
        return f"{first_part}-{key}"

    @staticmethod
    def delta_time_hours(hour, delta_hour):
        delta = timedelta(hours=delta_hour)
        hour_dt = datetime.strptime(hour, "%H:%M") + delta
        need_date = hour_dt.strftime("%H:%M")
        return need_date

    @staticmethod
    def create_need_time(day, hour, start=False):
        delta = timedelta(hours=3, seconds=1)
        if start:
            delta = timedelta(hours=3)
        hour_dt = datetime.strptime(hour, "%H:%M") - delta
        hour_dt_full = hour_dt.strftime("%H:%M:%S")
        need_date = f"{day}T{hour_dt_full}.000Z"
        return need_date

    @staticmethod
    def minus_day(time):
        input_datetime = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%fZ")
        previous_day_datetime = input_datetime - timedelta(days=1)
        output_str = previous_day_datetime.strftime("%Y-%m-%d")
        return output_str

    @staticmethod
    def get_russian_month():
        try:
            current_month = int(
                input("На какой месяц делаем расписание? \nцифра месяца 1-12\n")
            )
            if 1 <= current_month <= 12:
                month_name_ru = AutoScheduleTime.russian_months[current_month - 1]
                input(
                    f"Вы выбрали месяц {month_name_ru} \nНажмите ENTER если ГОТОВЫ ПРОДОЛЖИТЬ\n"
                )
                return month_name_ru
        except:
            print("Ошибка: введено не число. Программа завершена.")
            input("Нажмите ENTER для выхода...")
            sys.exit()

    @staticmethod
    def init_values():

        AutoScheduleTime.month_ru = AutoScheduleTime.get_russian_month()
        AutoScheduleTime.month_int = (
            AutoScheduleTime.russian_months.index(AutoScheduleTime.month_ru) + 1
        )
        AutoScheduleTime.num_days = calendar.monthrange(
            AutoScheduleTime.year, AutoScheduleTime.month_int
        )[1]

    @staticmethod
    def get_year():
        return datetime.now().year


class SPP:
    def __init__(self, ldap, name, id_in):
        self.ldap = ldap
        self.name = name
        self.id_in = id_in
        self.schedule = None
        self.post_data = None
        self.status = None

    @staticmethod
    def create_month():
        schedule = {}
        for day in range(1, AutoScheduleTime.num_days + 1):
            day_str = f"{day:02d}"  # форматируем число с ведущим нулём
            schedule[day_str] = []
        return schedule


class CompositeData(metaclass=SingletonMeta):
    def __init__(self):
        self.SPPs = {}  # Словарь спп у которых в свою очередь (ldap, имя, начало дня)
        self.blackout_id = []
        self.delete_spp = None

    # Множество реализовано по принципу хэш таблицы, поэтому быстрее
    def get_ldap_set(self):
        return {spp.ldap for spp in self.SPPs.values()}

    def return_all_posts(self):
        all_posts = []
        for spp in self.SPPs.values():
            if spp.post_data:
                for posts_list in spp.post_data.values():
                    all_posts.extend(posts_list)
        return all_posts

    def add_spp(self, spp):
        self.SPPs[spp.ldap] = spp

    def add_blackout_id(self, bl_id):
        self.blackout_id.append(bl_id)

    def get_spp_list(self):
        return self.SPPs

    def get_name_by_id(self, id_in):
        for spp in self.SPPs.values():
            if spp.id_in == id_in:
                return spp.name
        raise Exception(f"Не найден спп по id {id_in}")

    def get_spp(self, ldap):
        for spp in self.SPPs:
            if spp == ldap:
                return self.SPPs[ldap]
        return None


instruction = """Введи запрос
при выборе режима у тебя есть 6 опции:

очистка - полностью очистить за определенный месяц расписание. Пример - (очистка)

создание - полностью заполнить за месяц расписание. Пример(создание)

очистка  лдап дата1 дата 2. Пример - (очистка 6018582 24 26)
очистить определенного спп за несколько дней , для выбора 1-го дня просто пишешь 2 раза (очистка 6018582 24 24)

создание лдап дата1 дата 2. Пример -  (создание 6018582 24 26)
тоже самое только заполняем интервал на спп

очистка дата1 дата 2  . Пример - (очистка 24 26)
очистить ВСЕХ спп в интервале

создание дата1 дата 2 . Пример - (создание 24 26)
"""
