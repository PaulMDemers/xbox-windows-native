"""Create a unique standalone control; no preparation, launch or shared writes."""
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'owned-runtime272'
for name in ['model.py','protocol.py','audit.py','analyze-disk-delta.py','prepare.py','trace.py','Run.ps1']:
    s=(old/name).read_text().replace('xwn272','xwn275').replace('owned-runtime272','owned-reuse275').replace("case=='emu004'","case=='emu001'").replace("case in ('emu002','emu003','emu004')","case=='emu001'").replace("ValidateSet('emu004')","ValidateSet('emu001')").replace('4724','4754').replace('4725','4755')
    if name=='prepare.py':
        s=s.replace('reuse269-build005/xemu-reuse269.exe','boundary274-build002/xemu-boundary274.exe').replace('489c9af75c8734c47ce8b67231bedb7b10d15dc98617902350514252e5fcc295','3c3c61fff0615a2e2781b90a3f4ed9a6b119e343222e5defdcad4f0ea4cd806e')
        s=s.replace("(root/'private').mkdir()","(root/'private').mkdir();(root/'watch').mkdir()")
        s=s.replace("observer_operation=False","observer_operation=True").replace('Prepared unique272','Prepared unique275')
        # Freeze every module actually imported by this new controller/analysis.
        s=s.replace("dependencies={str(p.resolve()):sha(p) for p in list(k.glob('*.py'))", "dependencies={str(p.resolve()):sha(p) for p in list(k.glob('*.py'))")
    if name=='Run.ps1':
        s=s.replace("$process=$null;$controller=$null;$fallback=$false", "$process=$null;$controller=$null;$fallback=$false\n    $env:XWN_REUSE269_DIR=(Join-Path $root watch)")
        s=s.replace('300000','480000')
        s=s.replace("@{utc=[DateTime]::UtcNow.ToString('o');closed=$true", "Remove-Item Env:XWN_REUSE269_DIR -ErrorAction SilentlyContinue\n        @{utc=[DateTime]::UtcNow.ToString('o');closed=$true")
    if name=='trace.py':
        s=s.replace('from protocol import Remote,monitor','from protocol import Remote,monitor\nfrom objects import inspect as inspect_objects\nfrom backend import Backend')
        s=s.replace('observer_operation=False','observer_operation=True')
        s=s.replace('g=None;point=False;stopped=True;physical=False','g=None;point=False;stopped=True;physical=False;backend=None')
        s=s.replace("names=['_pb_Head'","names=['_pb_DmaBuffer2','_pb_DmaBuffer7','_pb_DmaBuffer8','_pb_DepthStencilPitch','_pb_Head'")
        s=s.replace("read(0xfd000000+pb['_pb_FifoHTAddr'],4096,'ramht')", "ramht=read(0xfd000000+pb['_pb_FifoHTAddr'],4096,'ramht')\n    row['objects']=inspect_objects(ramht,pb,h,lambda a,n,label:read(a,n,label));save()")
        s=s.replace("g=Remote(4755);r['initial_stop']", "backend=Backend(cmd,out,root,r,save)\n    g=Remote(4755);r['initial_stop']")
        s=s.replace('deadline=time.monotonic()+180','deadline=time.monotonic()+400')
        s=s.replace("assert phase==(11 if index==0 else 22)", "assert phase==(11 if index==0 else 22)\n        assert row['pixel_check'].get('passed'),'Native pixel control failed before observer request'\n        if phase==11:backend.begin()\n        else:backend.end()")
        s=s.replace("r['terminal_phase']=phase;r['passed']=phase==33", "r['terminal_phase']=phase;r['passed']=backend.completed and phase==33")
        s=s.replace("g.send('c');stopped=False;g.s.close();g=None", "if backend:backend.cleanup()\n            if r['passed']:g.send('c');stopped=False\n            else:r['quarantined_until_owned_exit']=True\n            g.s.close();g=None")
    p=k/name;assert not p.exists();p.write_text(s)
for source,dest in [('unit-reuse269/analyze-base.py','graph_base.py'),('unit-reuse269/analyze-extra.py','graph_extra.py'),('owned-lifetime273/decode.py','terminal.py'),('owned-texture271/oracle.py','oracle.py')]:
    p=k/dest;assert not p.exists();p.write_bytes((k.parent/source).read_bytes())
