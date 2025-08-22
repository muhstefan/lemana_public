import traceback

from main_logic import main_funktion
from my_libs import Logger

log = Logger()

try:
    main_funktion()
except Exception as e:
    print(e)
    traceback.print_exc()
    log.error(f"Произошла ошибка : {e}")
