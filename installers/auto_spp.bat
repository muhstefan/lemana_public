@echo off
chcp 65001 > nul

xcopy "..\MyLibs" ".\MyLibs" /E /I /Y

"..\.venv\Scripts\python.exe" -m PyInstaller --onefile --hidden-import=dateutil --hidden-import=selenium ".\AutoSPP.py"

ren ".\dist\AutoSPP.exe" "AutoSPP-Кухни.exe"

rmdir /S /Q ".\MyLibs"
cd dist
pause