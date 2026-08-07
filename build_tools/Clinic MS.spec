# -*- mode: python ; coding: utf-8 -*-
import sys
import os

SPEC_DIR = SPECPATH
ROOT_DIR = os.path.dirname(SPEC_DIR)

sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, SPEC_DIR)

from version import APP_VERSION, APP_NAME

EXE_NAME = f"{APP_NAME} v{APP_VERSION}"

a = Analysis(
    [os.path.join(SPEC_DIR, 'desktop_app.py')],
    pathex=[ROOT_DIR, SPEC_DIR],
    binaries=[],
    datas=[
        (os.path.join(ROOT_DIR, 'static'), 'static'),
        (os.path.join(ROOT_DIR, 'templates'), 'templates'),
        (os.path.join(ROOT_DIR, 'docs'), 'docs'),
        (os.path.join(SPEC_DIR, 'version.py'), '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['generate_license'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=EXE_NAME,
    icon=os.path.join(SPEC_DIR, 'app_icon.ico'),
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
