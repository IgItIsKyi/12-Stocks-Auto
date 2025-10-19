# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('templates', 'templates'), ('static', 'static')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

excluded_files = {
    '.env',
    '.gitignore',
    'Stocks Automation Notes.txt',
    'test.py',
}

def is_excluded(file_path):
    # Normalize to work on all OSes
    file_path = file_path.replace('\\', '/')
    if '__pycache__' in file_path:
        return True
    base = os.path.basename(file_path)
    return base in excluded_files

# Filter out excluded files from datas and binaries (if any were added manually)
a.datas = [d for d in a.datas if not is_excluded(d[0])]
a.binaries = [b for b in a.binaries if not is_excluded(b[0])]


pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='12StocksAuto',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='12StocksAuto',
)
