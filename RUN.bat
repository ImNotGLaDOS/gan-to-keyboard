@echo off
start "Sender" /B python controller.py
start "Reader" /B python key_emulator.py
pause