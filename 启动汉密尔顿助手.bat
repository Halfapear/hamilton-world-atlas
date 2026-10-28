@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
  start "Hamilton Ticket Assistant" cmd /k "cd /d ""%~dp0"" && py -m http.server 8765 --bind 127.0.0.1"
) else (
  where python >nul 2>nul
  if %errorlevel%==0 (
    start "Hamilton Ticket Assistant" cmd /k "cd /d ""%~dp0"" && python -m http.server 8765 --bind 127.0.0.1"
  ) else (
    echo Python was not found. Please install Python or run: python -m http.server 8765 --bind 127.0.0.1
    pause
    exit /b 1
  )
)
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8765/index.html"
endlocal
