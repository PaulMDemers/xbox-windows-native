"""Read own paused guest memory, decode the pre-entry record, discard raw RAM."""
import argparse,functools,hashlib,json,pathlib,re,struct,sys
out=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(out.parent/'native-windows-prebuild'))
from monitor_capture import command, acquire_monitor_lock
p=argparse.ArgumentParser();p.add_argument('--port',type=int,required=True);p.add_argument('--output',type=pathlib.Path,required=True);p.add_argument('--unarmed',action='store_true');p.add_argument('--kernel-mismatch',action='store_true');a=p.parse_args();preentry=a.unarmed or a.kernel_mismatch
raw=a.output.with_suffix('.ram')
lock=acquire_monitor_lock(a.port)
vm_status = command(a.port,'info status')
was_running = 'VM status: running' in vm_status
command(a.port,'stop')
try:
 regs=command(a.port,'info registers')
 command(a.port,'pmemsave 0 67108864 '+json.dumps(raw.resolve().as_posix()))
 ram=raw.read_bytes();assert len(ram)==64*1024*1024
 matches=[];start=0
 while True:
  pos=ram.find(b'XWNPPNT5',start)
  if pos<0:break
  words=struct.unpack_from('<23I',ram,pos)
  if words[2]==1 and words[3] in [30,40,99]:matches.append((pos,words))
  start=pos+1
 report={'scope':'Free-page lists built and complete PFN/color model verified; further MM initialization and partition handlers must not have run. Boot-driver and memory-descriptor layouts are decoded from pinned loader source, not the kernel PDB.','registers':regs,'record_candidates':[{'physical_address':hex(pos),'words':list(words)} for pos,words in matches]}
 if not matches:
  report['status']='no_completed_record'
 else:
  assert len(matches)==1
  pos,w=matches[0];cr3=w[8];assert w[3] in [40,99]
  def u32pa(addr):assert 0<=addr<=len(ram)-4;return struct.unpack_from('<I',ram,addr)[0]
  def pa(va):
   pde=u32pa((cr3&~4095)+4*(va>>22));assert pde&1,hex(va)
   assert not pde&128,'Unexpected large page'
   pte=u32pa((pde&~4095)+4*((va>>12)&1023));assert pte&1,hex(va)
   return (pte&~4095)+(va&4095)
  def read(va,size):
   b=bytearray()
   while size:
    n=min(size,4096-(va&4095));at=pa(va);assert at+n<=len(ram);b+=ram[at:at+n];size-=n;va+=n
   return bytes(b)
  def u32(va):return struct.unpack('<I',read(va,4))[0]
  def uni(va):
   length,maximum,buf=struct.unpack('<HHI',read(va,8));assert length<=maximum and length<4096
   return read(buf,length).decode('utf-16le') if length else ''
  def asciiz(va):
   b=bytearray()
   for i in range(1024):
    c=read(va+i,1)
    if c==b'\0':return b.decode('ascii')
    b+=c
   raise AssertionError('Unterminated string')
  def walk(head):
   node=u32(head);prev=head;seen=set()
   while node!=head:
    assert node not in seen and len(seen)<256;seen.add(node)
    assert u32(node+4)==prev,'Broken backlink'
    yield node
    prev=node;node=u32(node)
   assert u32(head+4)==prev
  lpb=w[5];assert pa(lpb)==w[4]
  layouts=json.loads((out.parent/'native-windows-nt5-kernel/handoff-pdb-layouts.json').read_text())
  df=layouts['_LDR_DATA_TABLE_ENTRY']['fields'];offset=lambda n:df[n]['offset']
  modules=[]
  for node in walk(lpb):
   dte=node-offset('InLoadOrderLinks');base=u32(dte+offset('DllBase'));size=u32(dte+offset('SizeOfImage'))
   assert read(base,2)==b'MZ'
   modules.append({'dte':hex(dte),'name':uni(dte+offset('BaseDllName')),'base':hex(base),'size':size,'entry':hex(u32(dte+offset('EntryPoint')))})
  drivers=[{'file':uni(n+8),'registry':uni(n+16),'dte':hex(u32(n+24))} for n in walk(lpb+16)]
  descriptors=[{'type':u32(n+8),'base_page':u32(n+12),'pages':u32(n+16)} for n in walk(lpb+8)]
  assert len(modules)==w[13] and len(drivers)==w[14] and len(descriptors)==w[15]+(0 if preentry else 2)
  names={m['name'].lower() for m in modules};assert {'ntoskrnl.exe','hal.dll','bootvid.dll'}<=names
  assert all(d['dte'] in {m['dte'] for m in modules} for d in drivers)
  assert w[7]&0x80000000 and w[9:12]==(40,5,0)
  ext=u32(lpb+88);assert u32(ext)==40
  nls=u32(lpb+72)
  nls_pointers=[u32(nls+i*4) for i in range(3)]
  assert all(read(v,2) for v in nls_pointers)
  assert read(u32(lpb+44),4)==b'regf'
  assert read(w[6],1)
  # Resolve every mapped import against mapped exports, including forwarders.
  module_map={m['name'].lower():m for m in modules}
  def directory(m,index):
   base=int(m['base'],16);nt=base+u32(base+60)
   assert read(nt,4)==b'PE\0\0' and read(nt+24,2)==b'\x0b\x01'
   return base,u32(nt+24+96+index*8),u32(nt+24+100+index*8)
  @functools.lru_cache(maxsize=None)
  def export(lib,symbol,depth=0):
   assert depth<8
   if lib.lower() not in module_map:
    lib=next(n for n in module_map if n.rsplit('.',1)[0]==lib.lower().rsplit('.',1)[0])
   m=module_map[lib.lower()];base,rva,size=directory(m,0);assert rva
   e=base+rva;count=u32(e+20);functions=base+u32(e+28)
   if isinstance(symbol,int):index=symbol-u32(e+16)
   else:
    n=u32(e+24);names=base+u32(e+32);ordinals=base+u32(e+36);index=None
    for j in range(n):
     if asciiz(base+u32(names+j*4))==symbol:
      index=struct.unpack('<H',read(ordinals+j*2,2))[0];break
    assert index is not None,(lib,symbol)
   assert 0<=index<count,(lib,symbol,index,count)
   target=u32(functions+index*4);assert target
   if rva<=target<rva+size:
    forward=asciiz(base+target);other,name=forward.rsplit('.',1)
    return export(other,int(name[1:]) if name.startswith('#') else name,depth+1)
   return base+target
  bindings=[]
  for m in modules:
   base,rva,size=directory(m,1)
   if not rva:continue
   desc=base+rva
   for di in range(128):
    original,stamp,forward,libname,iat=struct.unpack('<5I',read(desc+di*20,20))
    if not any((original,stamp,forward,libname,iat)):break
    assert original,'No preserved lookup table: '+m['name']
    lib=asciiz(base+libname);count=0
    for j in range(8192):
     thunk=u32(base+original+j*4)
     if not thunk:break
     # Pinned FreeLoader changes name RVAs in the lookup table into VAs.
     if base<=thunk<base+m['size']:sym=asciiz(thunk+2)
     else:
      assert thunk&0x80000000,(m['name'],hex(thunk))
      sym=thunk&0xffff
     expected=export(lib,sym);actual=u32(base+iat+j*4)
     assert actual==expected,(m['name'],lib,sym,hex(actual),hex(expected))
     count+=1
    else:raise AssertionError('Unterminated import table')
    bindings.append({'source':m['name'],'target':lib,'resolved_entries':count})
   else:raise AssertionError('Unterminated import descriptors')
  report['mapped_import_bindings']=bindings
  report['mapped_import_entries_verified']=sum(b['resolved_entries'] for b in bindings)
  # HAL image includes relocations; compare its mapped .text with relocated input.
  sys.path.insert(0,str(out.parents[1]/'work/python-packages'))
  import pefile
  integrity=[]
  for name,file in [('hal.dll',(out.parent/'native-windows-physical-freelist/package/loader/halxboxnt5.dll' if a.unarmed else out/'package/loader/halxboxnt5.dll')),('bootvid.dll',out/'package/loader/xboxbvid.dll'),('ntoskrnl.exe',out.parent/'native-windows-nt5/installed-files/WINNT/system32/ntoskrnl.exe')]:
   m=module_map[name];base=int(m['base'],16);pe=pefile.PE(str(file));pe.relocate_image(base)
   image=bytearray(pe.get_memory_mapped_image());sections=[]
   # NT5 places loader-modified import tables in an executable section.
   # Reproduce only the documented binding edits from the original PE inputs.
   for imp in getattr(pe,'DIRECTORY_ENTRY_IMPORT',[]):
    lib=imp.dll.decode()
    for j,symbol in enumerate(imp.imports):
     sym=symbol.name.decode() if symbol.name else symbol.ordinal
     struct.pack_into('<I',image,imp.struct.FirstThunk+j*4,export(lib,sym))
     if symbol.name:
      slot=imp.struct.OriginalFirstThunk+j*4
      original=struct.unpack_from('<I',image,slot)[0]
      struct.pack_into('<I',image,slot,base+original)
   if name=='ntoskrnl.exe' and not preentry:
    # Supplied 2195.7376 startup routine RVA 152894 swaps IDT high-offset
    # and selector words for all 256 template entries before first HAL call.
    assert hashlib.sha256(file.read_bytes()).hexdigest()=='84172dbd7e148dcf6e87c2e75e0c8716b3afcb6041b39802f63fd7fb67d7a152'
    for entry in range(256):
     pos=0x151918+entry*8
     image[pos+2:pos+4],image[pos+6:pos+8]=image[pos+6:pos+8],image[pos+2:pos+4]
    report['expected_kernel_mutation']={'routine_rva':'0x152894','idt_template_rva':'0x151918','entries':256,'operation':'swap 16-bit fields at offsets 2 and 6'}
   if name=='ntoskrnl.exe' and not preentry:
    registry=json.loads((out/'registry-init-inputs.json').read_text())
    assert hashlib.sha256((out/'package/WINNT/system32/config/system').read_bytes()).hexdigest()==registry['hive_sha256']
    values=registry['values'];assert values['Select\\Current']['bytes']=='01000000'
    updates=[]
    for suffix,buffer,length,kind in [('Nls\\Language\\Default',0x164f68,0x164f80,0x164f84),('Nls\\Language\\InstallLanguage',0x164f88,0x164fa0,0x164fa4)]:
     value=values['ControlSet001\\Control\\'+suffix];data=bytes.fromhex(value['bytes']);assert value['type']==1 and len(data)==10
     image[buffer:buffer+len(data)]=data
     struct.pack_into('<I',image,length,len(data));struct.pack_into('<I',image,kind,value['type'])
     updates.append({'source':suffix,'buffer_rva':hex(buffer),'data':data.hex(),'length':len(data),'type':value['type']})
    suite=values['ControlSet001\\Control\\ProductOptions\\ProductSuite'];assert suite=={'type':7,'bytes':'0000'}
    struct.pack_into('<II',image,0x164fa8,2,7)
    assert values['ControlSet001\\Control\\Session Manager\\Memory Management\\VerifyDrivers'] is None
    struct.pack_into('<I',image,0x164f54,0xffffffff)
    report['expected_registry_initialization_mutations']={'routine':'CmGetSystemControlValues','language_buffers':updates,'suite_length_type':[2,7],'missing_verify_drivers_length':'0xffffffff','scope':'Only named INIT data fields are reproduced; no instruction range is ignored.'}
   for sec in pe.sections:
    if sec.Characteristics&0x20000000:
     start=sec.VirtualAddress;size=sec.Misc_VirtualSize
     expected=image[start:start+size];actual=read(base+start,size)
     if actual!=expected:
      differences=[{'rva':hex(start+i),'actual':aa,'expected':bb} for i,(aa,bb) in enumerate(zip(actual,expected)) if aa!=bb]
      a.output.with_name('code-differences.json').write_text(json.dumps({'module':name,'section':sec.Name.rstrip(b'\0').decode(),'differences':differences},indent=2)+'\n')
      from PIL import Image
      Image.frombytes('RGB',(w[20],w[21]),ram[w[17]:w[17]+w[18]],'raw','BGRX',w[22],1).save(a.output.with_name('unverified-framebuffer.png'))
     assert actual==expected,(name,sec.Name,[(hex(start+i),aa,bb) for i,(aa,bb) in enumerate(zip(actual,expected)) if aa!=bb][:16])
     sections.append(sec.Name.rstrip(b'\0').decode())
   integrity.append({'module':name,'source_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'relocated_executable_sections_equal_after_expected_import_binding':sections})
  report['mapped_code_integrity']=integrity
  assert w[3]==99 and w[19]==0x50414745 and 'HLT=1' in regs
  assert len(modules)==20 and len(drivers)==14 and w[12]==1810432
  assert tuple(w[20:23]) in [(640,480,2560),(1024,576,4096)]
  assert w[18]==w[21]*w[22] and 0x03c00000<=w[17]<=0x04000000-w[18]
  assert (u32pa((cr3&~4095)+768*4)&~4095)==(cr3&~4095)
  fb_start=w[17]//4096;fb_end=(w[17]+w[18])//4096
  assert any(d['type']==6 and d['base_page']<=fb_start and d['base_page']+d['pages']>=fb_end for d in descriptors)
  for address in range(w[17],w[17]+w[18],4096):
   if preentry:
    assert pa(address)==address
   else:
    assert not u32pa((cr3&~4095)+4*(address>>22))&1
   assert pa(address+0x80000000)==address
   pde=u32pa((cr3&~4095)+4*((address+0x80000000)>>22));pte=u32pa((pde&~4095)+4*((address>>12)&1023))
   assert pte&0x1b==0x1b
  protected=[(pa(int(m['base'],16)),pa(int(m['base'],16))+m['size']) for m in modules]
  protected.extend([(pa(u32(lpb+44)),pa(u32(lpb+44))+w[12]),(w[17],w[17]+w[18]),(0,4096)])
  display_pt=u32pa((cr3&~4095)+4*((w[17]+0x80000000)>>22))&~4095
  protected.extend([(cr3&~4095,(cr3&~4095)+4096),(display_pt,display_pt+4096)])
  for d in descriptors:
   if d['type']==2:
    start=d['base_page']*4096;end=start+d['pages']*4096
    assert all(end<=lo or start>=hi for lo,hi in protected),d
  report['framebuffer_mapping']={'width':w[20],'height':w[21],'pitch':w[22],'pa':hex(w[17]),'bytes':w[18],'high_alias_pages_verified':w[18]//4096,'identity_mapping_present':preentry,'uncached_write_through':True,'firmware_reserved':True}
  from PIL import Image
  display_pixels=ram[w[17]:w[17]+w[18]]
  display_path=a.output.with_name('audited-framebuffer.png')
  Image.frombytes('RGB',(w[20],w[21]),display_pixels,'raw','BGRX',w[22],1).save(display_path)
  report['framebuffer_image']={'file':display_path.name,'method':'audited guest RAM using record dimensions and pitch','sha256':hashlib.sha256(display_path.read_bytes()).hexdigest()}
  report['no_free_descriptor_overlaps_images_hive_framebuffer_or_page_zero']=True
  expected_page=0
  for d in descriptors:
   assert d['base_page']==expected_page and d['pages']>0,d
   expected_page+=d['pages']
  assert expected_page==0x4000,hex(expected_page)
  report['descriptors_and_native_allocations_cover_64_mib']=True
  report['committed_native_allocation']={'base_page':0x160,'pages':623} if not preentry else None
  report['kernel_entered']=False

  report.update(status='physical_paging_halt_verified' if w[3]==99 else 'guest_validation_failed',lpb_va=hex(lpb),kernel_entry=hex(w[6]),cr0=hex(w[7]),cr3=hex(w[8]),extension={'size':w[9],'version':[w[10],w[11]],'bytes':read(ext,40).hex()},hive_bytes=w[12],modules=modules,boot_drivers=drivers,memory_descriptors=descriptors,nls_pointers=[hex(v) for v in nls_pointers],paths={n:asciiz(u32(lpb+o)) for n,o in [('arc_boot',52),('arc_hal',56),('nt_boot',60),('nt_hal',64),('options',68)]},lists_have_valid_backlinks=True,raw_ram_sha256=hashlib.sha256(ram).hexdigest())
 entry_matches=[]
 # Search the separate early-entry record, including failure state.
 at=0
 while True:
  at=ram.find(b'XWNZPNT5' if preentry else b'XWNYPNT5',at)
  if at<0:break
  e=struct.unpack_from('<96I' if preentry else '<256I',ram,at)
  if e[0]==(0x5a4e5758 if preentry else 0x594e5758) and e[1]==0x35544e50 and e[2]==1 and e[3] in (30,40,90):entry_matches.append((at,e))
  at+=1
 if len(entry_matches)!=1:
  report['status']='no_unique_mi_checkpoint'
  report['entry_record_candidates']=[{'pa':hex(at),'words':list(words)} for at,words in entry_matches]
  a.output.write_text(json.dumps(report,indent=2)+'\n')
 assert len(entry_matches)==1,entry_matches
 entry_pa,e=entry_matches[0]
 report['entry_record']={'pa':hex(entry_pa),'words':list(e)}
 if e[3]==90:
  assert report['status']=='physical_paging_halt_verified'
  assert e[4]==e[13]==w[5] and e[12]==0 and e[11]==e[16]==w[8]
  assert e[15]&0x80000000 and e[6]<=e[14]<e[6]+e[7]
  assert tuple(e[17:22])==(w[20],w[21],w[22],w[17],w[18])
  site=read(e[14]-6,6)
  assert site[:2]==b'\xff\x15',site.hex()
  slot=struct.unpack('<I',site[2:])[0]
  expected=export('hal.dll','HalInitSystem')
  assert u32(slot)==expected
  report['native_callsite']={'return_address':hex(e[14]),'instruction':site.hex(),'iat_slot':hex(slot),'target':hex(expected)}
  assert e[24:26]==(200,1) and e[28:32]==(0xfffffffb,100,1,1)
  assert e[26]==e[27]
  processor_site=read(e[26]-6,6)
  assert processor_site[:2]==b'\xff\x15'
  processor_slot=struct.unpack('<I',processor_site[2:])[0]
  assert u32(processor_slot)==export('hal.dll','HalInitializeProcessor')
  report['processor_callsite']={'return_address':hex(e[26]),'instruction':processor_site.hex(),'iat_slot':hex(processor_slot)}
  report['status']='kernel_system_ptes_verified'
  report['kernel_entered']=True
  report['original_hal_processor_init_executed']=True
  report['original_hal_phase0_body_executed']=True
  report['hal_phase0_completed']=True
  assert e[36]==1 and e[37]==e[38]
  assert e[39:43]==(0x1800,0xffff,50,0x7f) and e[43]&0x200 and e[44]==0
  assert e[14]==e[45]
  report['timer_calibration_reached']=True
  report['timer_calibration_returned']=True
  report['clock_initialization_reached']=True
  report['partition_hooks_registered']=True
  report['partition_handlers_entered']=False
  report['bios_initialization_reached']=True
  report['hal_phase0_body_completed']=True
  report['hal_phase0_returned']=True
  assert e[80]==e[6]+0x159bd7 and e[81]==0 and e[82]==e[4]
  assert e[83]==e[6]+0x155b55 and e[84]&0x80000000 and e[85]==e[11]
  assert e[87]==1 and read(e[80],8)==bytes.fromhex('6a006a00e88cb2fe')
  mm_call=read(e[83]-5,5);assert mm_call[0]==0xe8
  assert e[83]+struct.unpack('<i',mm_call[1:])[0]==e[6]+0x157d78
  assert e[90:94]==(512,1,e[20]+0x80000000,1)
  assert e[8]<=e[88]<e[8]+module_map['hal.dll']['size']
  assert e[8]<=e[94]<e[8]+module_map['hal.dll']['size']
  assert pa(e[95])==entry_pa
  assert all(not u32pa((cr3&~4095)+i*4)&1 for i in range(512))
  report['low_mapping_transition']={'absent_low_pdes':512,'tlb_flushed':True,'high_framebuffer_va':hex(e[92]),'checkpoint_va':hex(e[94]),'record_va':hex(e[95]),'record_in_hal':e[8]<=e[95]<e[8]+module_map['hal.dll']['size']}
  assert report['low_mapping_transition']['record_in_hal']
  assert e[96:99]==(0x3bff,1,0x3bff)
  assert e[104:108]==(0x3bff,2,26,1) and e[110]==0x3bfd
  assert e[99]==0 and e[108]==e[109] and e[100]==e[109] and e[111]==e[4]+8
  allowed=[d for d in descriptors if d['type'] in (2,4,5,8)]
  largest=max(allowed,key=lambda d:d['pages'])
  low=max((d for d in allowed if d['base_page']<0x1000),key=lambda d:min(d['pages'],0x1000-d['base_page']))
  assert (u32(e[108]+8),u32(e[108]+12),u32(e[108]+16))==(5,0x160,0x2000)
  assert largest==low=={'type':5,'base_page':0x160,'pages':0x2000}
  assert (u32(e[100]+8),u32(e[100]+12),u32(e[100]+16))==(low['type'],low['base_page'],low['pages'])
  assert e[102]==0xea0
  from sizing_model import verify_sizing
  sizing=verify_sizing(read,e[6],e[208],e[99],after=True,pool=True,initialized=True,pfn=True,mapped=True,committed=True,sysptes=True);report['memory_sizing']=sizing
  g=sizing['globals']
  assert e[112:128]==(g['initial_pool'],g['maximum_pool'],sizing['pfn_color_pages'],g['colors'],g['pool_start'],g['system_start'],int(sizing['first_pde'],16),int(sizing['last_pde'],16),0x160,0x2000,0x160,0x2000,g['possible_highest'],0,sizing['page_table_pages_planned'],1)
  assert e[101]==e[114] and e[103]==e[119]
  report['ram_scan']={'native_pages':e[96],'lowest_page':e[97],'highest_page':e[98],'earlier_limits_pages':e[110],'bios_reserved_pages':e[105],'descriptor_count':e[106],'largest_candidate':largest,'below_16_mib_candidate':low,'native_results_match_descriptor_model':True,'first_allocation_completed':True}
  assert e[128:136]==(1,28,352,8192,e[11],1,1,1)
  assert e[136]==e[89] and e[137]==e[6]+0x158439
  assert e[139:144]==(28,975,7569,0xc03fef7c,0x163)
  assert e[147:151]==(1,623,504,0xfe4af000)
  from pool_model import verify_pool_initialized
  report['pool_initialized']=verify_pool_initialized(read,e[6],pfn=True)
  assert e[152:160]==(1,1,4,500,5340,0xfe6a7000,0xc03f9aa0,0xc03fef7c)
  assert e[162:167]==(500,4,1,0x373,0x9ff)
  report['pool_backing']={'pages_mapped':504,'virtual_address':hex(e[150]),'first_pfn':380,'next_pfn':884,'remaining_pages':7660,'all_ptes_verified':True}
  from pfn_model import verify_pfn_backing
  report['pfn_backing']=verify_pfn_backing(read,e[6],e[208],mapped=True,committed=True,sysptes=True)
  from mapped_pfn_model import snapshot,verify,permission_mask
  from mapped_pfn_model import expected
  mapped=snapshot(read,e[6]);_,_,report['mapped_pfns']=expected(mapped)
  from freewalk_model import verify_final
  free=verify_final(read,e[6],[[d['type'],d['base_page'],d['pages']] for d in descriptors],sysptes=True)
  free_set=set(free.pop('free_pfns'))
  assert all(p not in free_set for lo,hi in protected for p in range(lo//4096,(hi+4095)//4096))
  assert all(p not in free_set for p in [0,1,2,e[11]>>12])
  report['free_lists']=free
  from sysptes_model import verify as verify_sysptes
  report['system_ptes']=verify_sysptes(read,e[6])
  assert e[238]==e[6]+0x159898 and e[240:247]==(1,1,6,22702,1880,650,20822)
  assert e[247]==e[248]!=0 and e[249]==e[251]==e[252]==e[253]==e[254]==1
  assert read(e[238],8)==bytes.fromhex('807dfe008b15')+struct.pack('<H',(e[6]+0x81ab0)&0xffff)
  assert e[197:199]==(1,1) and e[214:218]==(1,20,1,1)
  assert e[210]==e[211]==e[218]==free['available'] and e[212]==free['new_inuse'] and e[213]==free['preserved']
  assert e[219:221]==(1,1) and e[221]==e[196] and e[222:224]==(0x3c00,1024)
  assert e[224]==e[6]+0x1596f3 and read(e[224],8)==bytes.fromhex('8b45088b400ce98e')
  assert e[232:236]==(1,0,0xffff,1) and e[236]==e[237]!=0
  assert e[8]<=e[208]-104<e[208]+12<=e[8]+module_map['hal.dll']['size']
  assert read(e[208]+4,8)==struct.pack('<2I',e[83],e[4])
  assert e[188:196]==(0x3cf,0x1b23,0x2160,0x160,622,0x3cf,0x1d91,1)
  assert e[196]==e[144]
  report['descriptor_reconciliation']={'native_count':e[189],'reconciled_count':e[194],'restored_pages':e[192],'original_extent_end':e[190],'full_accounting_verified':True}
  assert e[176]==e[177] and e[178]==e[187]==1
  assert e[179:184]==tuple(report['mapped_pfns'][n] for n in ['pde_count','present_pte_count','mapped_pfn_updates','populated_pfn_records','color_heads'])
  assert e[167:176]==(1,1,0xffb85000,90,1,0xffff,1,0,1)
  assert e[144]==e[145] and e[144]!=0 and e[146]==1
  assert read(e[137],5)==bytes.fromhex('8b72100372')
  symbols=json.loads((out/'map-boundary-audit.json').read_text())['symbols_rva']
  assert e[138]==e[8]+int(symbols['_HalpXwnPtBeforeEntry'],16)
  shadow=struct.unpack('<1024I',read(e[8]+int(symbols['_XwnPtDirectory'],16),4096))
  first=(int(sizing['first_pde'],16)-0xc0300000)//4
  last=(int(sizing['last_pde'],16)-0xc0300000)//4
  for i,old in enumerate(shadow):
   actual=u32pa((cr3&~4095)+4*i)
   if not first<=i<=last:
    expected=old
    if old&1:expected|=permission_mask(read,e[6],0xc0000000+i*4096)|permission_mask(read,e[6],0xc0300000+i*4)
    assert actual&~0x60==expected&~0x60
  assert all((352+623)*4096<=lo or 352*4096>=hi for lo,hi in protected)
  report['first_page_tables']={'tables_created':28,'first_pfn':352,'next_pfn':380,'remaining_pages':8164,'preallocation_guard_passed':True,'both_kernel_hooks_restored':True,'unrelated_pdes_have_only_expected_permission_changes':True,'descriptor_hash_with_audited_commit_verified':True}
  report['kernel_mm_checkpoint']={'phase':e[81],'caller':hex(e[83]),'target':hex(e[80]),'entry_bytes_restored':True,'memory_manager_prefix_entered':True,'machine_dependent_body_entered':True,'ram_descriptor_scan_completed':True,'first_page_table_allocation_completed':True,'free_page_lists_built':True,'stopped_before_further_mm_initialization':True,'method':'temporary five-byte mid-function JMP; restored before final audit'}
  assert e[70]==1 and e[71]==0x2000 and e[72]==0
  assert e[73]==len(descriptors)==26 and e[74]==2 and e[75]==0xffff
  assert e[76]&0x200 and e[77:80]==(0,3,1)
  for page in [e[70],e[71]//4096]:
   assert any(d['type']==26 and d['base_page']==page and d['pages']==1 for d in descriptors)
   assert all(page*4096+4096<=lo or page*4096>=hi for lo,hi in protected)
  report['bios_allocation_state']={'fallback_pfn':e[70],'buffer_pa':hex(e[71]),'descriptor_count':e[73],'allocation_descriptors_used':e[74],'reserved_mask':e[78],'phase1_mapping_active':False}
  report['storage_initialization_reached']=False
  assert e[66:69]==(15,15,0xffff) and e[69]&0x200
  report['partition_hook_state']={'installed_mask':e[66],'saved_originals_mask':e[67],'pic_mask':hex(e[68]),'eflags':hex(e[69])}
  assert e[55:61]==(16875,150000,15,16875,150000,1)
  assert e[61]==0xffff and e[62]&0x200 and not e[63]&0x40
  assert e[64]<=e[55] and e[65]==10000
  query=read(export('ntoskrnl.exe','KeQueryTimeIncrement'),6)
  assert query[0]==0xa1 and query[5]==0xc3,query.hex()
  increment_va=struct.unpack_from('<I',query,1)[0]
  assert u32(increment_va)==e[56]
  report['kernel_time_increment']={'value':u32(increment_va),'global_va':hex(increment_va),'query_instructions':query.hex()}
  report['clock_state']={'rollover':e[55],'increment_100ns':e[56],'pic_mask':hex(e[61]),'rtc_b':hex(e[63]),'pit_count':e[64],'profile_stopped':bool(e[60])}
  assert e[46:49]==e[49:52] and e[52]==0xffff and e[53]&0x200
  assert 0<e[54]<=1000000 and e[33]==e[54]
  assert read(e[51]+0x38*8,8)==struct.pack('<2I',e[49],e[50])
  report['rtc_state']={'stall_factor':e[54],'idt_before':[hex(x) for x in e[46:49]],'idt_after':[hex(x) for x in e[49:52]],'pic_mask':hex(e[52]),'eflags_before_final_halt':hex(e[53])}
 elif e[3]==40 and e[22] in (1,3):
  report['status']='kernel_contract_rejected_before_entry' if e[22]==3 else 'unarmed_hal_rejected_before_kernel'
  report['kernel_entered']=False
 else:raise AssertionError('Unexpected entry record state: '+str(e))
 report['vm_status_before_capture'] = vm_status.split('VM status:')[-1].splitlines()[0].strip()
 a.output.write_text(json.dumps(report,indent=2)+'\n')
 print(report['status'])
finally:
 raw.unlink(missing_ok=True)
 try:
  if was_running:command(a.port,'cont')
 finally:lock.close()
