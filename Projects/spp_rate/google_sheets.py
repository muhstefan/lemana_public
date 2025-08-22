import re
import gspread
from world import *
from google.oauth2.service_account import Credentials
from private import credentials, SCOPES
from time_module import SppRateTime

current_month = SppRateTime.get_russian_month()


class GoogleSheetCore:
    world_names = [
        "кухни",
        "хранение",
        "столярные изделия",
        "стройка",
        "ванные",
        "конец",
    ]

    def __init__(self, main_data, main_world):

        credentials_new = Credentials.from_service_account_info(
            credentials, scopes=SCOPES
        )
        gc = gspread.authorize(credentials_new)

        self.worksheet = gc.open("График СППО 2025").worksheet(
            f"{current_month} {SppRateTime.get_current_time("%Y")}"
        )
        self.all_data = self.worksheet.get_all_values()
        self.world_name_place = None
        self.ldap_place = None
        self.spp_name_place = None
        self.need_time_column = None
        self.current_world = None
        self.main_world = main_world
        self.current_row = None
        self.main_data = main_data

    def find_indexes(self, data):
        for index, thing in enumerate(data):
            if thing:
                if "ldap" in thing.lower():
                    self.ldap_place = index
                    continue
                if current_month.lower() in thing.lower():
                    self.world_name_place = index
                    continue
                if "фамилия" in thing.lower() or "фио" in thing.lower():
                    self.spp_name_place = index
                    continue

    def check_world(self):
        for name in self.world_names:
            if name.lower() in self.current_row[self.world_name_place].lower():
                self.current_world = name
                return 1

    @staticmethod
    def is_valid_time_pair(time_str):
        pattern = r"^([01]?[0-9]|2[0-3]):00\s*\n?\s*([01]?[0-9]|2[0-3]):00$"
        return bool(re.fullmatch(pattern, time_str))

    def find_indexes_exepts(self):
        if not self.ldap_place:
            raise AttributeError("Не найден LDAP в заголовке!!!")
        elif not self.world_name_place:
            raise AttributeError("Не найден world_name_place в заголовке!!!")
        elif not self.spp_name_place:
            raise AttributeError("Не найден ФИО в заголовке!!!")

    def check_spp(self):

        ldap = self.current_row[self.ldap_place]
        name = self.current_row[self.spp_name_place]
        check = ldap.isdigit()
        check_2 = ldap.isalpha()
        times = self.current_row[self.need_time_column]
        if (
            check
            and not check_2
            and self.current_world.lower() == self.main_world.world_name
            and self.is_valid_time_pair(times)
        ):
            times = times.split()
            day_begin = SppRateTime.parse_time_return_str(times[0], "%H")
            day_end = SppRateTime.parse_time_return_str(times[1], "%H")
            new_spp = SPP(
                ldap=int(ldap),
                name=name,
                day_begin=int(day_begin),
                project_world=self.main_world,
                day_end=int(day_end),
            )
            self.main_data.add_spp(new_spp)

    def find_date(self, index):
        need_row = index + 2
        for i, world in enumerate(self.all_data[need_row]):
            if (
                SppRateTime.parse_time_return_str(SppRateTime.yesterday_date, "%d")
                in world
            ):
                self.need_time_column = i
                break

    def read_table(self):
        for i, row in enumerate(self.all_data):
            if "ldap" in row or "LDAP" in row:
                self.find_indexes(row)
                self.find_indexes_exepts()
                self.find_date(i)
                break
        for row in self.all_data:
            self.current_row = row
            if self.check_world() is None:
                self.check_spp()
