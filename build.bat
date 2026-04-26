@echo off
echo ==============================================
echo PAU Akademik Transkript Asistanı Build Script
echo ==============================================

if not exist ".venv\Scripts\activate" (
    echo [HATA] .venv klasoru bulunamadi. Lutfen once "python -m venv .venv" komutunu calistirin ve gereksinimleri yukleyin.
    pause
    exit /b
)

echo [1/3] Sanal ortam aktif ediliyor...
call .venv\Scripts\activate

echo [2/3] Eksik bagimliliklar kontrol ediliyor...
pip install pyparsing regex

echo [3/3] PyInstaller build islemi basliyor...
pyinstaller --noconfirm --clean WhisperTranscriber.spec

echo [3/3] Gerekli klasorler kopyalaniyor...
if not exist "dist\WhisperTranscriber\models" mkdir "dist\WhisperTranscriber\models"
if not exist "dist\WhisperTranscriber\outputs" mkdir "dist\WhisperTranscriber\outputs"

xcopy "ffmpeg" "dist\WhisperTranscriber\ffmpeg" /E /I /Y
copy "config.json" "dist\WhisperTranscriber\config.json"

echo.
echo ==============================================
echo Build basariyla tamamlandi! 
echo Ciktilar "dist/WhisperTranscriber" klasorundedir.
echo ==============================================
pause
