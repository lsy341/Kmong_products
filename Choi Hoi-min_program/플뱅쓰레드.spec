# -*- mode: python ; coding: utf-8 -*-

UI_PATH = "블로그대행사_외주.ui"

add_file = [(UI_PATH, '.')]

a = Analysis(
    ['플뱅쓰레드.py'],
    pathex=[],
    binaries=[],
    datas=add_file,
    hiddenimports=[],
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
    a.binaries,
    a.datas,
    [],
    name='플뱅쓰레드',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
