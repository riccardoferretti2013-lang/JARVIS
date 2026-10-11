@echo off

cd /d "C:\Users\ricca\Desktop\jarvis"

echo ================================
echo AVVIO J.A.R.V.I.S.
echo ================================

echo Avvio J.A.R.V.I.S. Main...

start "J.A.R.V.I.S. MAIN" /min ^
"C:\Users\ricca\Desktop\jarvis\venv\Scripts\python.exe" ^
"C:\Users\ricca\Desktop\jarvis\qml_main.py"

timeout /t 3 /nobreak >nul

echo Avvio J.A.R.V.I.S. Node...

start "J.A.R.V.I.S. NODE" /min ^
"C:\Users\ricca\Desktop\jarvis\venv\Scripts\python.exe" ^
"C:\Users\ricca\Desktop\jarvis\raspberry_node\main.py"

exit /b