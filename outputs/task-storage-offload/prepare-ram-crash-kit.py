"""Create a new diagnostic kit; never copy old run outputs or launch a guest."""
from pathlib import Path
import hashlib,json,sys
w=Path(__file__).resolve().parents[2];old=w/'outputs/video-shared-crash';k=w/'outputs/video-ram-crash'
k.mkdir(exist_ok=False);(k/'artifacts').mkdir()
names=['common.py','prepare.py','preflight.py','Run.ps1','Invoke-Lba.ps1','supervise.py','trace.py','audit-crash.py','configuration.py','cold-map.py','record-closure.py','verify.py','verify-payload.py','verify-render.py','atomic_json.py','modules.json','layouts.json','kernel-review.json','fatx-review.json','nvnet-review.json','atapi-review.json','address-review.json','video-sites.json']
for n in names:(k/n).write_text((old/n).read_text().replace('video-shared-crash','video-ram-crash'),encoding='utf-8')
for n in ['build-review.json','Build.ps1','review.py','probe.c','trigger.c']:(k/n).write_bytes((old/n).read_bytes())
for n in ['probe.exe','trigger.sys']:(k/'artifacts'/n).write_bytes((old/'artifacts'/n).read_bytes())
(k/'discover_kernel.py').write_bytes((w/'outputs/video-mode-trace3/discover_kernel.py').read_bytes())
def edit(n,old,new):
 p=k/n;s=p.read_text();assert old in s,(n,old);p.write_text(s.replace(old,new),encoding='utf-8')
edit('prepare.py',"assert read(k.parent/'video-shared-trace2/verification.json')['passed']","assert read(k.parent/'video-mode-trace3/verification.json')['passed']\nassert read(k.parent/'video-mode-reset/verification.json')['passed']")
edit('prepare.py',"parent=k.parent/'video-shared-framebuffer/fixture-candidate001.json'","parent=k.parent/'video-mode-reset/fixture-candidate001.json'")
edit('prepare.py',"rr=readers(io,source);protected=list(f['protected'])","rr=readers(io,source);protected=list(f['protected'])\n for row in f['payloads']:protected.append(dict(volume='F',path=row['path'],sha256=row['sha256']))")
edit('prepare.py',"alias_verification_sha256=sha(k.parent/'video-shared-trace2/verification.json')","alias_verification_sha256=sha(k.parent/'video-shared-trace2/verification.json'),ram_mode_verification_sha256=sha(k.parent/'video-mode-trace3/verification.json')")
edit('verify.py',"success=callback_complete and a['dump_write_evidence_passed'] and a['integrity_passed']","assert a['event_history_preserved'] and not a['warnings_errors'] and not a['new_events']['application']\nassert a['normal_shutdown_count']==0\nassert t['kernel_discovery']['kernel_base']==t['kernel_base']\nsuccess=callback_complete and a['dump_write_evidence_passed'] and a['integrity_passed']")
sys.path.insert(0,str(w/'work/python-packages'));import pefile
mods=json.loads((k/'modules.json').read_text())
for n,p in [('xwnown.dll',w/'outputs/video-mode-reset/candidate001/artifacts/xwnown.dll'),('probe.exe',k/'artifacts/probe.exe')]:
 pe=pefile.PE(str(p));mods[n]=dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),preferred_base=pe.OPTIONAL_HEADER.ImageBase,timestamp=pe.FILE_HEADER.TimeDateStamp,image_size=pe.OPTIONAL_HEADER.SizeOfImage)
 if n=='xwnown.dll':
  data=p.read_bytes();offset=pe.FILE_HEADER.PointerToSymbolTable;count=pe.FILE_HEADER.NumberOfSymbols;strings=offset+count*18;size=int.from_bytes(data[strings:strings+4],'little');syms={};i=0
  import struct
  while i<count:
   at=offset+i*18;name=data[at:at+8];value,sec,typ,storage,aux=struct.unpack_from('<IhHBB',data,at+8);i+=1+aux
   if name[:4]==bytes(4):
    pos=int.from_bytes(name[4:],'little');assert 4<=pos<size;name=data[strings+pos:strings+size].split(b'\0')[0]
   else:name=name.split(b'\0')[0]
   if sec>0:syms[name.decode().lstrip('_').split('@')[0]]=pe.sections[sec-1].VirtualAddress+value
  mods[n]['symbols']=syms
(k/'modules.json').write_text(json.dumps(mods,indent=2)+'\n',encoding='utf-8')
edit('trace.py','from atomic_json import write_json','from atomic_json import write_json\nfrom discover_kernel import discover')
edit('trace.py',"K=review['kernel_base_expected']","K=None")
edit('trace.py',"render_sites={};video=", "headers={};rambase=None;raminfo=mods['xwnown.dll'];ram_symbols=raminfo['symbols']\nrender_sites={};video=")
edit('trace.py',"    assert g.read(base,2)==b'MZ' and u32(base+u32(base+60)+8)==mods[name]['timestamp']","    if name not in headers:\n        try:\n            assert g.read(base,2)==b'MZ' and u32(base+u32(base+60)+8)==mods[name]['timestamp']\n            headers[name]=dict(readable=True,base=base)\n        except AssertionError as exc:\n            if name!='xwnown.dll' or str(exc)!='E14':raise\n            headers[name]=dict(readable=False,base=base,error='E14',identity='loader name/base/size plus complete relocated resident text and cold PE hash')\n        r['module_header_observations']=headers")
p=k/'trace.py';s=p.read_text();start=s.index("bc=K+kr");end=s.index('try:\n    command',start);sites=s[start:end]
s=s[:start]+"startup=pes['probe.exe'].OPTIONAL_HEADER.ImageBase+pes['probe.exe'].OPTIONAL_HEADER.AddressOfEntryPoint\nbc=dump=initret=precall=writecall=writeret=None;stages={}\n"+s[end:]
s=s.replace('    for a in [bc,dump,initret,precall,writecall]+list(stages):arm(a)','    arm(startup)')
insertion="""        if a==startup:
            K,discovery=discover(g.read,command(4594,'info registers'),pes['ntoskrnl.exe'],read(k.parent/'native-windows-nt5-kernel/kernel-publics.json')['symbols'])
            r['kernel_discovery']=discovery;r['kernel_base']=K
            observed=who();r.setdefault('startup_hits',[]).append(dict(owner=observed,registers=regs));assert len(r['startup_hits'])<=32
            if observed['image'].lower()!='probe.exe':
                remove(startup);step_observed();arm(startup);save();continue
            try:g.read(startup,32)
            except AssertionError as exc:
                if str(exc)!='E14':raise
                rows=r.setdefault('entry_unreadable',[]);rows.append(dict(owner=observed,registers=regs,error='E14'));assert len(rows)<=3
                remove(startup);step_observed();arm(startup);save();continue
            loaded=modules();r['module_list']=loaded
            process=int(observed['process'],16);peb=u32(process+field('_EPROCESS','Peb'));ldr=u32(peb+12);head=ldr+12;q=u32(head);seen=set()
            while q!=head:
                assert q and q not in seen and len(seen)<100;seen.add(q)
                loaded.append(dict(base=u32(q+24),size=u32(q+32),name=uni(q+44)));q=u32(q)
            assert next(v for v in loaded if v['name'].lower()=='probe.exe')['base']==pes['probe.exe'].OPTIONAL_HEADER.ImageBase
            r['startup_pin']=pin(startup);r['probe_entry_owner']=observed
SITES
            for address in [bc,dump,initret,precall,writecall]+list(stages):arm(address)
            remove(startup);r['kernel_sites_armed_utc']=utc();save();continue
""".replace('SITES','\n'.join('            '+line for line in sites.strip().splitlines()))
s=s.replace("        if not loaded:loaded=modules();r['module_list']=loaded",insertion+"        assert loaded")
s=s.replace("            bootbase=next", "            rambase=next(v['base'] for v in loaded if v['name'].lower()=='xwnown.dll')\n            sec=next(v for v in pes['xwnown.dll'].sections if v.Name.rstrip(b'\\0')==b'.text');offset=0\n            while offset<sec.Misc_VirtualSize:\n                idx=pin(rambase+sec.VirtualAddress+offset,min(48,sec.Misc_VirtualSize-offset));offset+=len(bytes.fromhex(r['runtime_pins'][idx]['raw']))\n            r['ram_text_identity']=dict(base=rambase,rva=sec.VirtualAddress,bytes=sec.Misc_VirtualSize)\n            r['ram_before']=ram_state()\n            bootbase=next")
s=s.replace("            r['boot_after']=video_state()","            r['boot_after']=video_state();r['ram_after']=ram_state()")
helper="""
def ram_state():
    raw=g.read(rambase+ram_symbols['XwnOwners'],32*12);slots=[]
    for i in range(32):
        owner,surface,device=struct.unpack_from('<3I',raw,i*12)
        if not owner:assert not surface and not device;continue
        values=list(struct.unpack('<7I',g.read(owner,28)))
        assert values[1]==device and values[2]==surface
        slots.append(dict(index=i,owner=owner,surface=surface,device=device,pdev7=values))
    assert slots and len(slots)<=32
    return dict(base=rambase,table_raw=raw.hex(),lock=u32(rambase+ram_symbols['XwnOwnerLock']),slots=slots)

def step_observed():
    for attempt in range(4):
        before=g.ask('g');who_before=who();reply=g.ask('s');after=g.ask('g');who_after=who()
        rows=r.setdefault('single_steps',[]);assert len(rows)<128
        rows.append(dict(before=before,after=after,before_owner=who_before,after_owner=who_after,reply=reply,attempt=attempt));save()
        assert reply.startswith(('T','S'))
        if before!=after or who_before!=who_after:return
    raise RuntimeError('Four real steps without CPU/owner progress')
"""
s=s.replace('def save():',helper+'\ndef save():');p.write_text(s,encoding='utf-8')
print('Fresh RAM crash kit created; not prepared or launched')
