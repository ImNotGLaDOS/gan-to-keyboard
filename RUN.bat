@echo off
start "Sender" /B python src\\controller.py
start "Reader" /B python src\\key_emulator.py
pause