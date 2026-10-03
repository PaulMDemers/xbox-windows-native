import sys,pathlib,subprocess,json,hashlib,argparse
p=argparse.ArgumentParser();p.add_argument('variant',choices=['good','bad-nls']);a=p.parse_args()
root=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');kit=root/'outputs/native-windows-physical-paging'
temp=pathlib.Path('/home/paul/xbox-windows-native/fixtures')/('physical-paging-'+a.variant+'.raw');target=root/('work/physical-paging-'+a.variant+'.qcow2');src=root/'work/unleashx-ftp-fixture.qcow2'
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
   if a.variant=='bad-nls' and name.casefold().endswith('/c_1252.nls'):continue
   data=path.read_bytes()
   remote='Applications/XWNLoader/'+name;result=fatx.write_path_file(fp,part,remote,data)
   assert fatx.read_path_file(fp,part,remote)==data;record['files'].append(result.__dict__)
 subprocess.run(['qemu-img','convert','-O','qcow2',str(temp),str(target)],check=True)
 record['sha256']=sha(target);assert sha(src)==record['source_sha256'];record['source_preserved']=True
finally:
 assert temp.parent==pathlib.Path('/home/paul/xbox-windows-native/fixtures');temp.unlink(missing_ok=True)
(kit/('fixture-'+a.variant+'.json')).write_text(json.dumps(record,indent=2)+'\n');print(a.variant,record['sha256'])
