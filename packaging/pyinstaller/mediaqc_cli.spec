# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path


ROOT = Path(SPECPATH).parents[1]


def collect_tree(source: str, target: str):
    base = ROOT / source
    if not base.exists():
        return []
    return [(str(path), str(Path(target) / path.relative_to(base).parent)) for path in base.rglob("*") if path.is_file()]


datas = []
datas += collect_tree("config", "config")
datas += collect_tree("profiles", "profiles")
datas += collect_tree("mediaqc/templates", "mediaqc/templates")
datas += collect_tree("mediaqc/dashboard_templates", "mediaqc/dashboard_templates")
datas += collect_tree("tools", "tools")


a = Analysis(
    [str(ROOT / "packaging" / "pyinstaller" / "entrypoints" / "mediaqc_cli.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "mediaqc.enterprise.api",
        "mediaqc.gui.app",
        "uvicorn",
        "fastapi",
        "jinja2",
        "yaml",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="mediaqc",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="mediaqc-cli",
)
