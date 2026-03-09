"""
spec.spec
=========
PyInstaller specification file.

This file instructs PyInstaller on how to build the executable, specifying:
    - The main entry point (main.py).
    - Data files to bundle (assets folder).
    - Hidden imports that PyInstaller might miss (e.g., for Sumy).
    - Application metadata (name, icon).
"""

# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# --- Data files to bundle with the application ---
# We need to include the entire 'assets' directory (themes, icons).
# We also need to include data files for the 'sumy' library (stopwords).
datas = []
datas += collect_data_files('sumy')
datas += [('assets', 'assets')]

# --- Main application script and settings ---
a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    # --- Hidden imports ---
    # PyInstaller sometimes fails to detect all necessary imports, especially
    # those used by libraries like Sumy and Transformers. We list them here.
    hiddenimports=[
        'sumy.summarizers.lsa',
        'sumy.summarizers.lex_rank',
        'sumy.summarizers.luhn',
        'sumy.summarizers.text_rank',
        'sumy.nlp.stemmers',
        'sumy.nlp.tokenizers',
        'pynput.keyboard._win32',
        'pynput.mouse._win32',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# --- Executable settings ---
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AI-Powered-Text-Summarizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to False for a GUI application (no console window)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/icon.ico',  # Path to the application icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AI-Powered-Text-Summarizer',
)
