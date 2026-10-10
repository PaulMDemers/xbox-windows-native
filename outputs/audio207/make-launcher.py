"""Acquire both leases before creating any run state; preserve existing launcher body."""
from pathlib import Path
k=Path(__file__).resolve().parent
s=(k.parent/'video-surface-history/Invoke-Exclusive.ps1').read_text()
anchor="& (Join-Path $integration 'with_xbox_resource.ps1') -Resource xemu -Action {"
assert s.count(anchor)==1
s=s.replace(anchor,"if ($env:XBOX_XEMU_MODE -ne 'exclusive') { throw 'Audio caller must hold exclusive xemu lease' }\n& {")
s=s.replace('-TaskId $InstanceTask -XemuPath $xemu',"-InstanceRoot (Join-Path $workspace 'work/instances') -TaskId $InstanceTask -XemuPath $xemu")
(k/'Invoke-Audio.ps1').write_text(s)
