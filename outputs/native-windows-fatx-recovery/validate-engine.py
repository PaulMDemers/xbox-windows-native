"""Cold-verify the native repair engine, including absence of unintended F: writes."""
import argparse,hashlib,json,pathlib,struct,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('--case',choices=['apply','reject','resume'],required=True);a=p.parse_args()
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');k=ws/'outputs/native-windows-fatx-recovery';run=ws/f'work/runs/fatx-repair-{a.case}-001';assert (run/'cleanup.json').exists()
fixture=json.loads((k/f'repair-{a.case}-fixture.json').read_text());src=k/f'artifacts/repair-{a.case}-001.qcow2'
raw=pathlib.Path('/home/paul/xbox-windows-native/fixtures')/f'engine-{a.case}.raw';base=raw.with_suffix('.base.raw');assert not raw.exists() and not base.exists()
sys.path[:0]=[str(ws/'outputs/native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
sha=lambda b:hashlib.sha256(b).hexdigest();lo=15633072*512;hi=lo+472764096*512
try:
 subprocess.run(['qemu-img','convert','-O','raw',str(run/'hdd.qcow2'),str(raw)],check=True)
 subprocess.run(['qemu-img','convert','-O','raw',str(src),str(base)],check=True)
 with raw.open('rb') as f,base.open('rb') as b:
  w=Writer(f,fatx.open_partition(f,raw,'E'));log=w.read('apps/xwnfatfix/repair.txt').decode('ascii')
  assert sha(w.read('apps/xwnfatfix/default.xbe'))==fixture['xbe_sha256'];assert sha(w.read('apps/xwnfatfix/plan.bin'))==fixture['plan_sha256']
  assert ('REPAIR_COMPLETE success=0' if a.case=='reject' else 'REPAIR_COMPLETE success=1') in log
  if a.case=='reject':assert 'APPLIED' not in log and 'ALL_PREIMAGES_VERIFIED' not in log
  if a.case=='resume':assert 'ALREADY_APPLIED sector=0' in log
  f.seek(lo);assert sha(f.read(14778368))==fixture['metadata_sha256']
  for rec in fixture['records']:
   f.seek(lo+rec['offset']);assert f.read(512)==bytes.fromhex(rec['before_hex'] if a.case=='reject' else rec['after_hex'])
  extents=json.loads(subprocess.check_output(['qemu-img','map','--output=json',str(run/'hdd.qcow2')]))
  extents=[e for e in extents if e.get('depth')==0 and e.get('data') and e['start']<hi and e['start']+e['length']>lo]
  assert sum(e['length'] for e in extents)<1024*1024
  if a.case=='reject':assert not extents
  for e in extents:
   at=e['start'];b.seek(at);expected=bytearray(b.read(e['length']))
   if a.case!='reject':
    for rec in fixture['records']:
     off=lo+rec['offset']-at
     if 0<=off<len(expected):expected[off:off+512]=bytes.fromhex(rec['after_hex'])
   f.seek(at);assert f.read(e['length'])==expected,'Unplanned F change'
 result=dict(case=a.case,run=run.name,xbe_sha256=fixture['xbe_sha256'],log=log,fat_unchanged=True,unplanned_F_changes=False,F_write_extents=extents,passed=True)
finally:raw.unlink(missing_ok=True);base.unlink(missing_ok=True)
(k/f'engine-{a.case}-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
