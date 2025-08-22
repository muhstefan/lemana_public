from time_module import SppRateTime
import os
import sys
from abc import ABC
from private import *


class WORLD(ABC):

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.actions_stat_template = {
            key: 0 for key in cls.spp_rate_logic
        }  # Сохраняем в cls!
        cls.ExData = {
            **{key: None for key in cls.names},
            **{
                key: None for key in cls.actions_stat_template
            },  # Используем cls.actions_stat_template
            **{i: None for i in range(0, 24)},
        }

    @classmethod
    def check_project_world(cls, test=None):
        exe_name = os.path.basename(sys.argv[0])
        if exe_name == "spp_rate-Кухни.exe":
            return KITCHEN
        elif exe_name == "spp_rate-Ванные.exe":
            return BATHROOM
        elif exe_name == "spp_rate-Хранение.exe":
            return STORAGE
        elif exe_name == "spp_rate-Стройка.exe":
            return FOUNDATION
        elif exe_name == "spp_rate-Столярка.exe":
            return JOINERY
        elif exe_name == "spp_rate.py":
            return test
        else:
            raise Exception("Не указан мир в названии программы")

    type_dictionary = {}

    spp_rate_points = {
        "Задачи": 2,
        "Комментарии": 1,
        "Отрисовки": 7,
        "Редактирование": 3,
        "Продажи": 3,
        "Услуги": 3,
        "Сметы": 2,
        "Аннулирование": 1,
        "Не закрыл": 0,
        "Поздно взял": 0,
    }

    spp_rate_logic = {
        "Задачи": ["COMPLETED_TASK", "USER_TASK"],
        "Комментарии": ["COMMENT", "PRESALES"],
        "Отрисовки": ["CONFIGURATION"],
        "Редактирование": ["PROJECT_EDIT"],
        "Продажи": ["MARKETPLACE_ORDER", "SOLUTION"],
        "Услуги": ["SERVICE_TASK_MEASUREMENT", "SERVICE_TASK_ORDER"],
        "Сметы": ["QUOTATION"],
        "Аннулирование": ["ADD_REASON_TO_CANCEL"],
        "Не закрыл": ["Unclosed ticket"],
        "Поздно взял": ["Late pickup"],
    }

    names = {"ИМЯ": None, "Points": None}

    @classmethod
    def get_type_dictionary(cls):
        return cls.type_dictionary

    world_number = -1
    deal_statuses = "..."
    name_world_eng = "..."
    project_types = "B2B,KITCHEN,BATHROOM,STORAGE,DRAFT_PROJECT,EXPRESS_PROJECT,DESIGN_CONSULTATION,DESIGN_PROJECT,INTERIOR_DOOR,TERRACE,STAIRCASE,ENTRANCE_DOOR,WINDOW,FOUNDATION,CEILING,PLASTER,FLOOR_SCREED,ROOF,FENCE,FACADE"

    @classmethod
    def get_url_deals_spp_list(cls):
        return url_deals_spp_list.format(
            deal_statuses=cls.deal_statuses, project_types=cls.project_types
        )

    @classmethod
    def get_url_eq(cls):
        return url_eq.format(
            world_number=cls.world_number, yesterday=SppRateTime.yesterday
        )

    @classmethod
    def get_url_deal_information(cls):
        return url_deal_information.format(name_world_eng=cls.name_world_eng)


class JOINERY(WORLD):

    world_name = "столярные изделия"
    name_world_eng = "JOINERY"
    world_number = "2"
    deal_statuses = "NEW,CALCULATION,MEASUREMENT,APPROVAL,PAPERS,PAYMENT,PAID,MANUFACTURING,ASSEMBLING"

    spp_rate_points = {
        "Задачи": 2,
        "Комментарии": 1,
        "Продажи": 3,
        "Услуги": 3,
        "Сметы": 2,
        "Аннулирование": 1,
    }

    spp_rate_logic = {
        "Задачи": ["COMPLETED_TASK", "USER_TASK"],
        "Комментарии": ["COMMENT", "PRESALES"],
        "Продажи": ["MARKETPLACE_ORDER", "SOLUTION"],
        "Услуги": ["SERVICE_TASK_MEASUREMENT", "SERVICE_TASK_ORDER"],
        "Сметы": ["QUOTATION"],
        "Аннулирование": ["ADD_REASON_TO_CANCEL"],
    }

    type_dictionary = {  # Тут и оптимизировать как то можно
        "ADD_REASON_TO_CANCEL": ["updatedAt", "updatedBy"],
        "USER_TASK": ["linkedDate", "createdBy.ldap"],
        "COMPLETED_TASK": ["updatedOn", "updatedBy.ldap"],
        "SERVICE_TASK_ORDER": ["linkedDate", "linkedBy"],
        "MARKETPLACE_ORDER": ["linkedDate", "linkedBy"],
        "SOLUTION": ["linkedDate", "linkedBy"],  #
        "CONFIGURATION": ["created", "createdBy"],
        "PROJECT_EDIT": ["updated", "updatedBy"],
        "PRESALES": ["createdDate", "createdBy"],
        "QUOTATION": ["linkedDate", "linkedBy"],
        "SERVICE_TASK_MEASUREMENT": ["linkedDate", "linkedBy"],
        "COMMENT": ["createdDate", "createdBy"],
    }


class FOUNDATION(WORLD):

    world_name = "стройка"
    name_world_eng = "FOUNDATION"
    world_number = "1"

    spp_rate_points = {
        "Задачи": 2,
        "Комментарии": 1,
        "Продажи": 3,
        "Услуги": 3,
        "Сметы": 2,
        "Аннулирование": 1,
        "Не закрыл": 0,
        "Поздно взял": 0,
    }

    deal_statuses = "NEW,CALCULATION,MEASUREMENT,APPROVAL,PAPERS,PAYMENT,PAID,MANUFACTURING,ASSEMBLING"

    spp_rate_logic = {
        "Задачи": ["COMPLETED_TASK", "USER_TASK"],
        "Комментарии": ["COMMENT", "PRESALES"],
        "Продажи": ["MARKETPLACE_ORDER", "SOLUTION"],
        "Услуги": ["SERVICE_TASK_MEASUREMENT", "SERVICE_TASK_ORDER"],
        "Сметы": ["QUOTATION"],
        "Аннулирование": ["ADD_REASON_TO_CANCEL"],
        "Не закрыл": ["Unclosed ticket"],
        "Поздно взял": ["Late pickup"],
    }

    @classmethod
    def spp_check(cls, resource):
        if (
            resource.get("appointments") or resource.get("isActive") is True
        ):  # если есть заявки
            return True

    type_dictionary = {  # Тут и оптимизировать как то можно
        "ADD_REASON_TO_CANCEL": ["updatedAt", "updatedBy"],
        "USER_TASK": ["linkedDate", "createdBy.ldap"],
        "COMPLETED_TASK": ["updatedOn", "updatedBy.ldap"],
        "SERVICE_TASK_ORDER": ["linkedDate", "linkedBy"],  # услуга
        "MARKETPLACE_ORDER": ["linkedDate", "linkedBy"],
        "SERVICE_TASK_MEASUREMENT": ["linkedDate", "linkedBy"],  # замер
        "SOLUTION": ["linkedDate", "linkedBy"],  #
        "CONFIGURATION": ["created", "createdBy"],
        "PROJECT_EDIT": ["updated", "updatedBy"],
        "PRESALES": ["createdDate", "createdBy"],
        "QUOTATION": ["created", "linkedBy"],
        "COMMENT": ["createdDate", "createdBy"],
    }


class KITCHEN(WORLD):

    world_name = "кухни"
    name_world_eng = "KITCHEN"
    world_number = "15"

    type_dictionary = {  # Тут и оптимизировать как то можно
        "ADD_REASON_TO_CANCEL": ["updatedAt", "updatedBy"],
        "USER_TASK": ["linkedDate", "createdBy.ldap"],
        "COMPLETED_TASK": ["updatedOn", "updatedBy.ldap"],
        "SERVICE_TASK_ORDER": ["linkedDate", "linkedBy"],
        "MARKETPLACE_ORDER": ["linkedDate", "linkedBy"],
        "SOLUTION": ["linkedDate", "linkedBy"],  #
        "CONFIGURATION": ["created", "createdBy"],
        "PROJECT_EDIT": ["updated", "updatedBy"],
        "COMMENT": ["createdDate", "updatedBy"],
        "QUOTATION": ["created", "createdBy"],
    }

    deal_statuses = (
        "NEW,DEAL_IN_WORK,MEASUREMENT,ON_HOLD,REGISTRATION,AFTER_SALES,DEAL_COMPLETED"
    )


class BATHROOM(WORLD):

    world_name = "ванные"
    name_world_eng = "BATHROOM"
    world_number = "6,7"

    type_dictionary = {  # Тут и оптимизировать как то можно
        "ADD_REASON_TO_CANCEL": ["updatedAt", "updatedBy"],
        "USER_TASK": ["linkedDate", "createdBy.ldap"],
        "COMPLETED_TASK": ["updatedOn", "updatedBy.ldap"],
        "SERVICE_TASK_ORDER": ["linkedDate", "linkedBy"],
        "MARKETPLACE_ORDER": ["linkedDate", "linkedBy"],
        "SOLUTION": ["linkedDate", "linkedBy"],  #
        "CONFIGURATION": ["created", "createdBy"],
        "PROJECT_EDIT": ["updated", "updatedBy"],
        "COMMENT": ["createdDate", "createdBy"],
        "QUOTATION": ["created", "createdBy"],
    }

    deal_statuses = (
        "NEW,DEAL_IN_WORK,MEASUREMENT,ON_HOLD,REGISTRATION,AFTER_SALES,DEAL_COMPLETED"
    )


class STORAGE(WORLD):

    world_name = "хранение"
    name_world_eng = "STORAGE"
    world_number = "14"
    type_dictionary = {
        "ADD_REASON_TO_CANCEL": ["updatedAt", "updatedBy"],
        "USER_TASK": ["linkedDate", "createdBy.ldap"],
        "COMPLETED_TASK": ["updatedOn", "updatedBy.ldap"],
        "SERVICE_TASK_ORDER": ["linkedDate", "linkedBy"],
        "MARKETPLACE_ORDER": ["linkedDate", "linkedBy"],
        "SOLUTION": ["linkedDate", "linkedBy"],  #
        "CONFIGURATION": ["created", "createdBy"],
        "PROJECT_EDIT": ["updated", "updatedBy"],
        "COMMENT": ["createdDate", "createdBy"],
        "QUOTATION": ["created", "createdBy"],
    }

    deal_statuses = (
        "NEW,DEAL_IN_WORK,MEASUREMENT,ON_HOLD,REGISTRATION,AFTER_SALES,DEAL_COMPLETED"
    )


class SPP:
    def __init__(self, ldap, name, day_begin, project_world, day_end):

        self.color = None
        self.ldap = ldap
        self.name = name
        self.day_begin = day_begin
        self.day_end = day_end
        self.points = 0
        self.actions_stat = project_world.actions_stat_template.copy()
        self.time_stat = []
        # Копируем словари, чтобы ссылку не передавать на одно и тоже
        for i in range(24):
            self.time_stat.append(self.actions_stat.copy())


if __name__ == "__main__":
    kitchen = KITCHEN()
    url = kitchen.get_url_eq()
    url2 = kitchen.get_url_deal_information()
    url3 = kitchen.get_url_deals_spp_list()
    pass
