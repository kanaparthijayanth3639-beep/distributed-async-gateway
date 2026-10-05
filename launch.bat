@echo off
title High-Availability Cluster Orchestrator
echo =======================================================
echo     LAUNCHING ASYNC PROXY GATEWAY MESH NETWORK
echo =======================================================
echo.

:: 1. Deploy Application Server Node Alpha on Port 8001
echo [*] Initializing Cluster Node Alpha on Port 8001...
start "Cluster Node Alpha" cmd /k "set SERVER_ID=ALPHA_NODE_8001&&set PORT=8001&&python backend/microservice.py"

:: 2. Deploy Application Server Node Beta on Port 8002
echo [*] Initializing Cluster Node Beta on Port 8002...
start "Cluster Node Beta" cmd /k "set SERVER_ID=BETA_NODE_8002&&set PORT=8002&&python backend/microservice.py"

:: 3. Give servers a quick 2-second buffer to initialize their socket loops
timeout /t 2 /nobreak >nul

:: 4. Launch the Central Traffic Proxy Engine
echo [*] Ignition sequence completed. Spawning Core Proxy Gateway...
start "Proxy Core Engine" cmd /k "set PYTHONPATH=.&&python gateway/core.py"
echo.
echo =======================================================
echo    Cluster deployed! Navigate to: http://127.0.0.1:8080
echo =======================================================
pause
