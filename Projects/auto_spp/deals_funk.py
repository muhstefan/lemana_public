import asyncio
import os
import re

from my_libs.aioclient import AioClient
from my_libs.log import Logger
from my_libs.processor import Strategy
from my_libs.ui_module import BaseInterface
from data import *
from module_selenium import Selenium
from private import *
from world import check_project_world

log = Logger(Selenium.get_chrome_profile_path())
CURRENT_WORLD = check_project_world(KITCHEN)


class EORequester(Strategy):

    def parse(self):
        ldap = self.main_data.ldap
        resources = self.get_json().get("resources")
        for resource in resources:
            if resource.get("ldap") == ldap:
                self.host_list(resource)

    def host_list(self, resource):

        for appointment in resource.get("appointments"):
            phone = appointment.get("phone")
            new_task = Task(title="host", deal_id="host", phone=phone)
            new_task.type = "host"
            self.main_data.tasks.append(new_task)


class TasksRequester(Strategy):

    def parse(self):
        tasks = self.get_json().get("userTasks")
        for task in tasks:
            task_title = task.get("title")
            task_deal_id = task.get("relatedObject").get("id")
            phone = task.get("customer").get("phone")
            new_task = Task(title=task_title, deal_id=task_deal_id, phone=phone)
            self.get_data.add_task(new_task)


class AutoSpp:
    def __init__(self, aio_client, interface, selenium_client):
        self.strategy = None
        self.aio_client = aio_client
        self.selenium_client = selenium_client
        self.interface = interface

    def set_strategy(self, strategy_name):
        self.strategy = strategy_name(self)
        self.strategy.run()

    def edit_scripts(self):
        script_path = self.take_path_scripts_file()
        os.startfile(script_path)

    def edit_log(self):
        script_path = self.take_path_scripts_file(filename="app_errors.log")
        os.startfile(script_path)

    def take_path_scripts_file(self, filename="script.txt"):
        script_path = os.path.join(Selenium.get_chrome_profile_path(), filename)
        if not os.path.isfile(script_path):
            return self.create_script_file(filename)
        return script_path

    @staticmethod
    def messages_str(messages):
        display_lines = []
        for key, message in messages.items():
            formatted_key = key.capitalize()
            line = f"{formatted_key} : {message}"
            display_lines.append(line)
        return "\n".join(display_lines)

    def read_scripts_messages(self):
        script_path = self.take_path_scripts_file()
        messages = {}

        try:
            with open(script_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            log.error(f"Ошибка при чтении файла: {e}")
            return messages

        blocks = [
            block.strip() for block in re.split(r"\n\s*\n+", content) if block.strip()
        ]

        keys = ["host", "актуальность", "сборка"]

        for i, block in enumerate(blocks):
            if "===" not in block:
                # Можно сделать лог или исключение, если формат неожидан
                continue
            message_part = block.split("===")[1]
            message = message_part.strip()

            messages[keys[i]] = message

        return messages

    @staticmethod
    def sort():
        data = CompositeData()
        tasks_types = data.tasks_types.keys()
        filtered_tasks = []

        for task in data.tasks:
            name = task.title.lower()
            found_key = None

            for key in tasks_types:
                if key in name:
                    found_key = key
                    break

            if found_key:
                task.type = found_key
                filtered_tasks.append(task)
        data.tasks = filtered_tasks

    @staticmethod
    def create_script_file(filename="script.txt"):
        initial_content = script_spp_base.format(
            ProjectWorld=CURRENT_WORLD.current_project_name
        )
        profile_path = Selenium.get_chrome_profile_path()
        script_path = os.path.join(profile_path, filename)
        if not os.path.isfile(script_path):
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(initial_content)
        return script_path


class AutoSppStrategy:
    def __init__(self, auto_spp):
        self.auto_spp = auto_spp
        self.interface: BaseInterface = auto_spp.interface
        self.data = None

    def build_aio_client(self, processor_strategy, url):
        client = self.auto_spp.aio_client
        (
            client.set_url(url)
            .set_request_mode(client.REQ_MODE_SOLO_GET)
            .set_certificate(cert_1)
            .set_headers(headers_base)
            .set_processor_strategy(processor_strategy)
        )
        asyncio.run(client.main_asynch())

    @staticmethod
    def with_common_behavior(run_func):
        def wrapper(self, *args, **kwargs):
            # Начальное общее поведение
            self.data = CompositeData()
            self.data.messages = self.auto_spp.read_scripts_messages()
            self.interface.root.withdraw()

            # Моя функция
            result = run_func(self, *args, **kwargs)

            # Конечное общее поведение
            self.auto_spp.selenium_client.send_messages()

            text = []
            counter = 0
            for task in self.data.tasks:
                if task.status != "done":
                    text.append(f"ОШИБКА -{task.phone} - {task.status}")
                if task.status == "done":
                    counter += 1
            text.append(f"Выполнено {counter} задач")
            self.interface.show_info(text)
            self.interface.root.deiconify()

        return wrapper

    # создаем новые задачи эти выполняем. причем ставим их на рабочие дни.
    # 1 нужно написать алгоритм графика спп. чтобы была карта на какое число ближайшее можно ставить
    # 2 потом алгоритм выполнения задачи и алгоритм постановки задачи.
    def do_tasks_in_crm_and_create_new(self):
        for task in self.data.tasks:
            if task.type == "актуальность" and task.status != "done":
                pass


class AutoSppHost(AutoSppStrategy):
    @AutoSppStrategy.with_common_behavior
    def run(self):
        url_eo = EO_get_url.format(number_world="15")
        self.build_aio_client(processor_strategy=EORequester, url=url_eo)
        pass


class AutoSppTasks(AutoSppStrategy):

    @AutoSppStrategy.with_common_behavior
    def run(self):
        ldap = self.data.ldap
        url_tasks = tasks_get_url.format(ldap=ldap)
        self.build_aio_client(processor_strategy=TasksRequester, url=url_tasks)
        self.auto_spp.sort()


class AutoSppWhatsAppLogin(AutoSppStrategy):
    def run(self):
        self.interface.root.withdraw()
        self.auto_spp.selenium_client.whatsapp_login()
        self.interface.root.deiconify()


class AutoSppSettings(AutoSppStrategy):
    def run(self):
        self.interface.invert_frames()
        self.data = CompositeData()
        self.data.messages = self.auto_spp.read_scripts_messages()
        self.interface.show_info(self.auto_spp.messages_str(self.data.messages))


def create_interface(interface, auto_spp, selenium_client):
    interface.create_button(
        frame=interface.frame_settings,
        button_funk=lambda: auto_spp.set_strategy(AutoSppSettings),
        text_button="НАСТРОЙКИ",
    )
    interface.create_button(
        button_funk=lambda: auto_spp.set_strategy(AutoSppHost),
        text_button="Сделать HOST",
    )
    interface.create_button(
        button_funk=lambda: auto_spp.set_strategy(AutoSppTasks),
        text_button="Отработка задач",
    )
    interface.create_button(
        button_funk=auto_spp.edit_scripts,
        text_button="Редактировать скрипты",
        frame=interface.frame_bottom,
        background_color=interface.pink,
    )
    interface.create_button(
        button_funk=auto_spp.edit_log,
        text_button="LOG",
        frame=interface.frame_bottom,
        background_color=interface.pink,
    )
    interface.create_button(
        button_funk=lambda: auto_spp.set_strategy(AutoSppWhatsAppLogin),
        text_button="WHATSAPP ВХОД",
        frame=interface.frame_bottom,
        background_color=interface.pink,
    )
    interface.initialize("LEGEND")


def auto_spp_main_function():  # Основная функция

    print("VER 0.3")
    selenium_client = Selenium()
    try:
        data = CompositeData()
        data.ldap = 60200223  # Test
        ldap = selenium_client.selenium_ldap_login_check()
        headers_base["ldap"] = ldap
        # data.ldap = ldap

        aio_client = AioClient(CompositeData)
        interface = BaseInterface()
        auto_spp = AutoSpp(
            aio_client=aio_client, interface=interface, selenium_client=selenium_client
        )
        create_interface(
            auto_spp=auto_spp, interface=interface, selenium_client=selenium_client
        )

    except Exception as e:
        log.error(f"Ошибка в главном блоке -{e}")
    finally:
        selenium_client.driver.quit()  # Гарантированное закрытие браузера
