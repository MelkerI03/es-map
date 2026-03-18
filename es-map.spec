block_cipher = None

a = Analysis(
    ['src/es_map/cli.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/es_map/graph/templates', 'src/es_map/graph/templates'),
        ('src/es_map/graph/static', 'src/es_map/graph/static'),
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
    [],
    exclude_binaries=True,
    name='es-map',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # CLI app
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='es-map',
)
