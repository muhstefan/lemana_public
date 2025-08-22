from my_libs import SingletonMeta
from world import *


class Action:
    def __init__(self, type_action, ldap, time):
        self.type_action = type_action
        self.ldap = ldap
        self.time = time


class CompositeData(metaclass=SingletonMeta):
    def __init__(self):
        self._actions = []  # Список действия общий.
        self.last_action_time = None  # Время последнего действия
        self._deals = []  # Список сделок общий
        self.SPPs = {}  # Список спп у которых в свою очередь (ldap, имя, начало дня)
        self.project_world = WORLD.check_project_world(KITCHEN)
        self.web_squad = {}

    def get_actions(self):
        return self._actions

    # Множество реализовано по принципу хэш таблицы, поэтому быстрее
    def get_ldap_set(self):
        return {spp.ldap for spp in self.SPPs.values()}

    def get_deals(self):
        return self._deals

    def add_deal(self, action):
        self._deals.append(action)

    def add_action(self, action):
        self._actions.append(action)
        self.last_action_time = action.time

    def add_spp(self, spp):
        self.SPPs[spp.ldap] = spp

    def get_spp_list(self):
        return self.SPPs

    def get_project_world(self):
        return self.project_world
