import os
from time import sleep
import sys
from datetime import datetime
from private import KITCHEN, BATHROOM, STORAGE, FOUNDATION, JOINERY

now = datetime.now()  # Получаем текущую дату
today = now.date().strftime("%Y-%m-%d")


def check_project_world(test=None):
    exe_name = os.path.basename(sys.argv[0])
    if exe_name == "AutoSPP-Кухни.exe":
        return KITCHEN
    elif exe_name == "AutoSPP-Ванные.exe":
        return BATHROOM
    elif exe_name == "AutoSPP-Хранение.exe":
        return STORAGE
    elif exe_name == "AutoSPP-Стройка.exe":
        return FOUNDATION
    elif exe_name == "AutoSPP-Столярка.exe":
        return JOINERY
    elif exe_name == "auto_spp.py":
        return test
    else:
        print(f"НЕ УКАЗАН МИР AutoSPP!")
        sleep(20)
        return None
