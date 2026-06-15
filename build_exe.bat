@echo off
echo ==========================================
echo   Gemini Telegram Bot - EXE Builder
echo ==========================================
echo.

REM Activate virtual environment
call myvenv\Scripts\activate.bat

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [*] PyInstaller o'rnatilmoqda...
    pip install pyinstaller
)

echo.
echo [*] EXE build boshlanmoqda...
echo.

REM Clean previous builds
if exist "dist\GeminiTelegramBot.exe" del /f "dist\GeminiTelegramBot.exe"

REM Build with spec file
pyinstaller Gemini_Bot.spec --clean

echo.
if exist "dist\GeminiTelegramBot.exe" (
    echo ==========================================
    echo   MUVAFFAQIYATLI!
    echo ==========================================
    echo.
    echo   EXE fayl: dist\GeminiTelegramBot.exe
    echo.
    echo   MUHIM: .env faylni exe yoniga qo'ying!
    echo   Yoki exe ichida o'rnatilgan .env ishlatiladi.
    echo.
    echo   Boshqa PC ga olib o'tish uchun:
    echo   1. dist\GeminiTelegramBot.exe ni nusxalang
    echo   2. .env faylni exe yoniga qo'ying (ixtiyoriy)
    echo   3. EXE ni ishga tushiring
    echo ==========================================
    
    REM Copy .env next to exe for convenience
    if exist ".env" copy ".env" "dist\.env" >nul
    echo.
    echo   .env fayl dist\ papkaga nusxalandi.
) else (
    echo ==========================================
    echo   XATOLIK! Build amalga oshmadi.
    echo   Loglarni tekshiring.
    echo ==========================================
)

echo.
pause
