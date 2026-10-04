"""Read a stopped emulator F: report without mounting or modifying the disk."""
import pathlib,sys,subprocess,json,hashlib,argparse
root=pathlib.Path('/home/paul/xbox-windows-native');ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');kit=ws/'outputs/native-windows-extended-storage'
sys.path[:0]=[str(ws/'outputs/native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
import fatx_stage_boot as fatx
from bulk_fatx import Writer
p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--write-generation',type=int,choices=[1,2]);a=p.parse_args()
assert a.run.startswith('nt5-extended-f-') and a.run.replace('-','').isalnum()
run=ws/'work/runs'/a.run;assert (run/'cleanup.json').exists()
raw=root/'fixtures'/('read-'+a.run+'.raw');assert not raw.exists()
r={'run':a.run,'native_windows_read_verified':False}
try:
 subprocess.run(['qemu-img','convert','-O','raw',str(run/'hdd.qcow2'),str(raw)],check=True)
 with raw.open('rb') as f:
  fatx.PARTITIONS['F']=(15633072*512,472764096*512);w=Writer(f,fatx.open_partition(f,raw,'F'))
  data=w.read('/xwn-large-write.log' if a.write_generation else '/xwn-large.log');(kit/(a.run+'-guest.txt')).write_bytes(data)
  r.update(report_sha256=hashlib.sha256(data).hexdigest(),report=data.decode('ascii'))
  r['native_windows_read_verified']=b'XWN-LARGE-PASS:' in data and b'Failures: 0\r\n' in data
  generation=a.write_generation or 0
  sentinel=w.read('/xwn-high.bin');r['sentinel_intact']=sentinel==bytes((i*37+(i>>8)+0x5a+11*generation)&255 for i in range(4097))
  e=w.directory(1)['entries']['xwn-high.bin'][2];cid=__import__('struct').unpack_from('<I',e,44)[0]
  r['sentinel_absolute_offset']=w.p.cluster_offset(cid)
  r['sentinel_cluster_tail_zero']=not any(w.read_cluster(cid)[4097:])
  assert r['sentinel_absolute_offset']==145644445696
  if a.write_generation:
   r['native_windows_write_verified']=(b'XWN-LARGE-WRITE-PASS:' in data and b'Failures: 0\r\n' in data and
    ('Previous generation: '+str(generation-1)+'\r\n').encode() in data and
    ('Written generation: '+str(generation)+'\r\n').encode() in data and r['sentinel_intact'])
   r['generation']=generation
   r['native_windows_read_verified']=r['native_windows_write_verified']
except KeyError as e:r['missing_file']=str(e)
finally:
 raw.unlink(missing_ok=True);(kit/(a.run+'-result.json')).write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
