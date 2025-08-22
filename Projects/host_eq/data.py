from my_libs import SingletonMeta

version = 0.3

instruction = """
Введите ДАТУ: Формат(0000-00-00) и фамилию сотрудника, заявки которого хотите посмотреть - пример:
2025-12-12 Иванов

введите только дату чтобы посмотреть хост всех сотрудников:
2025-12-12
=========================
"""


class Appointment:
    def __init__(self, spp_name, client_name, phone, time):
        self.spp_name = spp_name
        self.client_name = client_name
        self.phone = phone
        self.time = time

    def __str__(self):
        return f" СПП {self.spp_name} Клиент: {self.client_name} {self.phone} время по мск: {self.time}"


class CompositeData(metaclass=SingletonMeta):
    def __init__(self):
        self.appointments = []
