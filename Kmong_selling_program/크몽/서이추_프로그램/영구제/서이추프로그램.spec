# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules

UI_PATH = "로그인.ui"
UI_PATH2 = "서이추프로그램(영구제).ui"

add_file = [(UI_PATH, '.'), (UI_PATH2, '.')]

hidden = collect_submodules('selenium') + collect_submodules('trio') + collect_submodules('trio_websocket')

a = Analysis(
    ['서이추프로그램.py'],
    pathex=[],
    binaries=[],
    datas=add_file,
    hiddenimports=hidden,
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
    name='서이추프로그램',
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
