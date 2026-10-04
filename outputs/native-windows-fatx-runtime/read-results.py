"""Read selected diagnostic files from an owned, stopped private VM disk."""
import argparse,pathlib,subprocess,struct,shutil,os,json,hashlib,re
p=argparse.ArgumentParser();p.add_argument('--run',required=True);a=p.parse_args();assert re.fullmatch(r'nt5-fatx-runtime-(?:stress-)?[0-9]+',a.run)
root=pathlib.Path('/home/paul/xbox-windows-native');ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');source=ws/'work/runs'/a.run/'hdd.qcow2';assert (source.parent/'cleanup.json').exists();temp=root/'fixtures'/('read-'+a.run);assert not temp.exists();temp.mkdir();out=source.parent/'guest-logs';out.mkdir(exist_ok=True)
env=dict(os.environ,LD_LIBRARY_PATH=str(root/'toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu'));bin=root/'toolchains/offline-disk/root/usr/bin'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
record={'source_sha256':sha(source),'files':[]}
try:
 raw=temp/'disk.raw';part=temp/'part.ntfs';subprocess.run(['qemu-img','convert','-O','raw',str(source),str(raw)],check=True)
 with raw.open('rb') as src,part.open('xb') as dst:
  mbr=src.read(512);start,size=struct.unpack_from('<II',mbr,454);assert mbr[450]==7;src.seek(start*512);left=size*512
  while left:
   b=src.read(min(left,4*1024**2));assert b;dst.write(b);left-=len(b)
 commands=[('ntfsinfo',['-f','-m',str(part)],'ntfsinfo.txt')]
 for name in ['xwn-fatx.log','WINNT/setupapi.log']:
  commands.append(('ntfscat',['-f',str(part),'/'+name],name.split('/')[-1]))
 for tool,args,name in commands:
  p=subprocess.run([str(bin/tool),*args],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE);(out/name).write_bytes(p.stdout);(out/(name+'.stderr')).write_bytes(p.stderr)
  record['files'].append({'name':name,'exit_code':p.returncode,'sha256':hashlib.sha256(p.stdout).hexdigest()});print(name,p.returncode)
 sys_path='/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts'
 import sys
 sys.path.insert(0,sys_path);import fatx_stage_boot as fatx
 with raw.open('rb') as fp:
  part_e=fatx.open_partition(fp,raw,'E')
  try:data=fatx.read_path_file(fp,part_e,'XWNTest/roundtrip.bin')
  except Exception as ex:record['fatx_roundtrip_read_error']=str(ex)
  else:
   expected=bytes(((i*17+block*29)^0xa5)&255 for block in range(16) for i in range(65536))
   record['fatx_roundtrip']={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'matches_expected':data==expected}
 # Independent, strict full-width FATX chain traversal of stress files.
 sys.path.insert(0,str(ws/'outputs/native-windows-fatx-runtime'))
 from bulk_fatx import Writer
 with raw.open('rb') as fp:
  fs=Writer(fp,fatx.open_partition(fp,raw,'E'))
  try:
   entry=fs.directory(1)['entries']['xwnstress'][2];directory=struct.unpack_from('<I',entry,44)[0]
   files=fs.directory(directory)['entries'];checks=[]
   for name,(_,_,entry) in sorted(files.items()):
    row={'name':name};checks.append(row)
    try:
     data=fs.read('/XWNStress/'+name);chain=list(fs.chain(struct.unpack_from('<I',entry,44)[0]));pattern=bytes(((i*31)^(i>>8)^0x96)&255 for i in range(32768))
     expected=pattern*(1 if name=='mapped.dat' else 8)
     row.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),matches_expected=data==expected,end_marker=hex(fs.fat[chain[-1]]),clusters=len(chain))
    except Exception as ex:row['error']=repr(ex)
   record['strict_fatx_stress_files']=checks
  except Exception as ex:record['strict_fatx_stress_error']=repr(ex)
 assert sha(source)==record['source_sha256'];record['source_preserved']=True
finally:
 assert temp.resolve().parent==(root/'fixtures').resolve();shutil.rmtree(temp);record['temporary_raws_removed']=True;(out/'extraction.json').write_text(json.dumps(record,indent=2)+'\n')
