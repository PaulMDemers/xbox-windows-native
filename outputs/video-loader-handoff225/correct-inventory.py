"""Preserve first bounded-source graph error; sized ELF functions exclude embedded data."""
from pathlib import Path
import hashlib,json
k=Path(__file__).resolve().parent;dest=k/'inventory-correction.json';assert not dest.exists()
p=k/'inventory.py';text=p.read_text()
text=text.replace("dest=k/'inventory.json'","dest=k/'inventory002.json'").replace("art=k/'artifacts';art.mkdir(exist_ok=False)","art=k/'artifacts/inventory002';art.mkdir(exist_ok=False)")
a=text.index('functions={};current=None');b=text.index("r=dict(passed=True",a)
text=text[:a]+'''function_sizes={}
for line in subprocess.check_output(['/usr/bin/nm','-S','-n',str(art/'image-crom.elf')],text=True).splitlines():
 parts=line.split()
 if len(parts)==4 and parts[2] in ['t','T']:
  function_sizes[parts[3]]=(int(parts[0],16),int(parts[1],16))
closure={};todo=['startReactOS.part.0'];seen=set()
while todo:
 name=todo.pop()
 if name in seen:continue
 seen.add(name)
 if name not in function_sizes:
  closure[name]=dict(sized=False,calls=[],unresolved='No ELF function size; no decode across following embedded data');continue
 addr,n=function_sizes[name];body=subprocess.check_output(['/usr/bin/objdump','-d','--start-address='+hex(addr),'--stop-address='+hex(addr+n),str(art/'image-crom.elf')],text=True)
 calls=[line.strip() for line in body.splitlines() if re.search(r'\\bcall\\b',line)]
 closure[name]=dict(sized=True,address=addr,bytes=n,calls=calls)
 for line in calls:
  target=re.search(r'call\\s+[0-9a-f]+ <([^>]+)>',line)
  if target and target[1] in symbols:todo.append(target[1])
''' +text[b:]
q=k/'inventory002.py';assert not q.exists();q.write_text(text)
old=k/'inventory.json';dest.write_text(json.dumps(dict(source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),prior_script_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),prior_record_sha256=hashlib.sha256(old.read_bytes()).hexdigest(),correction='First disassembly scanner grouped unsized terminal thunk with embedded data and falsely included data-as-code calls. Original binary/ELF bridge valid; original recursive graph is NOT authoritative. New sized-function graph treats unsized symbols as unresolved, preserving indirect calls.',guest_launch_before_correction=False),indent=2)+'\n')
