# fmea_app.spec
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main_app.py'],
    pathex=['.'],  # Add any paths where your modules are located
    binaries=[],
    datas=[
        ('media/topbar/back_arrow.png', '.'),  # Add paths to your icon files
        ('media/topbar/new_file.png', '.'),
        ('media/topbar/save.png', '.'),
        ('media/topbar/load.png', '.'),
        ('media/topbar/undo.png', '.'),
        ('media/topbar/previous.png', '.'),
        ('media/topbar/next.png', '.'),
    ],
    hiddenimports=['PIL', 'PIL._imagingtk'],  # Add any hidden imports here
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FMEAApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Change to True if you want to see console output
    icon='Ofmea_logo.png'  # Add path to your app icon if you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FMEAApp',
)
