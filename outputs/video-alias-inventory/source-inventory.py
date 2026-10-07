"""Read pinned existing source trees; no builds or checkout modifications."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent
build=Path('/home/paul/xbox-windows-native/build')
inputs=[
 ('loader_bootvid','package-reconstruction-002/native/source','adf9b3d166ef84630a48d7393fcc9fe3ce78f104',[
  ('boot/freeldr/freeldr/ntldr/winldr.c',[(160,230)]),
  ('boot/freeldr/freeldr/arch/i386/xbox/xboxmem.c',[(220,280)]),
  ('drivers/base/bootvid/i386/xbox/bootvid.c',[(120,265)])]),
 ('miniport0093','video-reuse-001/source','329a29d61af1620a9fc005b0d8fcfb9e1a937d20',[
  ('win32ss/drivers/miniport/xboxvmp/nt5/xboxvnt5.c',[(42,120),(140,190)]),
  ('win32ss/drivers/miniport/xboxvmp/nt5/video_trace.c',[(1,90)]),
  ('win32ss/drivers/miniport/xboxvmp/nt5/CMakeLists.txt',[(1,90)])]),
 ('hal0102','hal-dump-path-002/source','8beed93598b97994a7836ab91285df1fcb8af27c',[
  ('hal/halx86/xboxnt5/rootbus.c',[(72,88)]),
  ('hal/halx86/xboxnt5/mapprobe.c',[(138,151),(885,903)])])]
records=[]
for role,rel,expected,files in inputs:
 repo=build/rel;tree=subprocess.check_output(['git','-C',str(repo),'write-tree'],text=True).strip();assert tree==expected
 rows=[]
 for name,spans in files:
  data=(repo/name).read_bytes();indexed=subprocess.check_output(['git','-C',str(repo),'show',':'+name]);assert data==indexed
  lines=data.decode('utf-8').splitlines();rows.append(dict(path=name,sha256=hashlib.sha256(data).hexdigest(),git_blob=subprocess.check_output(['git','-C',str(repo),'rev-parse',':'+name],text=True).strip(),excerpts=[dict(first=lo,last=min(hi,len(lines)),lines=lines[lo-1:hi]) for lo,hi in spans]))
 records.append(dict(role=role,private_source=str(repo),tree=tree,files=rows))
p=k/'source-inventory.json';assert not p.exists();p.write_text(json.dumps(dict(records=records,limits='Source contracts from indexed matching files in pinned existing build trees. Reconstruction source is not a fresh byte-identical binary rebuild or proof of all runtime branches.'),indent=2)+'\n');print('Pinned source contracts:',len(records),'trees')
