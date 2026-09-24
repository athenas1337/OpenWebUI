@echo off
title Open WebUI - Athena Instance
echo ============================================
echo   Open WebUI - Starting Servers
echo ============================================
echo.

REM Load .env file
for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
    set "line=%%a"
    if not "!line:~0,1!"=="#" (
        set "%%a=%%b"
    )
)

REM Set secret key
if not defined WEBUI_SECRET_KEY (
    set WEBUI_SECRET_KEY=athena-openwebui-k3y-s3cur3-2026
)

echo [1/2] Starting Backend on http://localhost:8080 ...
cd backend
start "OpenWebUI-Backend" cmd /c "venv\Scripts\python.exe -m uvicorn open_webui.main:app --host 0.0.0.0 --port 8080 --forwarded-allow-ips=*"
cd ..

echo [2/2] Starting Frontend on http://localhost:5173 ...
start "OpenWebUI-Frontend" cmd /c "npm run dev"

echo.
echo ============================================
echo   Servers Starting!
echo ============================================
echo.
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8080
echo.
echo   Press any key to stop all servers...
pause > nul

taskkill /FI "WINDOWTITLE eq OpenWebUI-Backend" /F 2>nul
taskkill /FI "WINDOWTITLE eq OpenWebUI-Frontend" /F 2>nul
echo Servers stopped.
