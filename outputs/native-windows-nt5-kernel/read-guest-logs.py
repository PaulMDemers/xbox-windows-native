"""Read selected diagnostic files from an owned, stopped private VM disk."""
import argparse,pathlib,subprocess,struct,shutil,os,json,hashlib
p=argparse.ArgumentParser();p.add_argument('--run',required=True);a=p.parse_args();assert a.run.startswith('nt5-kernel-') and a.run[11:].isdigit()
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
 for name in ['xwn-shutdown.log','xwn-sound-stress.log','xwnswsetup.log','xwnasetup.log','xwn-sound.log','xwnsetup.log','xwn-check.log','xwn-ipconfig.txt','xwn-ping.txt','xwn-cycle.log','xwn-ping-after.txt','xwn-renew.txt','WINNT/setupapi.log']:
  commands.append(('ntfscat',['-f',str(part),'/'+name],name.split('/')[-1]))
 for tool,args,name in commands:
  p=subprocess.run([str(bin/tool),*args],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE);(out/name).write_bytes(p.stdout);(out/(name+'.stderr')).write_bytes(p.stderr)
  record['files'].append({'name':name,'exit_code':p.returncode,'sha256':hashlib.sha256(p.stdout).hexdigest()});print(name,p.returncode)
 assert sha(source)==record['source_sha256'];record['source_preserved']=True
finally:
 assert temp.resolve().parent==(root/'fixtures').resolve();shutil.rmtree(temp);record['temporary_raws_removed']=True;(out/'extraction.json').write_text(json.dumps(record,indent=2)+'\n')
