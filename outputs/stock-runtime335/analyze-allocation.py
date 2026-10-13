"""Analyze a complete read-only stock E: metadata capture. Never repairs or writes a console."""
import argparse,array,hashlib,json,pathlib,struct
p=argparse.ArgumentParser();p.add_argument('--capture',type=pathlib.Path,required=True);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args()
meta=(a.capture/'fat-metadata.bin').read_bytes();blob=(a.capture/'directories.bin').read_bytes();log=(a.capture/'snapshot.txt').read_text()
assert 'SNAPSHOT_COMPLETE success=1 ' in log and len(blob)%80==0
assert struct.unpack_from('<I',meta)[0]==0x58544146 and struct.unpack_from('<II',meta,8)==(32,1)
fat=array.array('I');fat.frombytes(meta[4096:]);assert fat.itemsize==4
limit=(10000048*512-len(meta))//16384+1
assert len(fat)>=limit
clusters={};entries={};special=[];summary=None
for at in range(0,len(blob),80):
 typ,head,c,aux=struct.unpack_from('<4I',blob,at);e=blob[at+16:at+80]
 if typ==1:
  assert c not in clusters;clusters[c]=(head,aux);assert fat[c]==aux
 elif typ==2:entries.setdefault(head,[]).append((c,aux,e))
 elif typ in (3,4):special.append(dict(type=typ,head=head,cluster=c,value=aux))
 elif typ==5:
  assert at+80==len(blob);summary=(head,c)
 else:raise AssertionError('Unknown record')
assert summary==(len(clusters),sum(map(len,entries.values())))
owners=array.array('I',[0])*limit;objects=[];errors=[];seen_dirs=set();paths={1:'/'}
def error(path,kind,**details):errors.append(dict(path=path,kind=kind,**details))
def chain(first,path,size,isdir):
 ident=len(objects)+1;objects.append(path);c=first;n=0;seen=set()
 if c==0:
  if size or isdir:error(path,'missing-chain')
  return
 while 0<c<limit:
  if c in seen:error(path,'chain-loop',cluster=c);break
  seen.add(c);n+=1
  if owners[c] and owners[c]!=ident:error(path,'crosslink',cluster=c,other=objects[owners[c]-1])
  else:owners[c]=ident
  if isdir and (c not in clusters or clusters[c][0]!=first):error(path,'directory-not-fully-captured',cluster=c)
  nxt=fat[c]
  if nxt==0xffffffff:break
  if nxt==0 or nxt>=limit:error(path,'invalid-chain-terminal',cluster=c,next=f'{nxt:08x}');break
  c=nxt
 else:error(path,'invalid-first-cluster',cluster=c)
 if not isdir and n*16384<size:error(path,'short-chain',size=size,capacity=n*16384)
queue=[(1,'/')];files=0;directories=0
for first,path in queue:
 if not first:directories+=1;continue # FATX represents empty directories without a cluster.
 if first in seen_dirs:error(path,'shared-directory-root',cluster=first);continue
 seen_dirs.add(first);directories+=1;chain(first,path,0,True);names=set()
 for c,off,e in entries.get(first,[]):
  assert c in clusters and clusters[c][0]==first and off<16384 and off%64==0
  length=e[0]
  if not 1<=length<=42:error(path,'invalid-name-length',cluster=c,offset=off,length=length);continue
  name=e[2:2+length].decode('latin1');child=path.rstrip('/')+'/'+name
  if name.lower() in names:error(child,'duplicate-name')
  names.add(name.lower());start,size=struct.unpack_from('<II',e,44)
  if e[1]&0x10:queue.append((start,child))
  else:files+=1;chain(start,child,size,False)
assert all(head in seen_dirs for head,_ in clusters.values()),'Unreachable captured directory'
orphan=[];allocated=0;bad=0
for c in range(1,limit):
 if fat[c]==0xfffffff7:bad+=1
 elif fat[c]:
  allocated+=1
  if not owners[c]:orphan.append(c)
r=dict(scope=__doc__,capture_complete=True,directories=directories,files=files,live_entries=summary[1],directory_clusters=summary[0],allocated_clusters=allocated,bad_clusters=bad,orphan_cluster_count=len(orphan),orphan_cluster_sample=orphan[:64],capture_chain_warnings=special,errors=errors,allocation_consistent=not errors and not orphan and not special,metadata_sha256=hashlib.sha256(meta).hexdigest(),directory_records_sha256=hashlib.sha256(blob).hexdigest(),caveat='Allocation audit only; payload bytes and Windows registry semantics need separate verification.')
a.output.write_text(json.dumps(r,indent=2)+'\n');print({k:r[k] for k in ['directories','files','directory_clusters','orphan_cluster_count','allocation_consistent']});print('errors',len(errors))
