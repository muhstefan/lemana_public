import os
import time
from datetime import datetime

from selenium import webdriver
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from my_libs.log import Logger
from data import CompositeData

home_dir = os.path.expanduser("~")
user_data_dir = os.path.join(home_dir, "Documents", "Profile AutoSPP")
options = webdriver.ChromeOptions()
options.add_argument("--allow-profiles-outside-user-dir")
options.add_argument("--enable-profile-shortcut-manager")
options.add_argument(f"user-data-dir={user_data_dir}")
options.add_argument("--profiling-flush=n")
options.add_argument("--enable-aggressive-domstorage-flushing")
options.add_experimental_option("detach", True)

log = Logger(user_data_dir)


class Selenium:
    def __init__(self):
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        self.wait = WebDriverWait(self.driver, 180)
        self.url_presale = "https://clientprojects.lemanapro.ru/main"
        self.url_whatsapp = "https://web.whatsapp.com/"
        self.driver.set_window_size(1024, 768)
        self.current_task = None

    # Локаторы — классные переменные
    new_chat_button = (By.CSS_SELECTOR, 'span[data-icon="new-chat-outline"]')
    myself_button = (By.XPATH, "//div[normalize-space(text())='Сообщение для себя']")
    message_copy = (By.CSS_SELECTOR, '[data-icon="copy-refreshed"]')
    link_to_phone = (By.CSS_SELECTOR, '[data-icon="chat-refreshed"]')

    @staticmethod
    def get_chrome_profile_path():
        return user_data_dir

    def show_tittle(self, tittle):
        script = f"""
        var div = document.createElement('div');
        div.style.position = 'fixed';
        div.style.top = '10px';
        div.style.left = '10px';
        div.style.color = 'black'; 
        div.style.padding = '10px';
        div.style.backgroundColor = 'yellow';
        div.style.zIndex = 10000;
        div.innerText = '{tittle}';
        document.body.appendChild(div);
        """
        self.driver.execute_script(script)

    def check_redirect(self):
        self.driver.get(self.url_presale)
        current_url = self.driver.current_url
        if self.url_presale != current_url:
            return True
        return False

    def selenium_ldap_login_check(self):
        self.driver.set_window_position(0, 0)
        if self.check_redirect():
            self.show_tittle("ВОЙДИ В СИСТЕМУ У ТЕБЯ 180 СЕКУНД")
        element_main_page = self.find_element_by_name("Главная")
        if not element_main_page:
            raise Exception(
                "Вы, либо не вошли, либо что то не так со страницой главная."
            )

        avatar_container = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '[data-testid="avatar-container"]')
            )
        )
        avatar_container.click()
        container = self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.lmui-View.lmui-View-pl-gap8")
            )
        )
        element = container.find_element(By.TAG_NAME, "span")
        text = element.text
        if not text:
            raise Exception("Не получили LDAP")
        ldap = text.split(" ")[1]
        self.driver.set_window_position(-10000, 0)
        return ldap

    def whatsapp_login(self):
        self.driver.set_window_position(0, 0)
        url = self.url_whatsapp
        self.driver.get(url)
        self.show_tittle("ВОЙДИ В WHATSAPP 180 СЕКУНД")
        try:
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '[data-icon="settings-refreshed"]')
                )
            )
            self.show_tittle(
                "Нажми на шестеренку настроек внизу. чтобы подтвердить вход"
            )
            key_icon_locator = (By.CSS_SELECTOR, '[data-icon="key-outline"]')
            self.wait_for_presence(key_icon_locator)
            self.driver.set_window_position(-10000, 0)
        except Exception:
            raise Exception("Не удалось войти.")

    def wait_and_click(self, by_locator):
        try:
            element = self.wait.until(EC.element_to_be_clickable(by_locator))
            element.click()
            return element
        except Exception as e:
            raise Exception(f"Ошибка в wait_and_click с локатором {by_locator}: {e}")

    def wait_for_presence(self, by_locator):
        try:
            return self.wait.until(EC.presence_of_element_located(by_locator))
        except Exception as e:
            raise Exception(f"Ошибка в wait_for_presence с локатором {by_locator}: {e}")

    def find_element_safe(self, by_locator):
        try:
            return self.driver.find_element(*by_locator)
        except Exception as e:
            raise Exception(f"Ошибка в find_element_safe с локатором {by_locator}: {e}")

    def check_phone_not_exist(self):
        try:
            self.driver.find_element(
                By.XPATH, '//span[contains(text(),"Не найдено результатов")]'
            )
            return True  # нашли элемент — ошибка
        except NoSuchElementException:
            return False  # элемент не найден — ошибки нет

    def find_element_by_name(self, name):
        xpath = f"//*[contains(normalize-space(text()), '{name}')]"
        try:
            return self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        except Exception as e:
            raise Exception(f"Ошибка в find_element_by_name с текстом '{name}': {e}")

    def click_to_message_input(self):
        el = self.find_element_by_name("Введите сообщение")
        el.click()

    def check_message_sended(self, message):
        now = datetime.now()
        search_string = f"[{now.strftime('%H:%M')}, {now.strftime('%d.%m.%Y')}]"

        while True:

            try:
                element = self.wait.until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            f'//div[contains(@data-pre-plain-text, "{search_string}") and .//span[contains(text(), "{message}")]]',
                        )
                    )
                )

                parent_element = element.find_element(By.XPATH, "..")
                span_element = parent_element.find_element(
                    By.XPATH, ".//span[@aria-label]"
                )
                message_status = span_element.get_attribute("aria-label")

                if message_status.strip() in ["Доставлено", "Прочитано", "Отправлено"]:
                    break
                else:
                    time.sleep(0.1)
            except StaleElementReferenceException:
                self.current_task.status = "Element.устарел(check_message_sended)"

    def send_message_save(self, phone_number, message):

        url = f"https://web.whatsapp.com/send?phone={phone_number}&text={message}"
        self.driver.get(url)

        self.wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Меню']"))
        )
        time.sleep(0.5)  # чаты не моментально появляются(там что то типа анимации)
        elements = self.driver.find_elements(By.XPATH, '//*[@id="main"]/header')
        if elements:

            # time.sleep(12)
            self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[@aria-label='Отправить']")
                )
            ).click()
            self.current_task.status = "done"
            time.sleep(1.2)

        else:
            self.current_task.status = "phone.not_exist"
            return
        # Если у нас открылся чат с именем номера телефона-то это УЖЕ НЕ ОШИБКА кнопка.

    def send_message(self, message, check):
        if not check:
            self.wait_and_click(self.new_chat_button)
        active_element = self.driver.switch_to.active_element
        active_element.send_keys(self.current_task.phone)

        time.sleep(0.5)
        check = self.check_phone_not_exist()
        if check:
            self.current_task.status = "phone.not_exist"
            active_element.send_keys(Keys.CONTROL + "a")
            active_element.send_keys(Keys.DELETE)
            return True
        active_element.send_keys(Keys.ENTER)
        active_element = self.driver.switch_to.active_element
        active_element.send_keys(message)

        # active_element.send_keys(Keys.ENTER)
        # time.sleep(0.2)
        # self.check_message_sended(message)

        active_element.send_keys(Keys.CONTROL + "a")
        time.sleep(0)
        active_element.send_keys(Keys.DELETE)
        time.sleep(0)
        self.current_task.status = "done"
        return False

    # разделить функцию на отправление сообщений. желательно по 1 изначально.
    def send_messages(self):
        self.driver.get(self.url_whatsapp)
        self.driver.set_window_position(0, 0)
        data = CompositeData()
        tasks = data.tasks
        messages = data.messages
        # check = False
        for task in tasks:
            self.current_task = task
            self.send_message_save(phone_number=task.phone, message=messages[task.type])
            # check = self.send_message(message=messages[task.type], check=check)

        self.driver.set_window_position(-10000, 0)

    @staticmethod
    def numbers_test():
        data = CompositeData()
        tasks = data.tasks
        numbers = ["79999999999", "79999999999", "79999999999", "79999999999"]
        for i, task in enumerate(tasks):
            task.phone = numbers[i % len(numbers)]
