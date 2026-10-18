"""Prepare single held-run protocol from frozen539 without executing hardware."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;S=K.parent/'entry-footprint539';rows={}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name in ['controller.py','supervise.py','host001.py','stage-host001.py','audit.py','decode_actual.py',
             'primary_decode.py','witness_decode.py','decode.py','receipts.py','legacy_refusal_decode.py','failure_marker.py']:
    src=S/name;t=src.read_text(encoding='utf-8')
    if name in ['controller.py','supervise.py','host001.py','stage-host001.py','audit.py','decode_actual.py']:
        t=t.replace('entry-footprint539','stack-stop540').replace('xwn539','xwn540').replace('XWNBoot539b','XWNBoot540a')
        t=t.replace('audit539','audit540').replace('completed539','completed540')
        t=t.replace("context-pair536/after2.json","entry-footprint539/after1.json")
        t=t.replace('unchanged_dashboard_since536=True,intervening_launch_or_power_cycle=False','watching_LED=True,manual_reset_available=True')
    if name=='controller.py':
        t=t.replace("assert ready['unchanged_dashboard_since536'] and not ready['intervening_launch_or_power_cycle']","assert ready['watching_LED'] and ready['manual_reset_available']")
        t=t.replace('manual_normal_restart=True','manual_normal_restart=False,intentional_halt=True,windows_boot_intended=False,manual_reset_required=True')
        t=t.replace('One post-stack-marker ablation launch; no startup hook or ordinary changes.','One intentional post-stack halt; no Windows boot or startup hook.')
    if name=='host001.py':t=t.replace("read(K/'prepared001.json')['images']['b']","read(K/'prepared001.json')['images']['1']")
    if name=='stage-host001.py':t=t.replace("c.read(K/'prepared001.json')['images']['b']","c.read(K/'prepared001.json')['images']['1']")
    p=K/name;assert not p.exists();p.write_text(t,encoding='utf-8',newline='\n')
    rows[name]=dict(source=str(src),source_sha256=sha(src),sha256=sha(p))
(K/'workflow-copy001.json').write_text(json.dumps(dict(files=rows,physical_access=False),indent=2)+'\n',encoding='utf-8',newline='\n')
