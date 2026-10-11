@echo off
echo ===================================================
echo Starting Hivemind Tactical Command Dashboard...
echo ===================================================
set "PY_EXE=%USERPROFILE%\AppData\Roaming\uv\python\cpython-3.11.15-windows-x86_64-none\python.exe"
if exist "%PY_EXE%" (
    "%PY_EXE%" -m streamlit run app.py
) else (
    python -m streamlit run app.py
)
pause
