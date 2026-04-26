@echo off
echo ==================================================
echo PAU IIBF Transkript - Paketleme Betigi (Alpha v0.1)
echo ==================================================

:: 1. Python Sanal Ortam Kontrolü
if not exist ".venv\Scripts\activate" (
    echo [HATA] .venv klasoru bulunamadi.
    pause
    exit /b
)

:: 2. Python Backend Build
echo [1/4] Python Backend paketleniyor...
call .venv\Scripts\activate
pip install uvicorn fastapi
pyinstaller --noconfirm --clean server.spec

:: 3. Frontend Build
echo [2/4] Frontend (Vite/React) derleniyor...
cd frontend
call npm run build
cd ..

:: 4. Dosyaları Hazırlama
echo [3/4] Kaynaklar kopyalaniyor...
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
