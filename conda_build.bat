@echo off
echo ==============================================
echo Anaconda Build Scripti (PAU Transkript)
echo ==============================================

echo [1/3] Anaconda ortami aktif ediliyor...
call conda activate whisper_env

echo [2/3] Eksik bagimliliklar kontrol ediliyor...
pip install pyparsing regex

echo [3/3] PyInstaller build islemi basliyor...

pyinstaller --noconfirm --clean WhisperTranscriber.spec

echo [3/3] Gerekli klasorler ve dosyalar kopyalaniyor...
if not exist "dist\WhisperTranscriber\models"  mkdir "dist\WhisperTranscriber\models"
if not exist "dist\WhisperTranscriber\outputs" mkdir "dist\WhisperTranscriber\outputs"
if not exist "dist\WhisperTranscriber\logs"    mkdir "dist\WhisperTranscriber\logs"

xcopy "ffmpeg"      "dist\WhisperTranscriber\ffmpeg"  /E /I /Y
copy  "config.json" "dist\WhisperTranscriber\config.json"

echo.
echo ==============================================
echo Build basariyla tamamlandi!
echo Ciktilar: dist\WhisperTranscriber\
echo Calistirmak icin: dist\WhisperTranscriber\WhisperTranscriber.exe
echo ==============================================
pause
