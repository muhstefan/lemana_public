from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import os

home_dir = os.path.expanduser("~")
user_data_dir = os.path.join(home_dir, "Documents", "Profile AutoSPP")
options = webdriver.ChromeOptions()
options.add_argument("--allow-profiles-outside-user-dir")
options.add_argument("--enable-profile-shortcut-manager")
options.add_argument(f"user-data-dir={user_data_dir}")
options.add_argument("--profiling-flush=n")
options.add_argument("--enable-aggressive-domstorage-flushing")
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=options
)
wait = WebDriverWait(driver, 30)
file_path = "file.txt"


def read_file(file_path):
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as file:
            pass
        return [], []

    if os.path.getsize(file_path) == 0:
        return [], []

    phone_numbers = []
    messages = []

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.split("% ", 1)
            if len(parts) == 2:
                # Оставляем только цифры в phone_number
                phone_number = "".join(filter(str.isdigit, parts[0]))
                message = parts[1].strip()
                phone_numbers.append(phone_number)
                messages.append(message)

    return phone_numbers, messages


phone_numbers, messages = read_file(file_path)
if phone_numbers and messages:

    for phone_number, message in zip(phone_numbers, messages):

        url = f"https://web.whatsapp.com/send?phone={phone_number}&text={message}"
        driver.get(url)

        whatsapp = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Меню']"))
        )
        sleep(0.5)  # чаты не моментально появляются(там что то типа анимации)
        elements = driver.find_elements(By.XPATH, '//*[@id="main"]/header')
        if elements:

            wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[@aria-label='Отправить']")
                )
            ).click()
            sleep(1.5)

            # now = datetime.now()    Работал над отслеживанием отправленного.
            # search_string = f"[{now.strftime("%H:%M")}, {now.strftime("%d.%m.%Y")}]"
            # element = wait.until(EC.presence_of_element_located((By.XPATH,  f'//div[contains(@data-pre-plain-text, "{search_string}") and .//span[contains(text(), {message})]]')))
            # parent_element = element.find_element(By.XPATH, '..')
            # span_element = parent_element.find_element(By.XPATH, ".//span[@aria-label]")

        else:
            continue
        # Если у нас открылся чат с именем номера телефона-то это УЖЕ НЕ ОШИБКА кнопка.
