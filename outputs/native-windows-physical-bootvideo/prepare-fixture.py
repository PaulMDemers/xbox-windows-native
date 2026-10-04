import sys,pathlib,subprocess,json,hashlib,argparse
p=argparse.ArgumentParser();p.add_argument('variant',choices=['good','bad-hal','bad-kernel']);a=p.parse_args()
root=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');kit=root/'outputs/native-windows-physical-bootvideo'
temp=pathlib.Path('/home/paul/xbox-windows-native/fixtures')/('physical-bootvideo-'+a.variant+'.raw');target=root/('work/physical-bootvideo-'+a.variant+'.qcow2');src=root/'work/unleashx-ftp-fixture.qcow2'
assert not temp.exists() and not target.exists()
sys.path.insert(0,'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts');import fatx_stage_boot as fatx
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
record={'variant':a.variant,'source_sha256':sha(src),'files':[]}
try:
 subprocess.run(['qemu-img','convert','-O','raw',str(src),str(temp)],check=True)
 with temp.open('r+b') as fp:
  part=fatx.open_partition(fp,temp,'E')
  for path in sorted((kit/'package').rglob('*')):
   if not path.is_file():continue
   name=path.relative_to(kit/'package').as_posix()
   data=(root/'outputs/native-windows-physical-processinit/package/loader/halxboxnt5.dll').read_bytes() if a.variant=='bad-hal' and name=='loader/halxboxnt5.dll' else path.read_bytes()
   if a.variant=='bad-kernel' and name=='WINNT/system32/ntoskrnl.exe':
    import struct
    mutable=bytearray(data);nt=struct.unpack_from('<I',mutable,60)[0];mutable[nt+24+64]^=1;data=bytes(mutable)
   remote='Applications/XWNLoader/'+name;result=fatx.write_path_file(fp,part,remote,data)
   assert fatx.read_path_file(fp,part,remote)==data;record['files'].append(result.__dict__)
 subprocess.run(['qemu-img','convert','-O','qcow2',str(temp),str(target)],check=True)
 record['sha256']=sha(target);assert sha(src)==record['source_sha256'];record['source_preserved']=True
finally:
 assert temp.parent==pathlib.Path('/home/paul/xbox-windows-native/fixtures');temp.unlink(missing_ok=True)
(kit/('fixture-'+a.variant+'.json')).write_text(json.dumps(record,indent=2)+'\n');print(a.variant,record['sha256'])
