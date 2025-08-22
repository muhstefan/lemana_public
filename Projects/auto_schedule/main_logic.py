import asyncio
import copy

from my_libs import AioClient, TaskObject, Strategy
from my_libs import Logger
from data import *
from google_sheets import GoogleSheetCore
from private import *
from world import *

# Текущий проектный мир (в зависимости от мира меняются правила составления расписания)
main_world = check_project_world(KITCHEN)


log = Logger()


class PostRequester(Strategy):

    type_comparison = {
        "TRAINING": "ПЕРЕКРЫТЬ",
        "LUNCH": "ОБЕД",
        "TASK_HANDLING": "АКТИВНОСТЬ",
        "VACATION": "ВЫХОДНОЙ/ОТПУСК",
    }

    def parse(self):
        if self.get_status == 200:
            pass
        else:
            d = self.get_post_data
            current_spp_id = self.get_post_data["resourceId"]
            current_spp = self.get_main_data.get_name_by_id(current_spp_id)
            log.warning(f"У {current_spp} не вышло сделать запрос {self.get_post_data}")


class PassREQ(Strategy):

    def parse(self):
        pass


class EqDelRequester(Strategy):

    def parse(self):
        self._all_spp()

    def _all_spp(self):
        # Получаем значение delete_spp
        delete_spp = self.get_main_data.delete_spp
        for resource in self.get_json.get("resources", []):
            ldap = resource.get("ldap")
            # Если delete_spp задан, обрабатываем только совпадающие ldap
            if delete_spp and ldap != delete_spp:
                continue  # пропускаем ресурс, если ldap не совпадает
            if resource.get("blackouts"):
                for blackout in resource.get("blackouts"):
                    blackout_id = blackout.get("id")
                    self.get_main_data.add_blackout_id(blackout_id)


class EqRequester(Strategy):

    def parse(self):
        self._all_spp()

    # Делаем все тоже что и в процессорах. Как будто, получаем доступ к данным
    def _all_spp(self):
        for resource in self.get_json.get("resources", []):
            self._add_spp(resource)

    def _add_spp(self, resource):
        spp_ldap = resource.get("ldap")
        spp_id = resource.get("id")
        name = resource.get("title")
        self.get_main_data.add_spp(SPP(ldap=spp_ldap, name=name, id_in=spp_id))


class PostCreator:
    """Создает тела для post запросов в зависимости от статуса сотрудника, выходного и прочего"""

    def __init__(self, main_data):  # Принимаем название комбинатора
        self.main_data = main_data
        self.response = None

    hour_min = main_world.hour_min
    hour_max = main_world.hour_max

    hour_vocation_start = "00:00"

    post_template = {
        "resourceId": None,
        "type": "TRAINING",  #  LUNCH   \    TASK_HANDLING
        "capacity": 1,
        "startedAt": None,
        "finishedAt": None,  # Format : 2025-06-27T15:59:59.000Z
    }

    def activate(self):
        for spp in self.main_data.SPPs.values():
            if spp.post_data:  # Если вообще расписание есть и статус сменный
                self._create_post_data_for_spp(spp)

    def _create_post_data_for_spp(self, spp):  # ОПТИМИЗИРОВАТЬ
        if "игнор" in spp.status.lower():
            return

        for key, time in spp.post_data.items():
            post_pack = []

            key_date = AutoScheduleTime.create_key_data(key)

            if len(time) > 1:

                # Создаем обеды и активности

                lunch_hour_start = AutoScheduleTime.delta_time_hours(
                    time[0], main_world.break_1
                )  # время перерывов
                lunch_hour_end = AutoScheduleTime.delta_time_hours(lunch_hour_start, 1)
                break_hour_start = AutoScheduleTime.delta_time_hours(
                    lunch_hour_start, main_world.break_2
                )
                break_hour_end = AutoScheduleTime.delta_time_hours(break_hour_start, 1)

                post_br_1 = self.create_post(
                    "TASK_HANDLING", spp, lunch_hour_start, lunch_hour_end, key_date
                )
                post_br_2 = self.create_post(
                    "LUNCH", spp, break_hour_start, break_hour_end, key_date
                )
                post_pack.append(post_br_1)
                post_pack.append(post_br_2)

                # Создаем перекрытия для сменных
                if "сменный" in spp.status.lower():

                    time_min = AutoScheduleTime.create_need_time(
                        key_date, PostCreator.hour_min, start=True
                    )  # создаю валидную строку времени запроса
                    time_end = AutoScheduleTime.create_need_time(
                        key_date, time[1], start=True
                    )

                    # проверяю что границы не совпали(если совпали запрос не нужен)
                    if time_min != AutoScheduleTime.create_need_time(
                        key_date, time[0], start=True
                    ):
                        post_1 = self.create_post(
                            "TRAINING", spp, PostCreator.hour_min, time[0], key_date
                        )
                        post_pack.append(post_1)
                    if time_end != AutoScheduleTime.create_need_time(
                        key_date, PostCreator.hour_max, start=True
                    ):
                        post_2 = self.create_post(
                            "TRAINING", spp, time[1], PostCreator.hour_max, key_date
                        )
                        post_pack.append(post_2)

                # Работа с доп линией.
                if "(д)" in spp.status.lower():
                    pass

                spp.post_data[key] = []
                spp.post_data[key].extend(post_pack)

            else:  # Чтобы обработать не время (В \ от \ ДВ \ б)
                if (
                    time[0].lower() == "от"
                    or time[0].lower() == "дв"
                    or time[0].lower() == "б"
                    or "бэо" in time[0].lower()
                    or "сменный плавающий" in spp.status.lower()
                    and time[0].lower() == "в"
                ):
                    time_min = AutoScheduleTime.create_need_time(
                        key_date, PostCreator.hour_vocation_start, start=True
                    )
                    key2_date = AutoScheduleTime.minus_day(time_min)
                    post_1 = self.create_post(
                        "VACATION",
                        spp,
                        PostCreator.hour_vocation_start,
                        PostCreator.hour_vocation_start,
                        key2_date,
                        key_date,
                    )
                    spp.post_data[key] = [post_1]
                else:
                    spp.post_data[key] = []

    @staticmethod
    def copy_template():
        return copy.deepcopy(PostCreator.post_template)

    @staticmethod
    def create_post(type_blackout, spp, time_start, time_end, key, key2=None):
        time_start_format = AutoScheduleTime.create_need_time(
            key, time_start, start=True
        )
        key_for_time_end = (
            key2 if key2 is not None else key
        )  # Возможность передать 2й ключ
        time_end_format = AutoScheduleTime.create_need_time(key_for_time_end, time_end)
        new_dict = copy.deepcopy(PostCreator.post_template)
        new_dict["type"] = type_blackout
        new_dict["resourceId"] = spp.id_in
        new_dict["startedAt"] = time_start_format
        new_dict["finishedAt"] = time_end_format
        return new_dict


class AutoSchedule:

    def __init__(self, main_client: AioClient):
        self.main_client = main_client
        self.main_data = main_client.get_data()

    def start_auto_schedule(self, mode):

        custom_mode = self._split_mode(mode)

        mode = custom_mode["mode"]
        ldap = custom_mode["ldap"]
        start = custom_mode["start"]
        end = custom_mode["end"]

        if mode == "создание":
            self._create_schedule_mode(ldap=ldap, start=start, end=end)
        elif mode == "очистка":
            self._delete_schedule_mode(ldap=ldap, start=start, end=end)
        else:
            raise Exception(f"Unknown mode {mode}")

    def _create_schedule_mode(self, ldap=None, start=None, end=None):

        task = TaskObject(main_world.url_eq_get)

        (
            self.main_client.set_task(task)
            .set_certificate(cert_1)
            .set_headers(headersEQ)
            .set_strategy(EqRequester)
            .set_request_mode(self.main_client.REQ_MODE_GET_JSON)
        )

        asyncio.run(self.main_client.main_asynch())

        GoogleSheetCore(self.main_data).read_table()
        poster_maker = PostCreator(self.main_data)
        poster_maker.activate()

        self._filter_spps()

        if ldap:
            self._request_certain_spp(ldap, start, end)
        elif start and end:
            self._request_all_by_date(start, end)

        tasks = self.prepare_post_tasks()

        (
            self.main_client.set_headers(post_bl_headers)
            .set_request_mode(self.main_client.REQ_MODE_POST)
            .set_tasks(tasks)
            .set_strategy(PostRequester)
        )

        asyncio.run(self.main_client.main_asynch())

    def _delete_schedule_mode(self, ldap=None, start=1, end=None):

        day_of_month_modifications = AutoScheduleTime.get_all_days(
            AutoScheduleTime.month_int, start, end
        )
        data = self.main_data
        self._select_spp_for_clearing(data, ldap)

        tasks = self.main_client.create_tasks_from_number_list(
            day_of_month_modifications,
            lambda day: main_world.url_eq_group_get.format(date=day),
        )

        (
            self.main_client.set_tasks(tasks)
            .set_certificate(cert_1)
            .set_headers(headersEQ)
            .set_strategy(EqDelRequester)
            .set_request_mode(self.main_client.REQ_MODE_GET_JSON)
        )

        asyncio.run(self.main_client.main_asynch())

        ids = self.main_data.blackout_id

        tasks = self.main_client.create_tasks_from_number_list(
            ids,
            lambda deal_id: delete_blackout.format(id=deal_id),
        )

        (
            self.main_client.set_tasks(tasks)
            .set_strategy(PassREQ)
            .set_request_mode(self.main_client.REQ_MODE_DELETE)
        )

        asyncio.run(self.main_client.main_asynch())

    def prepare_post_tasks(self):
        all_post_data = self.main_data.return_all_posts()
        tasks = []
        for post in all_post_data:
            new_task = TaskObject(post_blackout_url, post)
            tasks.append(new_task)
        return tasks

    @staticmethod
    def _split_mode(mode) -> dict | None:
        custom_mode = mode.split(" ")
        ldap = start = end = None
        if len(custom_mode) not in (1, 2, 3, 4):
            raise Exception("Неверный формат ввода режима работы")

        if len(custom_mode) == 3:
            mode, start, end = custom_mode
        elif len(custom_mode) == 2:
            mode, ldap = custom_mode
        else:  # len == 4
            mode, ldap, start, end = custom_mode

        return {
            "start": int(start) if start else None,
            "end": int(end) if end else None,
            "ldap": int(ldap) if ldap else None,
            "mode": mode,
        }

    def _request_certain_spp(self, ldap, start=None, end=None):
        if isinstance(self.main_data.SPPs, dict):
            spp = self.main_data.SPPs[ldap]
            self.main_data.SPPs = {ldap: spp}
            if start and end:
                spp.post_data = self._days_interval(spp.post_data, start, end)

    def _request_all_by_date(self, start, end):
        if isinstance(self.main_data.SPPs, dict):
            for spp in self.main_data.SPPs:
                spp_current = self.main_data.SPPs[spp]
                spp_current.post_data = self._days_interval(
                    spp_current.post_data, start, end
                )

    def _filter_spps(self):
        if isinstance(self.main_data.SPPs, dict):
            keys_to_delete = []
            for key, spp in self.main_data.SPPs.items():
                if not (
                    spp.post_data or spp.status
                ):  # Удаляем спп без статуса или таблицы пост
                    keys_to_delete.append(key)
            for key in keys_to_delete:
                del self.main_data.SPPs[key]

    @staticmethod
    def _select_spp_for_clearing(data, ldap):
        if ldap:
            data.delete_spp = ldap

    @staticmethod
    def _days_interval(post_data, start, end):
        new_dict = {}
        for key, value in post_data.items():
            if start <= int(key) <= end:
                new_dict[key] = value
        return new_dict


def main_funktion():  # Основная функция
    print(f"VERSION {version}")
    AutoScheduleTime.init_values()
    main_client = AioClient(CompositeData)
    auto_schedule = AutoSchedule(main_client)
    mode = input(f"{instruction}\n")
    auto_schedule.start_auto_schedule(mode)
