# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

import os

spec_root = os.path.abspath(SPECPATH)

tmp_ret = collect_all('PIL')
datas = tmp_ret[0]; tmp_ret[1]; tmp_ret[2]
datas += [('data', 'data'), ('engine', 'engine'), ('animation-maker', 'animation-maker'), ('photo-studio', 'photo-studio')]

block_cipher = None

a = Analysis(['main.py'],
    pathex=[spec_root],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False)


b = Analysis(['animation-maker.py'],
    pathex=[spec_root],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False)

c = Analysis(['photo-studio.py'],
pathex=[spec_root],
binaries=[],
datas=datas,
hiddenimports=[],
hookspath=[],
hooksconfig=[],
runtime_hooks=[],
excludes=[],
win_no_prefer_redirects=False,
win_private_assemblies=False,
cipher=block_cipher,
noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True)

pyz = PYZ(b.pure, b.zipped_data, cipher=block_cipher)

exe2 = EXE(pyz,
    b.scripts,
    [],
    exclude_binaries=True,
    name='animation maker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True)

pyz = PYZ(c.pure, c.zipped_data, cipher=block_cipher)

exe3 = EXE(pyz,
    c.scripts,
    [],
    exclude_binaries=True,
    name='photo studio',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True)

coll = COLLECT(exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    exe2,
    b.binaries,
    b.zipfiles,
    b.datas,
    exe3,
    c.binaries,
    c.zipfiles,
    c.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='main')
