import os
from time import sleep
import sys
from datetime import datetime
from private import (
    KITCHEN1,
    KITCHEN2,
    BATHROOM1,
    BATHROOM2,
    STORAGE,
    FOUNDATION,
    JOINERY,
)

now = datetime.now()  # Получаем текущую дату
today = now.date().strftime("%Y-%m-%d")


def check_project_world(test=None):
    exe_name = os.path.basename(sys.argv[0])
    if exe_name == "goal_filler-Кухни-Рома.exe":
        return KITCHEN1
    if exe_name == "goal_filler-Кухни-Саша.exe":
        return KITCHEN2
    elif exe_name == "goal_filler-Ванные-Ира.exe":
        return BATHROOM1
    elif exe_name == "goal_filler-Ванные-Саша.exe":
        return BATHROOM2
    elif exe_name == "goal_filler-Хранение.exe":
        return STORAGE
    elif exe_name == "goal_filler.py":
        return test
    elif exe_name == "goal_filler-Стройка.exe":
        return FOUNDATION
    elif exe_name == "goal_filler-Столярка.exe":
        return JOINERY
    elif exe_name == "goal_filler.py":
        return test
    else:
        print(f"НЕ УКАЗАН МИР (Название должно вида goal_filler-Кухни.exe)")
        sleep(20)
        return None
