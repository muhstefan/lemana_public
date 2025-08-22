@echo off
chcp 65001 > nul
cd..
.venv\Scripts\python.exe -m PyInstaller --onefile Projects\can_ban_sort\can_ban_sort.py

pause