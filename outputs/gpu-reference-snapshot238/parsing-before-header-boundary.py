"""Bounded owned XBE mapping and after-write instruction discrimination."""
import re,struct

def snapshot_tuple(reply):
 """Parse complete published238 tuple; current PG row never implies current FIFO."""
 items=re.findall(r'(version|state|tuple_published|total|count|capacity|overwritten)=(\d+)',reply)
 assert len(items)==7 and len({a for a,b in items})==7
 fields={a:int(b) for a,b in items}
 assert len(fields)==7 and fields['version']==238 and fields['state']==3 and fields['tuple_published']==1
 assert fields['capacity']==256 and 0<=fields['count']<=256
 assert fields['total']<2**64 and fields['total']>=fields['count'] and fields['overwritten']==fields['total']-fields['count']
 raw=re.findall(r'row=([0-9,]+)',reply);assert len(raw)==fields['count']+1
 rows=[[int(v) for v in item.split(',')] for item in raw]
 assert all(len(r)==21 and r[0]<2**64 and r[1]<2**63 and all(v<2**32 for v in r[2:]) for r in rows)
 assert all(r[9]<16 and r[10] in [0,1] and (r[10] or not any(r[11:])) for r in rows)
 current=rows[0];assert current[0]==0 and current[2]==9 and current[10]==0
 events=rows[1:];assert [r[0] for r in events]==list(range(fields['total']-fields['count']+1,fields['total']+1))
 assert all(r[2] in [1,2,3,4,5] for r in events)
 labels={1:'FIFO access disabled',2:'NOP',4:'flip',8:'context-switch'}
 fifo_when=re.findall(r'(?<![a-z_])fifo_when=(\d+)',reply)
 metadata={}
 for key in ['renderer_valid','surface_count','surface_truncated']:
  values=re.findall(r'(?<![a-z_])'+key+r'=(\d+)',reply);assert len(values)==1;metadata[key]=int(values[0])
 assert len(fifo_when)==1 and 0<int(fifo_when[0])<=current[1]<2**63
 assert metadata['renderer_valid'] in [0,1] and metadata['surface_truncated'] in [0,1] and 0<=metadata['surface_count']<=128
 def vector(key,width):
  values=re.findall(r'(?<![a-z_])'+key+r'=([0-9,]+)',reply);assert len(values)==1
  values=list(map(int,values[0].split(',')));assert len(values)==width and all(v<2**64 for v in values);return values
 fifo=vector('fifo',14);context=vector('context',20)
 assert fifo[0] in [0,1] and fifo[1] in [0,1] and all(v<2**32 for v in fifo[2:])
 surfaces=[list(map(int,v.split(','))) for v in re.findall(r'(?<![a-z_])surface=([0-9,]+)',reply)]
 assert len(surfaces)==metadata['surface_count']
 for row in surfaces:
  assert len(row)==12 and all(v<2**64 for v in row) and row[5]<128 and all(v in [0,1] for v in row[6:9])
 if not metadata['renderer_valid']:assert not surfaces and not metadata['surface_truncated'] and not context[5] and not context[18] and not context[19]
 if metadata['surface_truncated']:assert len(surfaces)==128
 return dict(header=fields,current_pg_only=current,wait_mask=current[9],wait_labels=[v for bit,v in labels.items() if current[9]&bit],
             current_fifo_valid=True,fifo_when=int(fifo_when[0]),current_fifo=fifo,context=context,surfaces=surfaces,**metadata,events=events,
             limits='Distinct FIFO-then-PG worker samples; no producer halt, fence, readback, all-reference inventory or ownership.')

def xbe(data):
 assert len(data)>=0x178 and data[:4]==b'XBEH'
 base,headers,image=struct.unpack_from('<III',data,0x104)
 count,table=struct.unpack_from('<II',data,0x11c);encoded=struct.unpack_from('<I',data,0x128)[0]
 assert base==0x10000 and 0x178<=headers<=len(data) and 0<count<=32 and base<=table and table-base+count*56<=headers
 sections=[]
 for i in range(count):
  flags,va,size,offset,raw=struct.unpack_from('<5I',data,table-base+i*56)
  assert base<=va<2**32 and 0<size<=16*1024**2 and va+size<=base+image<=2**32
  assert offset+raw<=len(data) and raw<=size
  sections.append(dict(flags=flags,address=va,bytes=size,file_offset=offset,file_bytes=raw))
 candidates=[encoded^key for key in [0xa8fc57ab,0x94859d4b]]
 entries=[e for e in candidates if any(s['flags']&4 and s['address']<=e<s['address']+s['file_bytes'] for s in sections)]
 assert len(entries)==1
 return dict(base=base,header_bytes=headers,image_bytes=image,entry=entries[0],sections=sections)

def span(data,layout,address,n):
 assert 0<n<=4096 and 0<=address<=2**32-n
 found=[s for s in layout['sections'] if s['address']<=address and address+n<=s['address']+s['file_bytes']]
 assert len(found)==1,'Resident window outside exactly one file-backed section'
 s=found[0];offset=s['file_offset']+address-s['address'];return data[offset:offset+n]

def after_write_instruction(code,start,eip,registers,capstone):
 """Try bounded x86 decodes ending at post-write EIP; require exact effective address."""
 from capstone.x86_const import X86_OP_MEM,X86_OP_REG,X86_OP_IMM
 decoder=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32);decoder.detail=True
 names=['eax','ecx','edx','ebx','esp','ebp','esi','edi']
 regs=dict(zip(names,registers[:8]));result=[]
 for length in range(1,16):
  pc=eip-length;offset=pc-start
  if offset<0 or offset+length>len(code):continue
  prefixes={0xf0,0xf2,0xf3,0x26,0x2e,0x36,0x3e,0x64,0x65,0x66,0x67}
  # Refuse a suffix of an overridden instruction. This intentionally rejects
  # even a possible preceding instruction's prefix-valued final byte: without
  # a known forward boundary, false refusal is safer than false ownership.
  if code[offset] in prefixes or (offset and code[offset-1] in prefixes):continue
  items=list(decoder.disasm(code[offset:offset+length],pc));
  if len(items)!=1:continue
  insn=items[0]
  if insn.size!=length or insn.mnemonic!='mov' or len(insn.operands)!=2:continue
  dest,src=insn.operands
  if dest.type!=X86_OP_MEM or dest.size!=4 or dest.mem.segment:continue
  base_name=insn.reg_name(dest.mem.base) if dest.mem.base else None
  index_name=insn.reg_name(dest.mem.index) if dest.mem.index else None
  if (base_name and base_name not in regs) or (index_name and index_name not in regs):continue
  base=regs[base_name] if base_name else 0
  index=regs[index_name] if index_name else 0
  if (base+index*dest.mem.scale+dest.mem.disp)&0xffffffff!=0xfd400100:continue
  if src.type==X86_OP_REG:
   name=insn.reg_name(src.reg)
   if name not in regs:continue
   value=regs[name]
  elif src.type==X86_OP_IMM:value=src.imm&0xffffffff
  else:continue
  result.append(dict(address=pc,bytes=insn.size,hex=insn.bytes.hex(),mnemonic=insn.mnemonic,operands=insn.op_str,effective_address=0xfd400100,value=value))
 return result
