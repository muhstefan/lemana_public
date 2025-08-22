import gspread
from data import GoalFillerTime
from google.oauth2.service_account import Credentials
from private import credentials, SCOPES


class GoogleSheetCore:
    world_names = [
        "кухни",
        "хранение",
        "столярные изделия",
        "стройка",
        "ванные",
        "конец",
    ]

    def __init__(self, main_data):

        credentials_new = Credentials.from_service_account_info(
            credentials, scopes=SCOPES
        )
        gc = gspread.authorize(credentials_new)

        self.worksheet = gc.open("ОДП: Цели и досье СППО").worksheet(
            f"Цели ОДП {GoalFillerTime.year_str}"
        )
        self.all_data = self.worksheet.get_all_values()
        self.headers = self.all_data[4]
        self.ldap_place = None
        self.ldap_place_schedule = None
        self.work_days_indexes_schedule = None
        self.main_data = main_data
        self.current_month_year = main_data.current_month_year
        self.ldap_sets = main_data.get_ldap_set()
        self.kpi_dict = {
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

    def open_schedule(self):
        credentials_new = Credentials.from_service_account_info(
            credentials, scopes=SCOPES
        )
        gc = gspread.authorize(credentials_new)
        month_digit = self.current_month_year.split(".")
        GoalFillerTime.init_values(month_digit[0])
        self.worksheet = gc.open("График СППО 2025").worksheet(
            f"{GoalFillerTime.month_check} 20{month_digit[1]}"
        )
        self.all_data = self.worksheet.get_all_values()

    @staticmethod
    def find_column_index_schedule(row, find_word):
        for i, cell in enumerate(row):
            if find_word in cell.lower():
                return i
        return None

    def read_table_schedule(self):
        for row in self.all_data:
            if "ldap" in row or "LDAP" in row:
                self.ldap_place_schedule = GoogleSheetCore.find_column_index_schedule(
                    row, "ldap"
                )
                continue
            if "раб дни" in row:
                self.work_days_indexes_schedule = (
                    GoogleSheetCore.find_column_index_schedule(row, "раб дни")
                )
                continue
        if self.work_days_indexes_schedule is None and self.ldap_place_schedule is None:
            raise ValueError(
                "не нашли лдап и кол-во дней в расписании read_table_schedule"
            )
        for row in self.all_data:
            self.check_spp_schedule(row)

    def check_spp_schedule(self, row):
        ldap = row[self.ldap_place_schedule]
        check = ldap.isdigit()
        check_2 = ldap.isalpha()
        if check and not check_2 and ldap in self.ldap_sets:
            self.main_data.get_spp(ldap).work_days = int(
                row[self.work_days_indexes_schedule]
            )

    def find_ldap(self):
        for idx, header in enumerate(self.headers):
            if "LDAP" in header:
                self.ldap_place = idx
                return
        raise ValueError("Столбец с 'LDAP' не найден в 5-й строке")

    def read_table(self):
        self.find_ldap()
        self.find_kpi_date_indices()
        self.check_spps()
        # Читаем лдапы если есть пересечение с нашими применяем функцию считывания к ней.

    def check_spps(self):
        column_values = [row[self.ldap_place] for row in self.all_data]
        for idx, ldap in enumerate(column_values):
            if ldap in self.ldap_sets:
                self.read_spp(idx=idx, ldap=ldap)

    def read_spp(self, idx, ldap):
        row = self.all_data[idx]
        spp_obj = self.main_data.get_spp(ldap)

        for kpi, col_index in self.kpi_dict.items():
            if col_index is not None and col_index < len(row):
                value = row[col_index]
            else:
                value = None
            spp_obj.post_table[kpi] = value

    def find_kpi_date_indices(self):
        current_kpi = None
        for idx, cell in enumerate(self.headers):
            if not cell:
                continue

            for kpi_key in self.kpi_dict.keys():
                # Если индекс уже записан — пропускаем этот KPI
                if self.kpi_dict[kpi_key] is not None:
                    continue

                if kpi_key in cell:
                    current_kpi = kpi_key
                    break

            if current_kpi is not None and cell == self.current_month_year:
                self.kpi_dict[current_kpi] = idx
                current_kpi = None
