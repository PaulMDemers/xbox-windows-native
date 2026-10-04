"""Update files in an already-installed private Windows fixture for repeat testing."""
import pathlib,hashlib,json,shutil,struct,subprocess,os
root=pathlib.Path('/home/paul/xbox-windows-native');ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');out=ws/'outputs/native-windows-fatx-runtime';runtime=root/'toolchains/offline-disk/root'
source=ws/'outputs/native-windows-nt5-kernel/artifacts/windows2000-integrated-001.qcow2';target=out/'artifacts/windows2000-fatx-stress-001.qcow2';temp=root/'fixtures/fatx-stress-001';assert not target.exists() and not temp.exists();temp.mkdir()
env=dict(os.environ,LD_LIBRARY_PATH=str(runtime/'usr/lib/x86_64-linux-gnu'))
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(args):return subprocess.check_output(list(map(str,args)),env=env,stderr=subprocess.STDOUT)
record={'source_sha256':sha(source),'scope':'Private emulator derivative; add one MBR view of existing FATX E, a demand-start research filesystem driver and a cached file/directory/mapping stress test.','files':[]}
try:
 raw=temp/'disk.raw';part=temp/'partition.ntfs';run(['qemu-img','convert','-O','raw',source,raw])
 with raw.open('rb') as f,part.open('xb') as dst:
  mbr=f.read(512);start,count=struct.unpack_from('<II',mbr,454);assert start==16777216 and mbr[450]==7;f.seek(start*512);left=count*512
  while left:
   b=f.read(min(left,4*1024**2));assert b;dst.write(b);left-=len(b)
 # Expose the already-existing FATX E extent as MBR partition2 in this private derivative.
 # The original NTFS entry remains partition1; no Xbox partition is reformatted.
 with raw.open('r+b') as f:
  m=bytearray(f.read(512));assert m[510:512]==b'\x55\xaa' and not any(m[462:478])
  first,count=0x55f400,0x98f800;assert first+count<16777216
  f.seek(first*512);assert f.read(4)==b'FATX'
  m[462:478]=struct.pack('<B3sB3sII',0,b'\xfe\xff\xff',0x0b,b'\xfe\xff\xff',first,count)
  f.seek(0);f.write(m);record['private_mbr_fatx_extent']={'entry':2,'start':first,'sectors':count,'type':11}
 startup=out/'fatx-stress-startup.cmd';startup.write_bytes(b'@echo off\r\nC:\\xwnfatxstress.exe\r\nnotepad C:\\xwn-fatx.log\r\n')
 files=[(out/'artifacts/xwnfatxstress.exe','/xwnfatxstress.exe'),(out/'artifacts/xwnfatx.sys','/xwnfatx.sys'),(startup,'/Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd')]

 for file,destination in files:
  run([runtime/'usr/sbin/ntfscp','-f',part,file,destination]);readback=run([runtime/'usr/bin/ntfscat','-f',part,destination]);assert readback==file.read_bytes();record['files'].append({'path':destination,'sha256':sha(file),'readback_equal':True})
 with raw.open('r+b') as dst,part.open('rb') as src:dst.seek(start*512);shutil.copyfileobj(src,dst,4*1024**2)
 run(['qemu-img','convert','-O','qcow2',raw,target]);record['check']=run(['qemu-img','check',target]).decode();record['sha256']=sha(target);assert sha(source)==record['source_sha256'];record['source_preserved']=True
finally:
 assert temp.resolve().parent==(root/'fixtures').resolve();shutil.rmtree(temp);record['temporary_raws_removed']=True;(out/'fatx-stress-disk-001.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
