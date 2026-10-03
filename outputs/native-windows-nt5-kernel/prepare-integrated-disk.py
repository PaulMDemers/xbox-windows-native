"""Update files in an already-installed private Windows fixture for repeat testing."""
import pathlib,hashlib,json,shutil,struct,subprocess,os
root=pathlib.Path('/home/paul/xbox-windows-native');ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');out=ws/'outputs/native-windows-nt5-kernel';runtime=root/'toolchains/offline-disk/root'
source=ws/'work/runs/nt5-kernel-047/hdd.qcow2';assert (source.parent/'cleanup.json').exists();target=out/'artifacts/windows2000-integrated-001.qcow2';temp=root/'fixtures/integrated-001';assert not target.exists() and not temp.exists();temp.mkdir()
env=dict(os.environ,LD_LIBRARY_PATH=str(runtime/'usr/lib/x86_64-linux-gnu'))
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(args):return subprocess.check_output(list(map(str,args)),env=env,stderr=subprocess.STDOUT)
record={'source_sha256':sha(source),'scope':'Private installed-state derivative, replacing only this project driver and diagnostic files.','files':[]}
try:
 raw=temp/'disk.raw';part=temp/'partition.ntfs';run(['qemu-img','convert','-O','raw',source,raw])
 with raw.open('rb') as f,part.open('xb') as dst:
  mbr=f.read(512);start,count=struct.unpack_from('<II',mbr,454);assert start==16777216 and mbr[450]==7;f.seek(start*512);left=count*512
  while left:
   b=f.read(min(left,4*1024**2));assert b;dst.write(b);left-=len(b)
 startup=out/'integrated-startup.cmd';startup.write_bytes(b'@echo off\r\nipconfig /all > C:\\xwn-ipconfig.txt\r\nstart "" /b C:\\xwncheck.exe\r\nstart "" /b C:\\xwnsoundstress.exe\r\nping -n 120 10.0.2.2 > C:\\xwn-ping.txt\r\nC:\\xwncycle.exe\r\nipconfig /renew > C:\\xwn-renew.txt\r\nping -n 16 10.0.2.2 > C:\\xwn-ping-after.txt\r\nnotepad C:\\xwn-sound-stress.log\r\n')
 files=[(out/'artifacts/xwnsoundstress.exe','/xwnsoundstress.exe'),(startup,'/Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd')]

 for file,destination in files:
  run([runtime/'usr/sbin/ntfscp','-f',part,file,destination]);readback=run([runtime/'usr/bin/ntfscat','-f',part,destination]);assert readback==file.read_bytes();record['files'].append({'path':destination,'sha256':sha(file),'readback_equal':True})
 with raw.open('r+b') as dst,part.open('rb') as src:dst.seek(start*512);shutil.copyfileobj(src,dst,4*1024**2)
 run(['qemu-img','convert','-O','qcow2',raw,target]);record['check']=run(['qemu-img','check',target]).decode();record['sha256']=sha(target);assert sha(source)==record['source_sha256'];record['source_preserved']=True
finally:
 assert temp.resolve().parent==(root/'fixtures').resolve();shutil.rmtree(temp);record['temporary_raws_removed']=True;(out/'integrated-disk-001.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))


