@echo off
chcp 65001 > nul
cd..

.venv\Scripts\python.exe -m PyInstaller --onefile --hidden-import=dateutil --hidden-import=gspread Projects\goal_filler\goal_filler.py"

cd dist
copy goal_filler.exe goal_filler-Кухни-Рома.exe
copy goal_filler.exe goal_filler-Кухни-Саша.exe
copy goal_filler.exe goal_filler-Ванные-Ира.exe
copy goal_filler.exe goal_filler-Ванные-Саша.exe
copy goal_filler.exe goal_filler-Хранение.exe
copy goal_filler.exe goal_filler-Столярка.exe
copy goal_filler.exe goal_filler-Стройка.exe
copy goal_filler.exe goal_filler-Хранение.exe
del goal_filler.exe
pause