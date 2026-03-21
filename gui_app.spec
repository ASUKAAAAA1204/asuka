# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gui_app.py'],
    pathex=[],
    binaries=[],
    datas=[('local_file_manager', 'local_file_manager'), ('document_analyzer', 'document_analyzer'), ('gui', 'gui'), ('RESOURCE', 'RESOURCE')],
    hiddenimports=['sklearn.feature_extraction.text', 'sklearn.metrics.pairwise'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytesseract', 'ffmpeg'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='gui_app',
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
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='gui_app',
)
