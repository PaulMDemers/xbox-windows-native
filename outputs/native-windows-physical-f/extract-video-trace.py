"""Read a trace from a stopped, owned emulator overlay (including failed boots)."""
import argparse, pathlib, sys, subprocess, importlib.util, json
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
k=ws/'outputs/native-windows-physical-f'
p=argparse.ArgumentParser();p.add_argument('--run',required=True);a=p.parse_args()
assert a.run.startswith('nt5-physical-f-') and a.run.replace('-','').isalnum()
run=ws/'work/runs'/a.run;assert (run/'cleanup.json').exists()
raw=pathlib.Path('/home/paul/xbox-windows-native/fixtures')/('extract-'+a.run+'.raw')
assert not raw.exists()
sys.path[:0]=[str(ws/'outputs/native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
spec=importlib.util.spec_from_file_location('decoder',k/'decode-video-trace.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
try:
 subprocess.run(['qemu-img','convert','-O','raw',str(run/'hdd.qcow2'),str(raw)],check=True)
 with raw.open('rb') as f:
  fatx.PARTITIONS['F']=(15633072*512,472764096*512);w=Writer(f,fatx.open_partition(f,raw,'F'))
  data=w.read('/winnt/system32/xwn-video-trace.bin');decoded=m.decode(data)
  decoded['run']=a.run
  with (k/'artifacts'/(a.run+'-trace.bin')).open('xb') as out:out.write(data)
  (k/(a.run+'-trace.json')).write_text(json.dumps(decoded,indent=2)+'\n')
 print({'run':a.run,'records':decoded['records'],'events':decoded['events'][18:]})
finally:raw.unlink(missing_ok=True)
