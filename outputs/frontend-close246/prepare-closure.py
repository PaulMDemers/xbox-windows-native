"""Derive explicit once-only246 process/copy closure helpers; no execution here."""
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'gpu-lifecycle245'
p=k/'record-processes.ps1';assert not p.exists()
s=(old/'record-processes002.ps1').read_text().replace('foreach($phase in 244,245)','foreach($phase in 246)').replace('$kit=Join-Path $ws "outputs/gpu-lifecycle$phase"','$kit=Join-Path $ws "outputs/frontend-close$phase"')
a="unified_sessions=@{build00390573='closed0';build00467046='closed0';build0053548='closed0';matrix24482152='closed1';matrix24519660='closed0'}"
assert a in s;s=s.replace(a,"unified_sessions=@{build45619='closed0';matrix11204='closed0'}")
p.write_text(s)
p=k/'portable-offload.ps1';assert not p.exists()
s=(old/'portable-offload.ps1').read_text().replace('closed-portable-245-final','closed-portable-246').replace('foreach($phase in 245)','foreach($phase in 246)').replace('outputs/gpu-lifecycle245','outputs/frontend-close246').replace("Write-Output 'Closed242 portable copies hash verified on E with original paths preserved'","Write-Output 'Closed246 portable copy verified on E; original path retained'")
p.write_text(s)
print('246 exact process and portable copy closure helpers prepared; no execution')
