# PyInstaller spec for Copycat Chess Engine UCI executable

import os
from PyInstaller.utils.hooks import collect_submodules

# Resolve project directory robustly (PyInstaller may exec spec where __file__ absent)
_cwd = os.getcwd()
project_dir = _cwd  # spec is invoked from project root when we run pyinstaller spec
src_dir = os.path.join(project_dir, 'src')

# Hidden imports (python-chess sometimes dynamic)
hidden_imports = collect_submodules('chess')

# Exclude heavy analysis/visualization modules not needed for UCI play
excludes = [
    'matplotlib', 'matplotlib.*',
    'seaborn', 'seaborn.*',
    'pandas', 'pandas.*',
    'networkx', 'networkx.*',
    'numpy.random._examples',
]

# Data files: include only essential JSONs to reduce size
ESSENTIAL_JSON = {
    'analysis_summary.json',
    'player_stats.json',
    'enhanced_player_stats.json',
    'enhanced_analysis.json'
}
datas = []
results_dir = os.path.join(project_dir, 'results')
if os.path.isdir(results_dir):
    for name in os.listdir(results_dir):
        if name in ESSENTIAL_JSON:
            datas.append((os.path.join(results_dir, name), 'results'))

# Inject version via environment (can be read inside engine if desired)
os.environ.setdefault('COPYCAT_VERSION', '0.5.0')

block_cipher = None

a = Analysis(
    ['copycat_uci.py'],
    pathex=[project_dir, src_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='copycat_uci',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
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
    name='copycat_uci'
)
