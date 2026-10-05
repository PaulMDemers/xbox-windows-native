"""Read-only synthetic rotation/guard verification on a closed emulator disk."""
import argparse, hashlib, json, pathlib, struct, subprocess, sys
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
k=ws/'outputs/native-windows-fatx-forensics'
p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--boots',type=int,required=True);p.add_argument('--expected',choices=['pass','fail'],default='pass');a=p.parse_args()
assert a.run.startswith('nt5-physical-f-high-allocation-') and a.run.replace('-','').isalnum() and 1<=a.boots<=9
run=ws/'work/runs'/a.run;assert (run/'cleanup.json').exists()
raw=pathlib.Path('/home/paul/xbox-windows-native/fixtures')/(a.run+'-rotate.raw');assert not raw.exists()
sys.path[:0]=[str(ws/'outputs/native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
r=dict(scope=__doc__,run=a.run,expected_boots=a.boots,whole_filesystem_audit=False,guards=[])
try:
    subprocess.run(['qemu-img','convert','-O','raw',str(run/'hdd.qcow2'),str(raw)],check=True)
    with raw.open('rb') as f:
        fatx.PARTITIONS['F']=(15633072*512,472764096*512);w=Writer(f,fatx.open_partition(f,raw,'F'))
        log=w.read('xwn-rotate.log').decode('ascii');r['log']=log
        try:r['state']=struct.unpack('<I',w.read('xwnrotate/state.bin'))[0]
        except KeyError:r['state']=None
        r['reuse_counts']=[int(line.split('=')[1]) for line in log.splitlines() if line.startswith('reuse=')]
        r['probe_passed']=all([log.count('ROTATE-PASS\r\n')==a.boots,'FAIL:' not in log,
            log.count('cycles=96\r\n')==a.boots,len(r['reuse_counts'])==a.boots,
            all(n>0 for n in r['reuse_counts']),r['state']==a.boots])
        expected_entries={'a','b','state.bin'}
        for i in range(130):
            name=f'guard{i:03}.bin';expected_entries.add(name);data=w.read('xwnrotate/'+name)
            expected=bytes(((at*37)^(at>>8)^(i+123))&255 for at in range(65537))
            r['guards'].append(dict(path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),match=data==expected))
        parent=struct.unpack_from('<I',w.directory(1)['entries']['xwnrotate'][2],44)[0]
        directory=w.directory(parent)['entries'];r['no_temporary_files']=set(directory)==expected_entries
        for name in ('a','b'):
            child=struct.unpack_from('<I',directory[name][2],44)[0]
            r['no_temporary_files'] &= not w.directory(child)['entries']
        r['probe_sha256']=hashlib.sha256(w.read('xwnrotate.exe')).hexdigest()
        r['probe_matches_fixture']=r['probe_sha256']==json.loads((k/'rotate-regression-fixture.json').read_text())['rotate_sha256']
finally:
    raw.unlink(missing_ok=True)
r['passed']=all([r['probe_passed'],all(g['match'] for g in r['guards']),r['no_temporary_files'],r['probe_matches_fixture']])
(k/(a.run+'-rotate-audit.json')).write_text(json.dumps(r,indent=2)+'\n')
print(a.run,'PASS' if r['passed'] else 'FAIL','reuse:',r['reuse_counts'],'guard files:',len(r['guards']))
assert r['passed']==(a.expected=='pass')
