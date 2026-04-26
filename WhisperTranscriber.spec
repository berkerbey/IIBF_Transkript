# -*- mode: python ; coding: utf-8 -*-
import sys
sys.setrecursionlimit(5000)


from PyInstaller.utils.hooks import collect_data_files

faster_whisper_datas = collect_data_files('faster_whisper')

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[('src\\assets', 'src\\assets')] + faster_whisper_datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytest', 'tensorboard', 'matplotlib', 'cycler', 'scipy', 'IPython', 'jupyter'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WhisperTranscriber',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/assets/icon.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WhisperTranscriber',
)
