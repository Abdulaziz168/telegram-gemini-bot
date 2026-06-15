# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Telegram Gemini Bot.
Builds a single portable .exe that works on any Windows PC.
"""
from PyInstaller.utils.hooks import collect_all, collect_submodules, collect_data_files
import os

# Get the directory where this spec file lives
spec_dir = os.path.dirname(os.path.abspath(SPEC))

# Collect all data and hidden imports
datas = []
binaries = []
hiddenimports = []

# Add .env file to bundle (so tokens travel with exe)
env_file = os.path.join(spec_dir, '.env')
if os.path.exists(env_file):
    datas += [(env_file, '.')]

# Collect all dependencies
packages_to_collect = [
    'aiogram',
    'google.generativeai',
    'google.ai',
    'google.api_core',
    'google.auth',
    'google.protobuf',
    'grpc',
    'groq',
    'PIL',
    'reportlab',
    'aiohttp',
    'aiofiles',
    'dotenv',
    'certifi',
    'httpx',
    'httpcore',
    'anyio',
    'sniffio',
    'h11',
    'multidict',
    'yarl',
    'aiosignal',
    'frozenlist',
    'attrs',
    'idna',
    'charset_normalizer',
]

for pkg in packages_to_collect:
    try:
        tmp_ret = collect_all(pkg)
        datas += tmp_ret[0]
        binaries += tmp_ret[1]
        hiddenimports += tmp_ret[2]
    except Exception as e:
        print(f"Warning: Could not collect {pkg}: {e}")

# Additional hidden imports that may be missed
hiddenimports += [
    'google.generativeai',
    'google.generativeai.types',
    'google.ai.generativelanguage',
    'google.api_core',
    'google.auth',
    'google.auth.transport',
    'google.auth.transport.requests',
    'google.protobuf',
    'grpc',
    'grpc._cython',
    'groq',
    'PIL',
    'PIL.Image',
    'reportlab',
    'reportlab.lib',
    'reportlab.platypus',
    'reportlab.pdfbase',
    'sqlite3',
    'asyncio',
    'aiohttp',
    'aiofiles',
    'dotenv',
    'certifi',
    'encodings',
    'encodings.utf_8',
    'encodings.ascii',
    'encodings.latin_1',
    'encodings.idna',
    'json',
    'logging',
    'ssl',
    'http',
    'http.client',
    'urllib',
    'urllib.parse',
    'email',
    'email.mime',
    'email.mime.text',
    'email.mime.multipart',
    'concurrent',
    'concurrent.futures',
    'multiprocessing',
    'pkg_resources',
    'httpx',
    'httpcore',
    'anyio',
    'anyio._backends',
    'anyio._backends._asyncio',
    'sniffio',
    'h11',
    'multidict',
    'yarl',
    'aiosignal',
    'frozenlist',
    'attrs',
    'idna',
    'charset_normalizer',
    'proto',
    'proto.marshal',
    'proto.marshal.rules',
    'unittest',
    'unittest.mock',
]

# Remove duplicates
hiddenimports = list(set(hiddenimports))

# Add project source files as data
project_folders = ['handlers', 'services', 'database', 'utils']
for folder in project_folders:
    folder_path = os.path.join(spec_dir, folder)
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            if file.endswith('.py'):
                datas += [(os.path.join(folder_path, file), folder)]

a = Analysis(
    ['main.py'],
    pathex=[spec_dir],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'scipy',
        'pandas',
        'numpy',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
    ],
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
    name='GeminiBot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Console=True to see logs; set to False for no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
