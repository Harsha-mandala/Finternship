@echo off
echo.
echo  ██████╗  Hotel Aditya Grand
echo  ██╔══██╗ AI Order Assistant
echo  ███████║ POC v1.0
echo  ██╔══██╝
echo  ██║      Starting backend...
echo  ╚═╝
echo.

cd /d "%~dp0backend"
py -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
