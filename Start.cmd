@echo off
setlocal
set "PYTHONUTF8=1"
set "DJ_LANGUAGE=en"
if exist "%~dp0language.txt" set /p DJ_LANGUAGE=<"%~dp0language.txt"
if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" "%~dp0extract_audio.py" %*
) else (
    if /I "%DJ_LANGUAGE%"=="zh" (
        echo 请先运行 scripts\setup-windows.ps1，详见 README.md。
    ) else (
        echo Run scripts\setup-windows.ps1 first. See README.md.
    )
    pause
    exit /b 2
)
set "DJ_RESULT=%ERRORLEVEL%"
echo.
if /I "%DJ_LANGUAGE%"=="zh" (
    echo 退出码：%DJ_RESULT% [0=成功，1=部分失败，2=输入或依赖错误]
) else (
    echo Exit code: %DJ_RESULT% [0=OK, 1=partial failure, 2=input or dependency error]
)
pause
exit /b %DJ_RESULT%
