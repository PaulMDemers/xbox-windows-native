"""Stage an uninstalled NIC driver and native SetupAPI helper on a private disk."""
import pathlib,hashlib,json,shutil,struct,subprocess,argparse
p=argparse.ArgumentParser();p.add_argument("--number",type=int,required=True);a=p.parse_args();assert 4<=a.number<=999
version=f"{a.number:03d}"
root=pathlib.Path('/home/paul/xbox-windows-native')
ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility')
out=ws/'outputs/native-windows-nt5-kernel';runtime=root/'toolchains/offline-disk/root'
source=out/'artifacts/windows2000-xbox-ide-005.qcow2';target=out/f'artifacts/windows2000-network-{version}.qcow2'
temp=root/f'fixtures/network-{version}';assert not target.exists() and not temp.exists();temp.mkdir()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def run(args):return subprocess.check_output(list(map(str,args)),stderr=subprocess.STDOUT).decode()
before=sha(source);record={'source_sha256':before,'scope':'Staged files only; driver has not been installed by this script.'}
try:
 raw=temp/'disk.raw';part=temp/'partition.ntfs';run(['qemu-img','convert','-O','raw',source,raw])
 with raw.open('rb') as f:
  mbr=f.read(512);start,count=struct.unpack_from('<II',mbr,454);assert start==63 and mbr[450]==7
  f.seek(start*512)
  with part.open('xb') as dst:
   left=count*512
   while left:
    data=f.read(min(left,4*1024**2));assert data;dst.write(data);left-=len(data)
 files=[out/'artifacts/nvnetnt5.sys',out/'nvnetnt5.inf',out/'artifacts/xwnsetup.exe'];record['files']=[]
 for file in files:
  run([runtime/'usr/sbin/ntfscp',part,file,'/'+file.name]);record['files'].append({'path':file.name,'sha256':sha(file)})
 startup=out/'network-startup.cmd'
 startup.write_bytes(b'@echo off\r\nC:\\xwnsetup.exe\r\nipconfig /all > C:\\xwn-ipconfig.txt\r\nping -n 4 10.0.2.2 > C:\\xwn-ping.txt\r\n')
 destination='/Documents and Settings/All Users/Start Menu/Programs/Startup/xwnsetup.cmd'
 run([runtime/'usr/sbin/ntfscp',part,startup,destination])
 record['startup']={'path':destination,'sha256':sha(startup)}
 seven=root/'toolchains/7zip/root/usr/lib/7zip/7z'
 run([seven,'x','-y','-ssc-',f'-o{temp}/readback',part,*[p.name for p in files]])
 for file in files:assert sha(temp/'readback'/file.name)==sha(file)
 run([seven,'x','-y','-ssc-',f'-o{temp}/startup-readback',part,destination.lstrip('/')])
 assert sha(temp/'startup-readback'/destination.lstrip('/'))==sha(startup)
 with raw.open('r+b') as dst,part.open('rb') as src:dst.seek(start*512);shutil.copyfileobj(src,dst,4*1024**2)
 run(['qemu-img','convert','-O','qcow2',raw,target]);record['check']=run(['qemu-img','check',target])
 record['sha256']=sha(target);assert sha(source)==before;record['source_preserved']=True;record['readback_equal']=True
finally:
 assert temp.resolve().parent==(root/'fixtures').resolve();shutil.rmtree(temp);record['temporary_raws_removed']=True
 (out/f'network-disk-{version}.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2))
