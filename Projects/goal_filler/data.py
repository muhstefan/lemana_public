import sys
from datetime import datetime
import calendar
from my_libs import TimeHelper, SingletonMeta

version = 0.985


class GoalFillerTime(TimeHelper):
    """Класс позволяющий работать со временем"""

    now = datetime.now()
    year = now.year
    year_str = str(now.year)

    month_check = None
    month = None
    num_days = None  # Количество дней в месяце

    @staticmethod
    def init_values(month_digit):

        if 1 <= int(month_digit) <= 12:
            month_name_ru = TimeHelper.russian_months[int(month_digit) - 1]
            GoalFillerTime.month_check = month_name_ru
            GoalFillerTime.month = (
                TimeHelper.russian_months.index(GoalFillerTime.month_check) + 1
            )
            GoalFillerTime.num_days = calendar.monthrange(
                GoalFillerTime.year, GoalFillerTime.month
            )[1]
        else:
            pass

    @staticmethod
    def get_current_month_year():
        try:
            input_data = input("дата месяца в формате 00.00   (05.25) ")
            month, year = input_data.split(".")
            if 1 <= int(month) <= 12 and 20 <= int(year) <= 90:
                input(
                    f"Вы выбрали {input_data} \nНажмите ENTER если ГОТОВЫ ПРОДОЛЖИТЬ\n"
                )
                return input_data  # Возвращается числовое название месяца
        except:
            print("Ошибка: введено не число. Программа завершена.")
            input("Нажмите ENTER для выхода...")
            sys.exit()

    @staticmethod
    def minus_month(edit_month: str):
        correct_month = int(edit_month) - 1
        return str(correct_month)


class SPP:
    def __init__(self, ldap):
        self.ldap = ldap
        self.work_days = None
        self.post_table = {
            "GMV": None,
            "Создано сделок": None,
            "Конверсия": None,
            "SKU": None,
            "Средний бюджет заверш.": None,
            "Доля сделок с услугой": None,
            "GMV услуг": None,
            "GMV 3P": None,
            "Создано лидов в др. от.": None,
            "Доля сделок с КЛ": None,
            "Отменено сделок": None,
        }


class CompositeData(metaclass=SingletonMeta):
    def __init__(self):
        self.id_session = None
        self.SPPs = {}
        self.blackout_id = []
        self.delete_spp = None
        self.current_month_year = GoalFillerTime.get_current_month_year()

    def set_id_session(self, id_session):
        self.id_session = id_session

    def get_ldap_set(self):
        return {spp.ldap for spp in self.SPPs.values()}

    def add_spp(self, spp):
        self.SPPs[spp.ldap] = spp

    def add_blackout_id(self, bl_id):
        self.blackout_id.append(bl_id)

    def get_spp_list(self):
        return self.SPPs

    def get_spp(self, ldap):
        for spp in self.SPPs:
            if spp == ldap:
                return self.SPPs[ldap]
        return None
