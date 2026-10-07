"""One post-timeout read-only snapshot after the owned tracer releases its lock."""
import datetime,hashlib,json,socket,struct,sys,time
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'crash002';run=ws/'work/runs/nt5-controlled-dump-observe-crash002'
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (out/'timeout-snapshot.json').exists()
deadline=time.monotonic()+660
while not (out/'trace-finished.signal').exists():
    assert not (run/'cleanup.json').exists()
    if time.monotonic()>=deadline:raise RuntimeError('Owned tracer deadline exceeded')
    time.sleep(.5)
t=read(out/'trace.json')
if t['status']!='dump_capture_timeout':print('No timeout; no secondary snapshot');sys.exit(0)
assert t['guest_resumed'] and not t['armed_breakpoints_remaining'] and not (run/'cleanup.json').exists()
sys.path.insert(0,str(k.parent/'native-windows-prebuild'));from monitor_capture import command,acquire_monitor_lock
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
code=(k.parent/'native-windows-nt5-kernel/trace-entry.py').read_text();ns={};exec(code[code.index('class Remote:'):code.index('p=argparse.ArgumentParser()')],dict(socket=socket),ns);Remote=ns['Remote']
K=0x823df000;g=None;lock=acquire_monitor_lock(4594);r=dict(scope=__doc__,physical_access=False,ordinary_qualified=False,utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),source_sha256=sha(Path(__file__)),preceding_trace_sha256=sha(out/'trace.json'),callbacks=[],pins=[])
def u32(a):return struct.unpack('<I',g.read(a,4))[0]
def pin(a):
    module=next(v for v in t['module_list'] if v['base']<=a<v['base']+v['size']);name=module['name'].lower();mods=read(k/'modules.json')
    if name not in mods:
        r.setdefault('unverified_code',[]).append(dict(address=hex(a),module=name,base=hex(module['base']),rva=hex(a-module['base']),resident=g.read(a,64).hex(),reason='Module requires independent cold binary extraction and later verification'))
        return
    m=mods[name];p=Path(m['path']);assert sha(p)==m['sha256'];pe=pefile.PE(str(p));rva=a-module['base'];n=16
    while True:
        rel=[e.rva-rva for b in pe.DIRECTORY_ENTRY_BASERELOC for e in b.entries if e.type==3 and rva<=e.rva<rva+n];end=max([n]+[v+4 for v in rel]);assert end<=64
        if end==n:break
        n=end
    raw=pe.get_data(rva,n);b=bytearray(raw)
    for off in rel:struct.pack_into('<I',b,off,(struct.unpack_from('<I',b,off)[0]+module['base']-pe.OPTIONAL_HEADER.ImageBase)&0xffffffff)
    actual=g.read(a,n);assert b==actual
    r['pins'].append(dict(address=hex(a),module=name,base=hex(module['base']),rva=hex(rva),raw=raw.hex(),resident=actual.hex(),relocations=rel,source_sha256=m['sha256']))
try:
    command(4594,'stop');g=Remote(4595);g.ask('qSupported');g.ask('?')
    regs=dict(zip(['EAX','ECX','EDX','EBX','ESP','EBP','ESI','EDI','EIP'],struct.unpack('<9I',bytes.fromhex(g.ask('g'))[:36])))
    r['registers']={n:hex(v) for n,v in regs.items()};r['monitor_registers']=command(4594,'info registers');pin(regs['EIP'])
    r['stack']=dict(address=hex(regs['ESP']),bytes=g.read(regs['ESP'],512).hex())
    head=K+0x80af0;cur=u32(head);prev=head;seen=set();r['head']=dict(address=hex(head),bytes=g.read(head,8).hex())
    while cur!=head:
        assert cur and cur not in seen and len(seen)<64;seen.add(cur);b=g.read(cur,32);fwd,back,fn,buf,length,name,check=struct.unpack_from('<7I',b)
        assert back==prev;v=dict(address=hex(cur),raw=b.hex(),callback=hex(fn),buffer=hex(buf),length=length,name_pointer=hex(name),checksum=hex(check),checksum_valid=((fn+buf+length+name)&0xffffffff)==check,state=b[28]);r['callbacks'].append(v)
        if name:
            try:v['name_bytes']=g.read(name,16).hex()
            except Exception as exc:v['name_read_error']=repr(exc)
        if b[28]==2:pin(fn)
        prev,cur=cur,fwd
    assert u32(head+4)==prev
    r['final_dump_status']=hex(u32(K+0x6ce14))
    raw=out/'artifacts/timeout-ram.bin';assert not raw.exists();command(4594,'pmemsave 0 67108864 '+json.dumps(raw.as_posix()));r['ram_sha256']=sha(raw);r['captured']=True
except BaseException as exc:r['error']=repr(exc)
finally:
    if g:g.s.close()
    command(4594,'cont');r['resumed']=True;lock.close();(out/'timeout-snapshot.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({n:r[n] for n in ['captured','error','registers','callbacks','final_dump_status'] if n in r},indent=2))
