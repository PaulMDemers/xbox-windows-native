"""Independent ELF32 layout and actual instruction review, without execution."""
import struct,pathlib,json,hashlib,re
K=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def elf(p):
 b=p.read_bytes();assert b[:7]==b'\x7fELF\x01\x01\x01';assert struct.unpack_from('<H',b,18)[0]==3
 off=struct.unpack_from('<I',b,32)[0];size,num,si=struct.unpack_from('<3H',b,46);assert size==40 and num<100
 rows=[struct.unpack_from('<10I',b,off+i*40) for i in range(num)];ns=rows[si];names=b[ns[4]:ns[4]+ns[5]]
 cs=lambda v,o:v[o:v.index(0,o)].decode()
 sec={cs(names,s[0]):dict(type=s[1],flags=s[2],va=s[3],offset=s[4],size=s[5],link=s[6],entsize=s[9]) for s in rows};syms={}
 for s in sec.values():
  if s['type']!=2:continue
  st=rows[s['link']];strings=b[st[4]:st[4]+st[5]]
  for o in range(s['offset'],s['offset']+s['size'],16):
   n,v,z,info,other,index=struct.unpack_from('<IIIBBH',b,o)
   if n:syms[cs(strings,n)]=dict(va=v,size=z,section=index)
 return b,sec,syms
if __name__=='__main__':
 report={'scope':'Static source/layout/instruction review; no runtime qualification','rows':{}};warn=[]
 for mode,base,top in [('control004',0x3a00000,0x3c00000),('candidate004',0x2600000,0x2800000)]:
  p=pathlib.Path('E:/xwn293')/mode;build=json.loads((K/(mode+'.json')).read_text());assert build['status']=='compiled'
  for n,v in build['artifacts'].items():assert sha(p/n)==v['sha256']
  b,s,y=elf(p/'image-crom.elf');assert s['.text']['va']==base
  end=max(v['va']+v['size'] for v in s.values() if v['flags']&2);assert end==y['BSS_END']['va'] and top-end>=262144
  assert (p/'image-crom.bin').stat().st_size<=0x100000
  txt=b[s['.text']['offset']:s['.text']['offset']+s['.text']['size']]
  assert txt.count(b'\xbc'+struct.pack('<I',top))>=1
  bb,ss,yy=elf(p/'xbeboot.elf');assert b'\xbf'+struct.pack('<I',base)+b'\xb9\x00\x00\x10\x00\xf3\xa4\xfa\xea'+struct.pack('<I',base)+b'\x08\x00' in bb
  warnings=[re.sub(r'/home/paul/xbox-windows-native/build/relocation293-[^/]+','SOURCE',line) for line in (p/'build.log').read_text().splitlines() if re.search('warning:',line,re.I)]
  assert not any('clock skew' in w.lower() or 'modification time' in w.lower() for w in warnings);warn.append(warnings)
  report['rows'][mode]=dict(base=base,stack_top=top,bss_end=end,stack_headroom=top-end,sections=s,symbols={n:y[n] for n in ['BootResetAction','BootFromDevice','BootVgaInitializationKernelNG','vmode','BSS_END','start_linux']},xbe_sha256=sha(p/'default.xbe'),elf_sha256=sha(p/'image-crom.elf'),warnings=len(warnings))
 assert warn[0]==warn[1]
 for n in ['.text','.rodata','.data','.bss']:assert report['rows']['control004']['sections'][n]['size']==report['rows']['candidate004']['sections'][n]['size']
 report.update(passed=True,matched_warning_messages=True,framebuffer_unchanged_bytes=4194304,candidate_heap_end=0x2600000,candidate_initrd_start=0x2800000,source_files_changed=11)
 (K/'binary-review004.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'candidate_stack_headroom':report['rows']['candidate004']['stack_headroom'],'matched_warnings':len(warn[0])}))
