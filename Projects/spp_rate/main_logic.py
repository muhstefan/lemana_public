import asyncio

from data import Action, CompositeData
from exel import ExelEngine
from google_sheets import GoogleSheetCore
from my_libs import Strategy, AioClient, TaskObject
from private import cert_1, cert_2, headersDeals, headersEQ
from time_module import SppRateTime
from world import *

version = 1.7


class EqRequester(Strategy):

    def parse(self):
        self._all_spp()

    @classmethod
    def spp_check(cls, resource):
        if (
            resource.get("appointments") or resource.get("isActive") is True
        ):  # если есть заявки
            return True
        return False

    def _take_client_on_time(self, resource):
        ldap = resource.get("ldap")
        for client in resource.get("appointments", []):

            status = client.get("status")
            planned_start = client.get("plannedStartedAt")
            start = client.get("startedAt").replace(
                "Z", "+03:00"
            )  # Т.к у нас НЕВЕРОНОЕ UTC ВРЕМЯ ТУТ...
            difference_in_minutes = SppRateTime.delta_in_minutes(start, planned_start)
            planned_start = SppRateTime.parse_time_return_str(
                planned_start, "%Y-%m-%d-%H-%M"
            )

            if status != "done":
                new_action = Action("Unclosed ticket", ldap, planned_start)
                self.get_main_data.add_action(new_action)
                continue

            if difference_in_minutes > 5:
                new_action = Action("Late pickup", ldap, planned_start)
                self.get_main_data.add_action(new_action)
                continue

    # Делаем все тоже что и в процессорах. Как будто, получаем доступ к данным
    def _all_spp(self):
        for resource in self.get_json.get("resources", []):
            # Критерии добавления спп в зависимости от пр. мира
            if self.spp_check(resource):
                self._take_client_on_time(resource)

    @staticmethod
    def _find_time_slot(resource):
        for slot in resource["timeSlots"]:
            if slot["dayOfWeek"] == SppRateTime.yesterday_as_letters:

                return (
                    int(SppRateTime.format_time_convert_moskow(slot["start"], "%H")),
                    int(SppRateTime.format_time_convert_moskow(slot["end"], "%H")),
                )
        return 8  # Дефолтное время


# список сделок смотрит и сопоставляет чтобы там были вчерашние
class DealsList(Strategy):

    def parse(self):
        self._get_parsed_data()

    def _get_parsed_data(self):  # Все сделки 1 спп
        for one_deal in self.get_json.get("content", []):
            deal_id = one_deal.get("id")
            deal_update_time = SppRateTime.parse_time_return_date(
                one_deal.get("updatedDate")
            )
            # если эт сделки не вчерашние-то не нужны нам
            if deal_update_time < SppRateTime.yesterday_date:
                continue
            self.get_main_data.add_deal(deal_id)


# список сделок смотрит и сопоставляет чтобы там были вчерашние
class ActionList(Strategy):

    def _set_type_dict(self):
        self.type_dictionary = self.get_main_data.project_world.get_type_dictionary()

    def parse(self):
        self._set_type_dict()
        if self._deal_is_cancelled():
            return
        self._get_parsed_data(self.get_json, "relatedObjects")
        self._get_parsed_data(self.get_json, "comments")

    # Если статус сделки отменена, то смотрим только отмены и двигаемся дальше.
    def _deal_is_cancelled(self):
        if self.get_json.get("history") is None:
            return True
        for resource in self.get_json.get("history"):
            # Смотрим действия в сделке ищем отмены для подсчета
            if resource.get("type") == "ADD_REASON_TO_CANCEL":
                self._action_builder(resource)
        # Если отменена выходим вообще
        if self.get_json.get("processStatus") == "CANCELLED":
            return True
        return False

    def _get_parsed_data(self, json, container_label):
        for resource in json.get(container_label, []):
            self._action_builder(resource)

    def _action_builder(self, data):  # и он будет по типу сопоставлять

        if data.get("commentId") is not None:
            type_action = "COMMENT"
        else:
            type_action = data.get("type")

        status = data.get("status")

        if status == "COMPLETELY_CANCELED" or status == "CANCELLED":
            return
        # если нет прописанных значений для него выходим.
        if type_action not in self.type_dictionary:
            return

        if type_action == "USER_TASK" and status == "COMPLETED":
            type_action = "COMPLETED_TASK"

        self._create_action(data, type_action)

        if type_action == "CONFIGURATION":
            type_action = "PROJECT_EDIT"
            self._create_action(data, type_action)

    def _create_action(self, data, type_action):

        dictionary_fields = self.type_dictionary[type_action]
        ldap_str = self._get_data_from_path(data, dictionary_fields[1])
        action_creating_time = data.get(dictionary_fields[0])
        if (
            ldap_str is None
            or ldap_str == "Tunnel"
            or action_creating_time is None
            or ldap_str == "LK"
            or ldap_str == "PRESALE_SYSTEM"
        ):
            return
        time = self._date_check(action_creating_time, type_action)

        if not time:
            return
        ldap = int(ldap_str)
        # Создаем и добавляем действие
        new_action = Action(type_action, ldap, time)
        self.get_main_data.add_action(new_action)

    def _date_check(self, action_creating_time, type_action):

        test_check = SppRateTime.format_time_convert_moskow(
            action_creating_time, "%Y-%m-%d"
        )  # Шаблон для проверки
        time = SppRateTime.format_time_convert_moskow(
            action_creating_time, "%Y-%m-%d-%H-%M"
        )

        if test_check != SppRateTime.yesterday:  # фильтруем по времени и лдапу
            return None

        if type_action == "PROJECT_EDIT" or self.get_main_data.last_action_time == time:
            return None

        return time


class SppPointer:
    def __init__(self, main_data):
        self.main_data = main_data

    def activate(self):
        for action in self.main_data.get_actions():
            self._spp_point(action)

    def _spp_point(self, action):
        if action.ldap in self.main_data.get_ldap_set():
            matching_spp = self.main_data.SPPs[action.ldap]
            hour_act = int(action.time.split("-")[3])

            for key, values in self.main_data.project_world.spp_rate_logic.items():
                if action.type_action in values:
                    matching_spp.points += self.main_data.project_world.spp_rate_points[
                        key
                    ]
                    matching_spp.actions_stat[key] += 1
                    matching_spp.time_stat[hour_act][key] += 1


def loading(count):
    for symbol in range(count):
        sys.stdout.write("#")  # Печатаем символ
        sys.stdout.flush()  # Обновляем вывод


def spp_point_main_funktion():  # Основная функция
    main_data = CompositeData()
    # Создаем наш текстовый если его не было закрываем программу
    print(f"ОТЧЕТ {version} {main_data.project_world.world_name}")

    main_exel_book = ExelEngine(main_data.project_world)
    main_exel_book.excel_check()

    main_client = AioClient(CompositeData)
    main_data = main_client.get_data()
    GoogleSheetCore(main_data, main_data.project_world).read_table()


    task = TaskObject(main_data.project_world.get_url_eq())

    (
        main_client.set_task(task)
        .set_certificate(cert_1)
        .set_headers(headersEQ)
        .set_request_mode(main_client.REQ_MODE_GET_JSON)
        .set_strategy(EqRequester)
    )

    asyncio.run(main_client.main_asynch())

    loading(2)

    tasks = main_client.create_tasks_from_number_list(
        main_data.get_ldap_set(),
        lambda ldap: main_data.project_world.get_url_deals_spp_list().format(ldap=ldap),
    )

    (
        main_client.set_tasks(tasks)
        .set_headers(headersDeals)
        .set_strategy(DealsList)
        .set_certificate(cert_2)
    )

    asyncio.run(main_client.main_asynch())

    loading(10)

    tasks = main_client.create_tasks_from_number_list(
        main_data.get_deals(),
        lambda project_id: main_data.project_world.get_url_deal_information().format(
            projectId=project_id
        ),
    )

    main_client.set_tasks(tasks).set_strategy(ActionList)

    asyncio.run(main_client.main_asynch())

    loading(10)

    spp_pointer = SppPointer(main_data)
    spp_pointer.activate()

    loading(3)

    main_exel_book.set_spp_list(main_data.get_spp_list())
    main_exel_book.activate()
