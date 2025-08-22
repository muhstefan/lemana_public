@echo off
chcp 65001 > nul
cd..

.venv\Scripts\python.exe -m PyInstaller --onefile --hidden-import=dateutil --hidden-import=gspread Projects\spp_rate\spp_rate.py

cd dist
copy spp_rate.exe spp_rate-Кухни.exe
copy spp_rate.exe spp_rate-Ванные.exe
copy spp_rate.exe spp_rate-Хранение.exe
copy spp_rate.exe spp_rate-Стройка.exe
copy spp_rate.exe spp_rate-Столярка.exe
del spp_rate.exe
pause