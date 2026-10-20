"""Interpret private live instructions and fixed WINMM frames after closure."""
import hashlib,json,re,struct,sys
from collections import Counter
from pathlib import Path
from frame_layout import OFFSETS,frame_return,call_target
K=Path(__file__).resolve().parent;W=K.parents[1]
sys.path.insert(0,str(W/'work/python-packages'));import pefile,capstone
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=K/'runtime-review001.json';assert not out.exists()
assert read(K/'frame-tests001.json')['passed'] and read(K/'review001.json')['passed']
P=Path('C:/xwn628/pc001/cold1-002');manifest=read(P/'manifest.json')
log=P/'files/xwn628/cost.txt';files={}
for row in read(K.parent/'rct621/seed-symbols001.json')['files']:
 p=Path(row['path'].replace('/mnt/c/','C:/'));assert sha(p)==row['sha256']==manifest['winnt/system32/'+row['name']]['sha256'];files[row['name']]=p
files['kernel32.dll']=P/'files/WINNT/system32/kernel32.dll'
assert sha(files['kernel32.dll'])==manifest['winnt/system32/kernel32.dll']['sha256']
# Independently compare the C switch compiled into this probe with host layout.
header=(K/'caller_plan.h').read_text();cmap={}
for cases,offset in re.findall(r'((?:case 0x[0-9a-f]+:)+)return (\d+);',header):
 for value in re.findall(r'0x[0-9a-f]+',cases):cmap[int(value,16)]=int(offset)
assert cmap==OFFSETS
mods=[];samples={};captures={};images={};counts=Counter();sites=Counter();unknown=Counter();code_versions={}
for line in log.read_text().splitlines():
 v=line.split();tag=v[0]
 if tag=='MODULE':mods.append((int(v[2],16),int(v[3],16),' '.join(v[4:]).lower().split('\\')[-1]))
 elif tag=='SAMPLE':samples[int(v[2])]=v
 elif tag in ('CODE','STACK','CALLSITE','TARGET'):
  assert len(v)==6 and int(v[1])==4
  key=(int(v[2]),tag);assert key not in captures
  address=int(v[3],16);ok=int(v[4]);assert ok in (0,1)
  data=bytes.fromhex(v[5]) if ok else b''
  assert (len(data)==dict(CODE=32,STACK=64,CALLSITE=64,TARGET=4)[tag]) if ok else v[5]=='-'
  captures[key]=(address,ok,data)
assert len(captures)==4*len(samples)
wm=[(b,s) for b,s,n in mods if n=='winmm.dll'];game=[(b,s) for b,s,n in mods if n=='rct.exe'];assert len(wm)==len(game)==1
winbase=wm[0][0];gamebase,gamesize=game[0]
dis=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
for index,v in samples.items():
 ip=int(v[4],16);sp=int(v[5],16);code=captures[index,'CODE'];stack=captures[index,'STACK'];caller=captures[index,'CALLSITE'];target=captures[index,'TARGET']
 assert code[0]==ip and stack[0]==sp
 owners=[(b,s,n) for b,s,n in mods if b<=ip<b+s];assert len(owners)==1
 base,size,name=owners[0]
 for label,item in [('code',code),('stack',stack),('caller',caller),('target',target)]:counts[label+('_read_success' if item[1] else '_read_unavailable')]+=1
 if not code[1]:continue
 code_versions.setdefault((name,ip-base),set()).add(hashlib.sha256(code[2]).hexdigest())
 if name in files:
  if (name,base) not in images:images[name,base]=pefile.PE(str(files[name])).get_memory_mapped_image(ImageBase=base)
  assert code[2]==images[name,base][ip-base:ip-base+32],(index,name,hex(ip-base))
  counts['exact_dll_code_matches']+=1
 elif name=='rct.exe':counts['packed_game_live_code_captures']+=1
 else:unknown['unreviewed_module_'+name]+=1;continue
 if name!='winmm.dll' or ip-base not in OFFSETS or not stack[1]:continue
 ret=frame_return(base,ip-base,stack[2]);counts['fixed_winmm_frames']+=1
 assert caller[0]==ret-32
 if not caller[1]:unknown['caller_read_unavailable']+=1;continue
 slot=(target[0],target[2]) if target[1] else None
 if caller[2][26:28]==b'\xff\x15' and slot is None:unknown['indirection_unavailable']+=1;continue
 dest,kind=call_target(ret,caller[2],slot)
 if dest is None:unknown[kind]+=1;continue
 ins=caller[2][26:32] if kind.startswith('indirect') else caller[2][27:32]
 decoded=list(dis.disasm(ins,ret-len(ins)))
 assert len(decoded)==1 and decoded[0].mnemonic=='call' and decoded[0].address+decoded[0].size==ret
 if not gamebase<=ret-len(ins)<ret<=gamebase+gamesize:unknown['caller_outside_game']+=1;continue
 if dest!=winbase+0x7bbc:unknown['different_target_'+hex(dest)]+=1;continue
 sites[ret-gamebase,kind]+=1;counts['runtime_call_target_matches_timeGetTime']+=1
assert len(samples)>=100 and counts['fixed_winmm_frames']>0
r=dict(passed=True,private_log_sha256=sha(log),samples=len(samples),counts=dict(counts),unknown=dict(unknown),
 caller_sites=[dict(return_rva=hex(rv),encoding=kind,observations=n) for (rv,kind),n in sorted(sites.items())],
 repeated_code_locations_with_different_bytes=sum(len(h)>1 for h in code_versions.values()),
 scope='Bounded live code, fixed-version timer frame and captured call-target attribution. No packed on-disk code substituted; no sample percentages as CPU-time fractions, game FPS or Xbox measurement.',
 source_sha256=sha(Path(__file__)))
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
