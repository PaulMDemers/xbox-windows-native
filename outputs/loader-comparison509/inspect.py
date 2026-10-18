"""Independent bounded structural parser for the observed single-section XBE family.

Field offsets/types follow pinned nxdk tools/cxbe/Xbe.h. This is not a kernel
loader emulator, signature validator or proof that a physical kernel accepts TLS.
"""
import hashlib,struct

def inspect(b):
 def need(ok,message):
  if not ok:raise ValueError(message)
 def u(o):
  need(0<=o<=len(b)-4,'DWORD outside file');return struct.unpack_from('<I',b,o)[0]
 need(0x1000<=len(b)<=2*1024**2 and b[:4]==b'XBEH','bounded XBE family')
 base,headers,size,ih=u(0x104),u(0x108),u(0x10c),u(0x110)
 need(base==0x10000 and 0x178<=ih<=headers<=0x1000 and size==len(b),'header/image bounds')
 def header(va,n):
  off=va-base;need(0<=off<=headers-n,'header pointer bounds');return off
 need(u(0x11c)==1,'single section only')
 so=header(u(0x120),56);v=struct.unpack_from('<9I',b,so)
 flags,va,vs,raw,rs,name,refs,head,tail=v
 need(flags==7 and va==base+0x1000 and raw==0x1000,'observed section layout/flags')
 need(vs==rs and 0<rs<=len(b)-raw and raw+rs==len(b),'raw extent')
 need(va+vs<=0xffffffff and va+vs==base+size,'virtual extent')
 no=header(name,1);end=b.find(b'\0',no,min(headers,no+9));need(end>=no,'bounded section name')
 section_name=b[no:end].decode('ascii')
 for ptr in [head,tail]:header(ptr,2)
 digest=hashlib.sha1(struct.pack('<I',rs)+b[raw:raw+rs]).digest()
 need(digest==b[so+36:so+56],'section SHA1')
 def data(address,n):
  need(va<=address and address+n<=va+vs,'section pointer bounds');off=raw+address-va;return b[off:off+n]
 ep=u(0x128)^0xa8fc57ab;data(ep,1)
 thunk=u(0x158)^0x5b6d40b6;ordinals=[]
 for i in range(64):
  q=struct.unpack('<I',data(thunk+i*4,4))[0]
  if q==0:break
  need(q&0x80000000 and 1<=q&0x7fffffff<=366,'ordinal bounds')
  ordinal=q&0x7fffffff;need(ordinal not in ordinals,'duplicate ordinal');ordinals.append(ordinal)
 else:raise ValueError('unterminated bounded thunk list')
 cert=header(u(0x118),4);cs=u(cert);need(0x1d0<=cs and cert+cs<=headers,'certificate bounds')
 tls=u(0x12c);tw=list(struct.unpack('<6I',data(tls,24))) if tls else None
 def in_image(address,n=1):return base<=address and address+n<=base+size
 tls_generic_sane=bool(tw and tw[0]<=tw[1] and in_image(tw[0],tw[1]-tw[0]) and in_image(tw[2],4) and (not tw[3] or in_image(tw[3],4)))
 return dict(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),base=base,header_size=headers,image_size=size,
  header_fields={f'{o:03x}':u(o) for o in range(0x104,0x178,4)},entry=ep,entry_file_offset=ep-base,
  entry_page=ep&~4095,section=dict(flags=flags,address=va,virtual_bytes=vs,raw_offset=raw,raw_bytes=rs,
  name=section_name,head_ref_address=head,tail_ref_address=tail,section_refcount=refs,sha1=digest.hex()),
  imports=ordinals,certificate_sha256=hashlib.sha256(b[cert:cert+cs]).hexdigest(),
  certificate_media=u(cert+0x9c),certificate_region=u(cert+0xa0),tls_address=tls,
  tls_words=tw,tls_generic_in_image_range_check=tls_generic_sane,tls_bytes_sha256=hashlib.sha256(data(tls,24)).hexdigest() if tls else None,
  rounded_image_end=(base+size+4095)&~4095,structural_scope_passed=True,
  signature_validated=False,TLS_runtime_acceptance_proved=False,physical_loader_qualified=False)
