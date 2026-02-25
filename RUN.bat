@echo off
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "BINDS_DIR=%SCRIPT_DIR%binds"

:: List all binds
echo Awailable binds:
set "count=0"
for /f "delims=" %%f in ('dir /b /a-d "%BINDS_DIR%" 2^>nul') do (
    set /a count+=1
    set "file[!count!]=%%f"
    echo !count!: %%f
)

set /p "choice=Enter the number of the file to process: "

start "Sender" /B python src\\controller.py
start "Reader" /B python src\\key_emulator.py "%BINDS_DIR%\!file[%choice%]!"
pause