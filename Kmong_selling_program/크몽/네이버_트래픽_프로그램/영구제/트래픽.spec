# -*- mode: python ; coding: utf-8 -*-

UI_PATH = "로그인.ui"
UI_PATH2 = "트래픽(영구제).ui"

add_file = [(UI_PATH, '.'), (UI_PATH2, '.')]

a = Analysis(
    ['트래픽.py'],
    pathex=[],
    binaries=[],
    datas=add_file,
    hiddenimports=[
        'selenium.webdriver.chrome.webdriver',
        'selenium.webdriver.chrome.options',
        'selenium.webdriver.chrome.service',
        'selenium.webdriver.common.service',
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
    a.binaries,
    a.datas,
    [],
    name='트래픽',
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
