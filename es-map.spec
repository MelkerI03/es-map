from PyInstaller.utils.hooks import collect_dynamic_libs

block_cipher = None

a = Analysis(
    ['src/es_map/cli.py'],
    pathex=[],
    binaries=collect_dynamic_libs('pydantic_core'),
    datas=[
        ('src/es_map/graph', 'graph'),
        ('src/es_map/icons', 'icons'),
    ],
    hiddenimports=[
        'matplotlib.backends.backend_svg',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    exclude_binaries=False,
    name='es-map',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)
