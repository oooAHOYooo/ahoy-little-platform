# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Ahoy Indie Media Desktop App
# Platform-specific: macOS uses BUNDLE, Windows uses onefile EXE

import os
import sys
from pathlib import Path

block_cipher = None

# Get version from ahoy/version.py
import os
# Spec file is in packaging/, project root is one level up
PROJECT_ROOT = Path(__file__).parent.parent if '__file__' in globals() else Path.cwd().parent if Path.cwd().name == 'packaging' else Path.cwd()
try:
    sys.path.insert(0, str(PROJECT_ROOT))
    from ahoy.version import __version__
except ImportError:
    __version__ = "0.2.0"

a = Analysis(
    ['../desktop_main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('../templates', 'templates'),
        ('../static', 'static'),
        ('../data', 'data'),
        ('../ahoy', 'ahoy'),
    ],
    hiddenimports=[
        'flask',
        'pywebview',
        'webview',
        'structlog',
        'bcrypt',
        'flask_limiter',
        'flask_cors',
        'flask_login',
        'flask_bcrypt',
        'flask_wtf',
        'sqlalchemy',
        'alembic',
        'psycopg',
        'sentry_sdk',
        'werkzeug',
        'jinja2',
        'markupsafe',
        'itsdangerous',
        'click',
        'python_dotenv',
        'gunicorn',
        'requests',
        'marshmallow',
        'pyjwt',
        'email_validator',
        'limits',
        'python_json_logger',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Windows: onefile EXE
if sys.platform == 'win32':
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='AhoyIndieMedia',
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
        icon='icons/ahoy.ico',
        onefile=True,
    )
# macOS: APP bundle
else:
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='AhoyIndieMedia',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon='icons/ahoy.icns',
    )
    
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='AhoyIndieMedia',
    )
    
    app = BUNDLE(
        coll,
        name='AhoyIndieMedia.app',
        icon='icons/ahoy.icns',
        bundle_identifier='com.ahoyindiemedia.desktop',
        info_plist={
            'CFBundleName': 'Ahoy Indie Media',
            'CFBundleDisplayName': 'Ahoy Indie Media',
            'CFBundleVersion': __version__,
            'CFBundleShortVersionString': __version__,
            'CFBundlePackageType': 'APPL',
            'CFBundleSignature': '????',
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,
            'LSMinimumSystemVersion': '10.13',
        },
    )
