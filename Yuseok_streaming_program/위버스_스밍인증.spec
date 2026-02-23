# -*- mode: python ; coding: utf-8 -*-

UI_PATH = "로그인.ui"
UI_PATH2 = "위버스_스밍.ui"

add_file = [(UI_PATH, '.'), (UI_PATH2, '.'), ('C:\\Users\\user\\AppData\\Local\\Programs\\Python\\Python312\\Lib\\site-packages\\autoit\\lib\\AutoItX3_x64.dll', 'autoit\\lib')]

a = Analysis(
    ['위버스_스밍인증.py'],
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
    name='위버스_스밍인증',
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
