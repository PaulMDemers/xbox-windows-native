"""Cold standalone disk comparison, QCOW integrity and exact frozen inputs."""
import hashlib,json,subprocess,sys
from pathlib import Path
k=Path(__file__).resolve().parent;case=sys.argv[1];assert case=='emu001';out=k/case;root=Path('/mnt/c/xwn632')/case
assert sys.platform=='linux' and not (out/'audit.json').exists()
closure=json.loads((out/'host-closure.json').read_text(encoding='utf-8-sig'));assert closure['closed']
prepared=json.loads((out/'prepared.json').read_text());r=dict(read_only=True,physical_access=False,checks={},windows_run=False)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def linux(p):
    p=p.replace('\\','/');return Path('/mnt/'+p[0].lower()+p[2:])
for name in ('base.qcow2','hdd.qcow2'):
    x=subprocess.run(['qemu-img','check','--output=json',str(root/name)],capture_output=True,text=True,timeout=60)
    r['checks'][name]=dict(returncode=x.returncode,stdout=x.stdout,stderr=x.stderr)
x=subprocess.run(['qemu-img','compare','-f','qcow2','-F','qcow2',str(root/'base.qcow2'),str(root/'hdd.qcow2')],capture_output=True,text=True,timeout=120)
r['entire_logical_disk_comparison']=dict(returncode=x.returncode,stdout=x.stdout,stderr=x.stderr,bytes=8589934592)
r['disk_all_bytes_unchanged']=x.returncode==0
r['source_pins']={n:sha(linux(v['source']))==v['sha256'] for n,v in prepared['inputs'].items()}
r['immutable_copies']={n:sha(root/n)==v['sha256'] for n,v in prepared['inputs'].items() if n!='eeprom.bin'}
r['dependencies']={n:sha(linux(n))==s for n,s in prepared['dependencies'].items()}
r['eeprom_after_sha256']=sha(root/'eeprom.bin')
r['eeprom_unchanged']=r['eeprom_after_sha256']==prepared['inputs']['eeprom.bin']['sha256']
r['passed']=r['disk_all_bytes_unchanged'] and all(x['returncode']==0 for x in r['checks'].values()) and all(r['source_pins'].values()) and all(r['immutable_copies'].values()) and all(r['dependencies'].values())
r['scope']='Entire8GiB logical disk equality and QCOW structure. No Windows boot, Windows events or hive mutation expected; no Windows shutdown claim.'
(out/'audit.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({key:r[key] for key in ['passed','disk_all_bytes_unchanged','eeprom_unchanged']},indent=2))
