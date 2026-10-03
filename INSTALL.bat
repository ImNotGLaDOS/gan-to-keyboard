@echo off
pip install bleak
pip install pywin32
pip install pydirectinput

:: sleep, so user can read the output for a bit. Otherwise it may look like an installation of malware
timeout /t 5