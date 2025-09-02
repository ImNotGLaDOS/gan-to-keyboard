@echo off
start "Sender" /B python mock_sender.py
start "Reader" /B python key_emulator.py
pause