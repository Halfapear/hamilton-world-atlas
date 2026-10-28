@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>&1
if %errorlevel%==0 (
  start "Hamilton World Atlas" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:8765/index.html"
  py -3 -m http.server 8765 --bind 127.0.0.1
) else (
  where python >nul 2>&1
  if errorlevel 1 (
    echo Python 3 was not found. Install Python 3, then run this file again.
    pause
    exit /b 1
  )
  start "Hamilton World Atlas" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:8765/index.html"
  python -m http.server 8765 --bind 127.0.0.1
)
endlocal
