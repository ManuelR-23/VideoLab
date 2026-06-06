# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

# Incluir todos los archivos de datos de MediaPipe (modelos TFLite, etc.)
mediapipe_datas = collect_data_files('mediapipe', includes=['**/*'])

# Archivos de datos propios del proyecto
project_datas = [
    ('ui/styles.qss', 'ui'),
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=collect_dynamic_libs('mediapipe'),
    datas=mediapipe_datas + project_datas,
    hiddenimports=[
        'mediapipe.python._framework_bindings',
        'mediapipe.tasks',
        'mediapipe.tasks.python',
        'mediapipe.tasks.python.vision',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='VideoLab',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Sin ventana de terminal en macOS
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VideoLab',
)

app = BUNDLE(
    coll,
    name='VideoLab.app',
    icon=None,
    bundle_identifier='com.videolab.app',
    info_plist={
        'NSCameraUsageDescription': 'VideoLab necesita acceso a la cámara para capturar vídeo.',
        'NSMicrophoneUsageDescription': 'VideoLab puede acceder al micrófono.',
    },
)
