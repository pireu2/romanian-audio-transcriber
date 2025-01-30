block_cipher = None

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[
        (os.path.join("vendor", "ffmpeg", "ffmpeg.exe"), "vendor/ffmpeg"),
        (
            os.path.join("whisper.cpp", "build", "bin", "Release", "whisper-cli.exe"),
            "whisper.cpp/build/bin/Release",
        ),
    ],
    datas=[
        (os.path.join("whisper.cpp", "models", "ggml-base.bin"), "whisper.cpp/models"),
        ("transcriber.py", "."),
    ],
    hiddenimports=[],
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

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="Romanian Audio Transcriber",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    onefile=True,
    icon="icon.ico",
)
