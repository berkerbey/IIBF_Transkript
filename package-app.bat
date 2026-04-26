@echo off
echo ==================================================
echo PAU IIBF Transkript - Paketleme Betigi (Alpha v0.1)
echo ==================================================

:: 1. Python Ortam Kontrolü
:: Eğer hali hazırda bir ortam aktifse (conda gibi) devam et, değilse .venv kontrol et.
set "PYTHON_READY=0"
if defined CONDA_DEFAULT_ENV set "PYTHON_READY=1"
if defined VIRTUAL_ENV set "PYTHON_READY=1"

if "%PYTHON_READY%"=="0" (
    if exist ".venv\Scripts\activate" (
        echo [1/4] .venv aktif ediliyor...
        call .venv\Scripts\activate
        set "PYTHON_READY=1"
    )
)

if "%PYTHON_READY%"=="0" (
    echo [HATA] Aktif bir Python ortami bulunamadi.
    echo Lutfen once ortaminizi aktif edin veya projenize .venv kurun.
    pause
    exit /b
)

echo [1/4] Python Backend paketleniyor...
pip install uvicorn fastapi
pyinstaller --noconfirm --clean server.spec

:: 3. Frontend Build
echo [2/4] Frontend (Vite/React) derleniyor...
cd frontend
call npm run build
cd ..

:: 4. Dosyaları Hazırlama
echo [3/4] Kaynaklar kopyalaniyor...
copy "src\assets\icon.ico" "frontend\icon.ico" /Y
copy "frontend\license.txt" "frontend\license.txt" /Y
if not exist "frontend\extraResources" mkdir "frontend\extraResources"
if exist "frontend\extraResources\python" rd /S /Q "frontend\extraResources\python"
:: PyInstaller COLLECT puts files in dist/python
xcopy "dist\python" "frontend\extraResources\python" /E /I /Y

:: Copy ffmpeg as well (extraResources/python needs it or it should be global)
if exist "ffmpeg" (
    echo FFmpeg kopyalaniyor...
    if not exist "frontend\extraResources\python\ffmpeg" mkdir "frontend\extraResources\python\ffmpeg"
    xcopy "ffmpeg" "frontend\extraResources\python\ffmpeg" /E /I /Y
)

:: 5. Electron-Builder ile Installer Oluşturma
echo [4/4] Installer (Kurulum Dosyasi) olusturuluyor...
cd frontend
call npm run dist
cd ..

echo.
echo ==================================================
echo Islem Tamamlandi!
echo Kurulum dosyasi: frontend/dist-electron/
echo ==================================================
pause
