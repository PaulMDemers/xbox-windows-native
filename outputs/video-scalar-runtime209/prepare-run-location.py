"""New standalone runs on E:; no existing disk or backing chain relocation."""
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
original=k.parent/'video-surface-history/Invoke-Exclusive.ps1'
dest=k/'Invoke-209.ps1';assert not dest.exists()
s=original.read_text(encoding='utf-8')
s=s.replace('$run = Join-Path $workspace "work\\runs\\$RunId"', '$run = Join-Path "E:/Codex-private-artifacts/xbox-windows-feasibility/scalar209-runs" $RunId')
s=s.replace("(Join-Path $workspace 'work\\scratch')", "'E:/Codex-private-artifacts/xbox-windows-feasibility/scalar209-scratch'")
# Run.ps1 holds the exclusive xemu lease before this script creates anything.
s=s.replace("& (Join-Path $integration 'with_xbox_resource.ps1') -Resource xemu -Action {", '& {')
assert 'work\\runs\\$RunId' not in s
dest.write_text(s,encoding='utf-8',newline='\n')
for name in ['audit-emulator.py','supervise-emulator.py']:
 p=k/name;s=p.read_text(encoding='utf-8')
 s=s.replace("ws/('work/runs/nt5-scalar209-'+case)", "Path('/mnt/e/Codex-private-artifacts/xbox-windows-feasibility/scalar209-runs/nt5-scalar209-'+case)" if name=='audit-emulator.py' else "Path('E:/Codex-private-artifacts/xbox-windows-feasibility/scalar209-runs/nt5-scalar209-'+case)")
 p.write_text(s,encoding='utf-8',newline='\n')
p=k/'Run.ps1';s=p.read_text(encoding='utf-8')
s=s.replace("(Get-PSDrive C).Free - (Get-Item -LiteralPath $seed).Length", "(Get-PSDrive E).Free - (Get-Item -LiteralPath $seed).Length")
s=s.replace('(Join-Path $ws ("work/runs/nt5-scalar209-$Case"))', '(Join-Path "E:/Codex-private-artifacts/xbox-windows-feasibility/scalar209-runs" ("nt5-scalar209-$Case"))')
s=s.replace("-Resource build -Action {", "-Resource build -Action {\n & C:/Users/Paul/Desktop/ogxbox-linux/scripts/with_xbox_resource.ps1 -Resource xemu -Action {")
s=s.replace("../video-surface-history/Invoke-Exclusive.ps1", "Invoke-209.ps1")
s=s.rstrip()+'\n}\n'
p.write_text(s,encoding='utf-8',newline='\n')
print('New209 standalone locations on E; leases acquired before run creation; C reserve unchanged')
