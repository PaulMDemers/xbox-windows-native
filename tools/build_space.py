"""Check both the output filesystem and WSL's actual Windows backing volume."""
import base64
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess


def require_space(output, minimum_gib=20):
    anchor = Path(output).resolve()
    while not anchor.exists():
        anchor = anchor.parent
    checks = [{'kind': 'output filesystem', 'path': str(anchor),
               'free_bytes': shutil.disk_usage(anchor).free}]
    if 'microsoft' in platform.release().lower():
        distro = os.environ.get('WSL_DISTRO_NAME')
        if not distro:
            raise RuntimeError('Cannot identify WSL backing volume: WSL_DISTRO_NAME missing')
        # Quote the distro as data; do not interpolate it into shell syntax.
        quoted = distro.replace("'", "''")
        script = """$ErrorActionPreference='Stop'
$d=@(Get-ChildItem HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Lxss | Where-Object { $_.GetValue('DistributionName') -eq '%s' })
if($d.Count -ne 1) { throw 'Cannot identify WSL registry entry' }
$base=$d[0].GetValue('BasePath').Replace('\\\\?\\','')
$drive=[IO.DriveInfo]::new([IO.Path]::GetPathRoot($base))
@{kind='WSL backing volume';path=$drive.Name;free_bytes=$drive.AvailableFreeSpace} | ConvertTo-Json -Compress
""" % quoted
        encoded = base64.b64encode(script.encode('utf-16le')).decode('ascii')
        exe = shutil.which('powershell.exe')
        if not exe:
            raise RuntimeError('Windows PowerShell is required to check WSL backing-volume space')
        raw = subprocess.check_output([exe, '-NoProfile', '-NonInteractive',
                                       '-EncodedCommand', encoded], timeout=30)
        checks.append(json.loads(raw.decode('utf-8-sig')))
    needed = minimum_gib * 1024**3
    for check in checks:
        if check['free_bytes'] < needed:
            raise RuntimeError(f"Insufficient space on {check['kind']} {check['path']}: "
                               f"{check['free_bytes']} bytes free; require {needed}")
    return {'minimum_free_gib': minimum_gib, 'checks': checks,
            'scope': 'Preflight reserve, not a guarantee against concurrent host writes'}
