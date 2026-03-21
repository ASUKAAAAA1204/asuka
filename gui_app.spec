# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['gui_app.py'],
             pathex=['d:\\game2\\wc\\git2'],
             binaries=[],
             datas=[('C:\\Users\\33671\\AppData\\Local\\Programs\\Python\\Python313\\Lib\\site-packages\\jieba', 'jieba')],
             hiddenimports=['numpy', 'pandas', 'openpyxl', 'pdfminer', 'docx', 'PIL'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['scipy', 'sklearn'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='gui_app',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=False )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               upx_exclude=[],
               name='gui_app')
