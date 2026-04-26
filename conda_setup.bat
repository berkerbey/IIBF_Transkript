@echo off
echo ==============================================
echo Anaconda Kurulum Scripti (PAU Transkript)
echo ==============================================

echo [1/3] "whisper_env" adinda yeni bir Anaconda ortami olusturuluyor...
call conda create -n whisper_env python=3.11 -y

echo [2/3] Ortam aktif ediliyor...
call conda activate whisper_env

echo [3/3] Gereksinimler ve FFmpegendiriliyor...
pip install -r requirements.txt
python setup.py

echo.
echo ==============================================
echo Kurulum tamamlandi!
echo Uygulamayi calistirmak icin Anaconda Prompt uzerinden:
echo 1. conda activate whisper_env
echo 2. python run.py
echo ==============================================
pause
