# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],  # 主程式進入點
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources'),          # 包含所有資源檔案
        ('src', 'src'),                      # 包含整個 src 目錄
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=True,  # 改為 True 可以加快啟動速度
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # 這個選項使其成為 onedir 模式
    name='permission_controll',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 設為 False 來隱藏控制台窗口
    icon='resources/images/icon.ico' if os.path.exists('resources/images/icon.ico') else None,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# COLLECT 要在 EXE 之後作為獨立的語句
COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='permission_controll',
)