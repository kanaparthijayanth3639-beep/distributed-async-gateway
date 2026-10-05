@echo off
title Local Infrastructure Dev Cluster
echo Booting microservice backend nodes...
echo.

start "Node 8001" cmd /k "set SERVER_ID=ALPHA_NODE_8001&&set PORT=8001&&python backend/microservice.py"
start "Node 8002" cmd /k "set SERVER_ID=BETA_NODE_8002&&set PORT=8002&&python backend/microservice.py"

timeout /t 2 /nobreak >nul

echo Spawning core proxy engine...
start "Proxy Gateway" cmd /k "set PYTHONPATH=.&&python gateway/core.py"
echo Engine setup complete. Target access: http://127.0.0.1:8080
pause
