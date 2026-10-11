@echo off
echo ===================================================
echo Starting Hivemind FastAPI Microservice Backend...
echo ===================================================
set "PY_EXE=%USERPROFILE%\AppData\Roaming\uv\python\cpython-3.11.15-windows-x86_64-none\python.exe"
if exist "%PY_EXE%" (
    "%PY_EXE%" server.py
) else (
    python server.py
)
pause
