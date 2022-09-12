# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


ikobconfig_a = Analysis(
            ['ikobconfig.py'],
            pathex=[],
            binaries=[],
            datas=[],
            hiddenimports=[],
            hookspath=[],
            hooksconfig={},
            runtime_hooks=[],
            excludes=[],
            win_no_prefer_redirects=False,
            win_private_assemblies=False,
            cipher=block_cipher,
            noarchive=False)
ikobconfig_pyz = PYZ(
            ikobconfig_a.pure,
            ikobconfig_a.zipped_data,
            cipher=block_cipher)
ikobconfig_exe = EXE(
            ikobconfig_pyz,
            ikobconfig_a.scripts,
            [],
            exclude_binaries=True,
            name='ikobconfig',
            debug=False,
            bootloader_ignore_signals=False,
            strip=False,
            upx=True,
            console=False,
            disable_windowed_traceback=False,
            target_arch=None,
            codesign_identity=None,
            entitlements_file=None )

ikobrunner_a = Analysis(
            ['ikobrunner.py'],
            pathex=[],
            binaries=[],
            datas=[],
            hiddenimports=[],
            hookspath=[],
            hooksconfig={},
            runtime_hooks=[],
            excludes=[],
            win_no_prefer_redirects=False,
            win_private_assemblies=False,
            cipher=block_cipher,
            noarchive=False)
ikobrunner_pyz = PYZ(
            ikobrunner_a.pure,
            ikobrunner_a.zipped_data,
            cipher=block_cipher)
ikobrunner_exe = EXE(
            ikobrunner_pyz,
            ikobrunner_a.scripts,
            [],
            exclude_binaries=True,
            name='ikobrunner',
            debug=False,
            bootloader_ignore_signals=False,
            strip=False,
            upx=True,
            console=False,
            disable_windowed_traceback=False,
            target_arch=None,
            codesign_identity=None,
            entitlements_file=None )

skims_a = Analysis(
            ['skimsberekenen.py'],
            pathex=[],
            binaries=[],
            datas=[],
            hiddenimports=[],
            hookspath=[],
            hooksconfig={},
            runtime_hooks=[],
            excludes=[],
            win_no_prefer_redirects=False,
            win_private_assemblies=False,
            cipher=block_cipher,
            noarchive=False)
skims_pyz = PYZ(
            skims_a.pure,
            skims_a.zipped_data,
            cipher=block_cipher)
skims_exe = EXE(
            skims_pyz,
            skims_a.scripts,
            [],
            exclude_binaries=True,
            name='skimsberekenen',
            debug=False,
            bootloader_ignore_signals=False,
            strip=False,
            upx=True,
            console=True,
            disable_windowed_traceback=False,
            target_arch=None,
            codesign_identity=None,
            entitlements_file=None )

verdeling_a = Analysis(
            ['Verdelingovergroepen.py'],
            pathex=[],
            binaries=[],
            datas=[],
            hiddenimports=[],
            hookspath=[],
            hooksconfig={},
            runtime_hooks=[],
            excludes=[],
            win_no_prefer_redirects=False,
            win_private_assemblies=False,
            cipher=block_cipher,
            noarchive=False)
verdeling_pyz = PYZ(
            verdeling_a.pure,
            verdeling_a.zipped_data,
            cipher=block_cipher)
verdeling_exe = EXE(
            verdeling_pyz,
            verdeling_a.scripts,
            [],
            exclude_binaries=True,
            name='Verdelingovergroepen',
            debug=False,
            bootloader_ignore_signals=False,
            strip=False,
            upx=True,
            console=True,
            disable_windowed_traceback=False,
            target_arch=None,
            codesign_identity=None,
            entitlements_file=None )

enkel_a = Analysis(
            ['Gewichtenberekenenenkelscenarios.py'],
            pathex=[],
            binaries=[],
            datas=[],
            hiddenimports=[],
            hookspath=[],
            hooksconfig={},
            runtime_hooks=[],
            excludes=[],
            win_no_prefer_redirects=False,
            win_private_assemblies=False,
            cipher=block_cipher,
            noarchive=False)
enkel_pyz = PYZ(
            enkel_a.pure,
            enkel_a.zipped_data,
            cipher=block_cipher)
enkel_exe = EXE(
            enkel_pyz,
            enkel_a.scripts,
            [],
            exclude_binaries=True,
            name='Gewichtenberekenenenkelscenarios',
            debug=False,
            bootloader_ignore_signals=False,
            strip=False,
            upx=True,
            console=True,
            disable_windowed_traceback=False,
            target_arch=None,
            codesign_identity=None,
            entitlements_file=None )

combi_a = Analysis(
            ['Gewichtenberekenencombis.py'],
            pathex=[],
            binaries=[],
            datas=[],
            hiddenimports=[],
            hookspath=[],
            hooksconfig={},
            runtime_hooks=[],
            excludes=[],
            win_no_prefer_redirects=False,
            win_private_assemblies=False,
            cipher=block_cipher,
            noarchive=False)
combi_pyz = PYZ(
            combi_a.pure,
            combi_a.zipped_data,
            cipher=block_cipher)
combi_exe = EXE(
            combi_pyz,
            combi_a.scripts,
            [],
            exclude_binaries=True,
            name='Gewichtenberekenencombis',
            debug=False,
            bootloader_ignore_signals=False,
            strip=False,
            upx=True,
            console=True,
            disable_windowed_traceback=False,
            target_arch=None,
            codesign_identity=None,
            entitlements_file=None )

ontplooiing_a = Analysis(
            ['Ontplooiingsmogelijkhedenechteinwoners.py'],
            pathex=[],
            binaries=[],
            datas=[],
            hiddenimports=[],
            hookspath=[],
            hooksconfig={},
            runtime_hooks=[],
            excludes=[],
            win_no_prefer_redirects=False,
            win_private_assemblies=False,
            cipher=block_cipher,
            noarchive=False)
ontplooiing_pyz = PYZ(
            ontplooiing_a.pure,
            ontplooiing_a.zipped_data,
            cipher=block_cipher)
ontplooiing_exe = EXE(
            ontplooiing_pyz,
            ontplooiing_a.scripts,
            [],
            exclude_binaries=True,
            name='Ontplooiingsmogelijkhedenechteinwoners',
            debug=False,
            bootloader_ignore_signals=False,
            strip=False,
            upx=True,
            console=True,
            disable_windowed_traceback=False,
            target_arch=None,
            codesign_identity=None,
            entitlements_file=None )

potentie_a = Analysis(
            ['Potentiebedrijven.py'],
            pathex=[],
            binaries=[],
            datas=[],
            hiddenimports=[],
            hookspath=[],
            hooksconfig={},
            runtime_hooks=[],
            excludes=[],
            win_no_prefer_redirects=False,
            win_private_assemblies=False,
            cipher=block_cipher,
            noarchive=False)
potentie_pyz = PYZ(
            potentie_a.pure,
            potentie_a.zipped_data,
            cipher=block_cipher)
potentie_exe = EXE(
            potentie_pyz,
            potentie_a.scripts,
            [],
            exclude_binaries=True,
            name='Potentiebedrijven',
            debug=False,
            bootloader_ignore_signals=False,
            strip=False,
            upx=True,
            console=True,
            disable_windowed_traceback=False,
            target_arch=None,
            codesign_identity=None,
            entitlements_file=None )

arbeid_a = Analysis(
            ['Concurrentieomarbeidsplaatsen.py'],
            pathex=[],
            binaries=[],
            datas=[],
            hiddenimports=[],
            hookspath=[],
            hooksconfig={},
            runtime_hooks=[],
            excludes=[],
            win_no_prefer_redirects=False,
            win_private_assemblies=False,
            cipher=block_cipher,
            noarchive=False)
arbeid_pyz = PYZ(
            arbeid_a.pure,
            arbeid_a.zipped_data,
            cipher=block_cipher)

arbeid_exe = EXE(
            arbeid_pyz,
            arbeid_a.scripts,
            [],
            exclude_binaries=True,
            name='Concurrentieomarbeidsplaatsen',
            debug=False,
            bootloader_ignore_signals=False,
            strip=False,
            upx=True,
            console=True,
            disable_windowed_traceback=False,
            target_arch=None,
            codesign_identity=None,
            entitlements_file=None )

inwoners_a = Analysis(
            ['Concurrentieominwoners.py'],
            pathex=[],
            binaries=[],
            datas=[],
            hiddenimports=[],
            hookspath=[],
            hooksconfig={},
            runtime_hooks=[],
            excludes=[],
            win_no_prefer_redirects=False,
            win_private_assemblies=False,
            cipher=block_cipher,
            noarchive=False)
inwoners_pyz = PYZ(
            inwoners_a.pure,
            inwoners_a.zipped_data,
            cipher=block_cipher)

inwoners_exe = EXE(
            inwoners_pyz,
            inwoners_a.scripts,
            [],
            exclude_binaries=True,
            name='Concurrentieominwoners',
            debug=False,
            bootloader_ignore_signals=False,
            strip=False,
            upx=True,
            console=True,
            disable_windowed_traceback=False,
            target_arch=None,
            codesign_identity=None,
            entitlements_file=None )

coll = COLLECT(ikobconfig_exe,
               ikobconfig_a.binaries,
               ikobconfig_a.zipfiles,
               ikobconfig_a.datas,
               ikobrunner_exe,
               ikobrunner_a.binaries,
               ikobrunner_a.zipfiles,
               ikobrunner_a.datas,
               skims_exe,
               skims_a.binaries,
               skims_a.zipfiles,
               skims_a.datas,
               verdeling_exe,
               verdeling_a.binaries,
               verdeling_a.zipfiles,
               verdeling_a.datas,
               enkel_exe,
               enkel_a.binaries,
               enkel_a.zipfiles,
               enkel_a.datas,
               combi_exe,
               combi_a.binaries,
               combi_a.zipfiles,
               combi_a.datas,
               ontplooiing_exe,
               ontplooiing_a.binaries,
               ontplooiing_a.zipfiles,
               ontplooiing_a.datas,
               potentie_exe,
               potentie_a.binaries,
               potentie_a.zipfiles,
               potentie_a.datas,
               arbeid_exe,
               arbeid_a.binaries,
               arbeid_a.zipfiles,
               arbeid_a.datas,
               inwoners_exe,
               inwoners_a.binaries,
               inwoners_a.zipfiles,
               inwoners_a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='ikob')
