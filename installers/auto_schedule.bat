@echo off
chcp 65001 > nul

cd..
.venv\Scripts\python.exe -m PyInstaller --onefile --hidden-import=gspread Projects\AutoSchedule\AutoSchedule.py
cd dist

copy AutoSchedule.exe AutoSchedule-Кухни.exe
copy AutoSchedule.exe AutoSchedule-Ванные.exe
copy AutoSchedule.exe AutoSchedule-Хранение.exe
del AutoSchedule.exe

pause