"""Read selected diagnostic files from an owned, stopped private VM disk."""
import argparse,pathlib,subprocess,struct,shutil,os,json,hashlib,re
p=argparse.ArgumentParser();p.add_argument('--run',required=True);a=p.parse_args();assert re.fullmatch(r'nt5-fatx-boot-(?:eof-|format-)?[0-9]+',a.run)
root=pathlib.Path('/home/paul/xbox-windows-native');ws=pathlib.Path('/mnt/c/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility');source=ws/'work/runs'/a.run/'hdd.qcow2';assert (source.parent/'cleanup.json').exists();temp=root/'fixtures'/('read-'+a.run);assert not temp.exists();temp.mkdir();out=source.parent/'guest-logs';out.mkdir(exist_ok=True)
env=dict(os.environ,LD_LIBRARY_PATH=str(root/'toolchains/offline-disk/root/usr/lib/x86_64-linux-gnu'));bin=root/'toolchains/offline-disk/root/usr/bin'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
record={'source_sha256':sha(source),'files':[]}
try:
 raw=temp/'disk.raw';part=temp/'part.ntfs';subprocess.run(['qemu-img','convert','-O','raw',str(source),str(raw)],check=True)
 import sys
 sys.path[:0]=[str(ws/'outputs/native-windows-fatx-runtime'),'/mnt/c/Users/Paul/Desktop/ogxbox-linux/scripts']
 import fatx_stage_boot as fatx
 from bulk_fatx import Writer
 with raw.open('rb') as fp:
  fs=Writer(fp,fatx.open_partition(fp,raw,'E'))
  for path in ['/xwn-check.log','/WINNT/debug/UserMode/userenv.log','/WINNT/setupapi.log']:
   try:data=fs.read(path)
   except Exception as ex:record['files'].append({'path':path,'error':repr(ex)});continue
   (out/path.split('/')[-1]).write_bytes(data);record['files'].append({'path':path,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
  for path in ['/Documents and Settings','/Documents and Settings/Default User','/WINNT']:
   try:
    at=1
    for name in fs.parts(path):
     e=fs.directory(at)['entries'][name.lower()][2];at=struct.unpack_from('<I',e,44)[0]
    record.setdefault('directories',{})[path]=list(fs.directory(at)['entries'])
   except Exception as ex:record.setdefault('directories',{})[path]={'error':repr(ex)}
 assert sha(source)==record['source_sha256'];record['source_preserved']=True
finally:
 assert temp.resolve().parent==(root/'fixtures').resolve();shutil.rmtree(temp);record['temporary_raws_removed']=True;(out/'extraction.json').write_text(json.dumps(record,indent=2)+'\n')
