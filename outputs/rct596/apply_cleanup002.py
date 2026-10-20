"""MIT. Bounded owned E SOFTWARE replacement with exact preimage and retained rollback."""
import importlib.util
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('cleanup596controller',K/'controller001.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
m=c.m
TARGET='/E/winnt/system32/config/software'
TEMP='/E/winnt/system32/config/xwn596.new'
BACKUP='/E/xwn586-kit/software-before596.hiv'

def run():
    c.verify();c.budget();col=c.read(K/'collection001.json');assert col['completed'] and col['hook_removed']
    prep=c.read(K/'cleanup-preparation002.json');assert prep['passed'] and prep['all_other_key_names_and_raw_values_unchanged']
    data=Path(prep['candidate']['path']).read_bytes();assert len(data)==prep['candidate']['bytes'] and m.sha(data)==prep['candidate']['sha256']
    out=K/'cleanup-apply001.json';assert not out.exists()
    r=dict(completed=False,utc=m.utc(),writes=[],console_C_accessed=False,launches=0,source_sha256=m.sha(Path(__file__).read_bytes()),preparation_sha256=m.sha((K/'cleanup-preparation002.json').read_bytes()))
    m.write_json(out,r)
    with m.connect(timeout=15) as f:
        m.baseline(f,'720p');c.startup(f,False)
        assert m.get(f,c.HOOK,True) is None
        assert m.get(f,TEMP,True) is None and m.get(f,BACKUP,True) is None
        old=m.get(f,TARGET);assert old==m.get(f,TARGET) and m.sha(old)==prep['source']['sha256']
        # Every rename is journaled before sending. Never retry an uncertain write.
        r['writes'].append(dict(action='stage-candidate',path=TEMP));m.write_json(out,r);m.put(f,TEMP,data);assert m.get(f,TEMP)==data
        assert m.get(f,TARGET)==old
        r['writes'].append(dict(action='retain-current-hive',source=TARGET,destination=BACKUP));m.write_json(out,r);f.rename(TARGET,BACKUP)
        assert m.get(f,BACKUP)==old and m.get(f,TARGET,True) is None
        r['writes'].append(dict(action='install-reviewed-hive',source=TEMP,destination=TARGET));m.write_json(out,r);f.rename(TEMP,TARGET)
        assert m.get(f,TARGET)==data and m.get(f,TEMP,True) is None
        m.baseline(f,'720p');c.startup(f,False)
    for path,digest in [(TARGET,prep['candidate']['sha256']),(BACKUP,prep['source']['sha256'])]:
        b=m.cold_pair(path,r,out);assert m.sha(b)==digest;r.setdefault('verified',{})[path]=dict(bytes=len(b),sha256=digest);m.write_json(out,r)
    r.update(completed=True,ended_utc=m.utc(),temporary_game_registry_restored=True,rollback_retained=BACKUP,normal_startup_preserved=True)
    m.write_json(out,r)

if __name__=='__main__':run()
