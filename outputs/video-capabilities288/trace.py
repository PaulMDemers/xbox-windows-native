"""Attest and read the owned inventory; never alter guest data or registers."""
import datetime,hashlib,json,struct,sys,time,traceback
from pathlib import Path
from protocol import Remote,monitor
k=Path(__file__).resolve().parent;case=sys.argv[1];assert case=='emu001'
out=k/case;root=Path('E:/xwn288')/case
sys.path.insert(0,str(k.parent/'surface-bridge260'));from atomic_json import write_json
review=json.loads((k/'binary-review001.json').read_text());xbe=(root/'default.xbe').read_bytes()
assert hashlib.sha256(xbe).hexdigest()==review['xbe_sha256']
assert not (out/'trace.json').exists();point=False;stopped=True;g=None
r=dict(started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),passed=False,
       guest_memory_writes=False,guest_register_writes=False,mode_changes=False,physical_access=False)
def save():write_json(out/'trace.json',r)
def read(a,n,name):
    b=g.read(a,n);p=root/'private'/(name+'.bin');assert not p.exists();p.write_bytes(b)
    r.setdefault('reads',[]).append(dict(address=a,bytes=n,path=str(p),sha256=hashlib.sha256(b).hexdigest()));save();return b
try:
    g=Remote(4885);r['initial_stop']=g.ask('?');assert g.ask('qqemu.PhyMemMode')=='0'
    point=True;assert g.ask('Z1,%x,1'%review['checkpoint']['va'])=='OK'
    g.send('c');stopped=False;r['stop']=g.recv(120);stopped=True
    regs=struct.unpack('<16I',bytes.fromhex(g.ask('g'))[:64]);assert regs[8]==review['checkpoint']['va']
    stack=struct.unpack('<3I',read(regs[4],12,'stack'));caller,phase,record=stack
    assert phase==33 and record==review['record']
    assert read(regs[8],12,'checkpoint')==bytes.fromhex(review['checkpoint']['bytes'])
    call=review['calls'][0];assert caller==call['va']+5
    assert read(call['va'],5,'caller')==bytes.fromhex(call['bytes'])
    header=read(0x10000,4096,'header');assert header[:4]==b'XBEH'
    for offset in [0x104,0x108,0x10c,0x11c,0x120]:assert header[offset:offset+4]==xbe[offset:offset+4]
    text=next(s for s in review['sections'] if s['name']=='.text')
    assert hashlib.sha256(read(text['va'],text['raw_size'],'text')).hexdigest()==text['sha256']
    h=list(struct.unpack('<88I',read(record,352,'record')))
    assert h[:4]==[0x288c0de,1,352,0] and h[4]==0 and 0<h[23]<=16
    assert h[13]==0 and h[14] in (16384,32768)
    r['record']=h;r['modes']=[h[24+i*4:28+i*4] for i in range(h[23])]
    r['log_ok']=bool(h[5]);r['log_scope']='ISO D: is read-only; physical app-local log requires separate validation'
    r['passed']=True;save()
except BaseException as e:r['error']=repr(e);r['traceback']=traceback.format_exc();save()
finally:
    try:
        if g:
            if not stopped:r['interrupt']=g.interrupt();stopped=True
            if point:assert g.ask('z1,%x,1'%review['checkpoint']['va'])=='OK';point=False
            r['physical_mode_restored']=g.ask('qqemu.PhyMemMode')=='0'
            g.send('c');stopped=False;g.s.close();g=None
            time.sleep(12)
        r['final_status']=monitor(4884,'info status')
        monitor(4884,'stop');r['quit_reply']=monitor(4884,'quit',True);r['orderly_quit_sent']=True
    except BaseException as e:r['cleanup_error']=repr(e)
    r['remaining_breakpoint']=point;r['closed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();save()
print(json.dumps({n:r.get(n) for n in ['passed','error','cleanup_error','log_ok']},indent=2))
