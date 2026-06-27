$ErrorActionPreference = "Stop"

$Root = Resolve-Path "$PSScriptRoot\..\.."
Set-Location $Root

python -m pip install -U pip
python -m pip install -e ".[gui,enterprise]" pyinstaller

Remove-Item -Recurse -Force build, dist, dist_release -ErrorAction SilentlyContinue
pyinstaller packaging/pyinstaller/mediaqc_cli.spec --noconfirm --clean
pyinstaller packaging/pyinstaller/mediaqc_gui.spec --noconfirm --clean
python packaging/scripts/make_release.py --platform windows --dist dist --output dist_release
