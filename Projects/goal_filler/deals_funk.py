import asyncio
import re

from data import *
from google_sheets import GoogleSheetCore
from my_libs import Strategy, AioClient, TaskObject
from private import *
from world import check_project_world

CURRENT_WORLD = check_project_world(KITCHEN1)


class PatchSoloRequester(Strategy):

    def parse(self):
        pass


class EqRequester(Strategy):

    def parse(self):
        id_session = self.get_json.get("id")
        self.get_main_data.set_id_session(id_session)
        self.add_spps()

    def create_dict(self):
        metrics_dict = {
            metric.get("id"): metric.get("name")
            for metric in self.get_json.get("metricsDescription")
        }
        return metrics_dict

    def add_spps(self):
        for spp_data in self.get_json.get("results"):
            ldap_str = spp_data.get("user").get("ldap")  # строка LDAP
            new_spp = SPP(ldap=ldap_str)  # создаём объект SPP
            self.get_main_data.add_spp(new_spp)  # передаём объект в add_spp


class PostCreator:
    """Создает тела для post запросов в зависимости от статуса сотрудника, выходного и прочего"""

    def __init__(self, SSP):  # Принимаем название комбинатора
        self.SPP = SSP

    current_metrics = {
        "Создано сделок": "deals_created_sppo",
        "Конверсия": "conversion_to_payment_sppo",
        "Средний бюджет заверш.": "average_budget_sppo",
        "GMV": "gmv_sppo",
        "Доля сделок с услугой": "penetration_of_services_sppo",
        "SKU": "unique_sku_sppo",
        "Создано лидов в др. от.": "leads_created_sppo",
    }

    def post_creator(self):
        plan_metrics_updates = []
        users_updates = []
        for spp in self.SPP.values():
            ldap = getattr(spp, "ldap", None)
            if not ldap:
                continue

            post_table = getattr(spp, "post_table", {})
            for metric_key, metric_id in self.current_metrics.items():
                if metric_key in post_table:
                    value = post_table[metric_key]
                    if not value:
                        continue
                    digits_only = int(re.sub(r"\D", "", value))
                    if metric_key == "Средний бюджет заверш." or metric_key == "GMV":
                        digits_only /= 1000
                        digits_only = int(digits_only)

                    if value is not None:
                        plan_metrics_updates.append(
                            {
                                "metricId": metric_id,  # это значение из словаря по ключу metric_key
                                "userLdap": ldap,
                                "newValue": digits_only,  # значение из post_table по ключу metric_key
                            }
                        )
            if spp.work_days:
                users_updates.append({"userLdap": ldap, "workingDays": spp.work_days})

        data = {
            "planMetricsUpdates": plan_metrics_updates,
            "usersUpdates": users_updates,
        }
        return data


def spp_point_main_funktion():  # Основная функция

    print("VER 0.4")

    main_client = AioClient(CompositeData)
    main_data = main_client.get_data()

    report_date = main_data.current_month_year.split(".")[0]

    current_month = GoalFillerTime.minus_month(report_date)
    current_rsd_id = CURRENT_WORLD.current_rsd_id

    url_goals = url_goals_get.format(
        current_month=current_month, current_rsd_id=current_rsd_id
    )

    task = TaskObject(url_goals)

    (
        main_client.set_task(task)
        .set_certificate(cert_3)
        .set_headers(headersGoals)
        .set_request_mode(main_client.REQ_MODE_GET_JSON)
        .set_strategy(EqRequester)
    )

    asyncio.run(main_client.main_asynch())

    google_processor = GoogleSheetCore(main_data)
    google_processor.read_table()

    google_processor.open_schedule()
    google_processor.read_table_schedule()

    post_creator = PostCreator(main_data.SPPs)
    data = post_creator.post_creator()

    session_id = main_data.id_session

    url_patch_to_service_witch_session = url_patch_to_service.format(
        session_id=session_id
    )

    task = TaskObject(url_patch_to_service_witch_session, data)

    (
        main_client.set_task(task)
        .set_request_mode(main_client.REQ_MODE_PATCH)
        .set_strategy(PatchSoloRequester)
    )

    asyncio.run(main_client.main_asynch())
