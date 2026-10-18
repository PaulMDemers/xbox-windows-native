# SPDX-License-Identifier: MIT
"""Actual packet parser, chunk reader and capture body; socket/guest bytes modeled."""
import ast,hashlib,json,struct,traceback
from pathlib import Path
from protocol003 import Remote
K=Path(__file__).resolve().parent;OUT=K/'host005.json';assert not OUT.exists()
P=Path('C:/xwn522/transport001');assert not P.exists();P.mkdir(parents=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
class Wire:
    def __init__(self,kind='valid',fragment=7):self.kind=kind;self.fragment=fragment;self.buf=bytearray();self.commands=[];self.timeouts=[]
    def settimeout(self,n):assert n>0;self.timeouts.append(n)
    def sendall(self,b):
        if b==b'+':return
        assert b.startswith(b'$') and b[-3:-2]==b'#'
        body=b[1:-3];assert int(b[-2:],16)==sum(body)%256
        self.commands.append(body.decode())
        if self.kind=='stops':payload=b'S05'
        elif self.kind=='error':payload=b'E14'
        else:
            assert body.startswith(b'm');a,n=(int(x,16) for x in body[1:].split(b','))
            payload=bytes((a+i)%251 for i in range(n)).hex().encode()
            if self.kind=='short':payload=payload[:-2]
            if self.kind=='long':payload+=b'00'
            if self.kind=='hex':payload=b'zz'+payload[2:]
        check=(sum(payload)+(self.kind=='checksum'))%256
        packet=b'$'+payload+b'#'+f'{check:02x}'.encode()
        if self.kind=='truncated':packet=packet[:-1]
        if self.kind=='console':
            text=b'O6869';packet=b'$'+text+b'#'+f'{sum(text)%256:02x}'.encode()+packet
        self.buf.extend(packet)
    def recv(self,n):
        n=min(n,self.fragment,len(self.buf));v=bytes(self.buf[:n]);del self.buf[:n];return v

def remote(kind='valid',fragment=7):
    q=object.__new__(Remote);q.s=Wire(kind,fragment);return q
r=dict(passed=False,scope='actual Remote packet/chunk and trace capture; all socket and guest responses modeled',physical_access=False)
try:
    positives=0;negatives=0
    for size in (1,1023,1024,1025,4097):
        for frag in (1,7,4096):
            q=remote(fragment=frag);got=q.read(0x94000,size)
            assert got==bytes((0x94000+i)%251 for i in range(size))
            assert len(q.s.commands)==(size+1023)//1024;positives+=1
    q=remote('console');assert q.read(0x94000,17)==bytes((0x94000+i)%251 for i in range(17));positives+=1
    for kind in ('error','short','long','hex','checksum','truncated','stops'):
        q=remote(kind)
        try:q.read(0x94000,17)
        except (AssertionError,ValueError,EOFError,RuntimeError):negatives+=1
        else:raise AssertionError(('accepted bad packet',kind))
    for a,n in ((0,0),(0,131073),(-1,1),(0xffffffff,2)):
        q=remote()
        try:q.read(a,n)
        except AssertionError:assert q.s.commands==[];negatives+=1
        else:raise AssertionError('invalid read accepted')
    tree=ast.parse((K/'trace001.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='capture')
    code=compile(ast.fix_missing_locations(ast.Module(body=[fn],type_ignores=[])),'actual-capture','exec')
    capture_cases=[]
    for i,(physical,length,fail) in enumerate([(False,17,None),(True,17,None),(True,65537,None),(True,65537,'read1'),(True,65537,'read2'),(True,17,'enter'),(True,17,'exit')]):
        events=[];reads=[];counter=[0]
        class G:
            def ask(self,c):
                events.append(c)
                if fail==('enter' if c.endswith(':1') else 'exit'):return 'ERR'
                return 'OK'
            def read(self,a,n):
                counter[0]+=1;events.append('read'+str(counter[0]))
                if fail=='read'+str(counter[0]):raise OSError('modeled read failure')
                return bytes((a+j)%251 for j in range(n))
        case=P/f'case{i:03}';case.mkdir();env=dict(stopped=True,physical_mode=False,g=G(),PRIVATE=case,r={'reads':reads},sha=sha,save=lambda:None)
        exec(code,env);raised=False
        try:data=env['capture'](0x94000,length,'sample',physical)
        except (OSError,AssertionError):raised=True
        assert raised==bool(fail)
        assert env['physical_mode']==(fail=='exit')
        if fail in ('read1','read2'):assert events[-1]=='Qqemu.PhyMemMode:0' and not reads
        if fail=='enter':assert not reads and len(events)==1
        if not fail:assert data==bytes((0x94000+j)%251 for j in range(length))
        for row in reads:assert sha(Path(row['private_file']).read_bytes())==row['sha256']
        capture_cases.append(dict(physical=physical,length=length,injected_failure=fail,raised=raised,events=events,physical_mode_remaining=env['physical_mode'],reads=reads))
    r.update(passed=True,protocol_positive_cases=positives,protocol_negative_cases=negatives,capture_cases=capture_cases,source_sha256={n:sha((K/n).read_bytes()) for n in ['host005.py','protocol003.py','trace001.py']})
except Exception:r['failure']=traceback.format_exc()
OUT.write_bytes((json.dumps(r,indent=2)+'\n').encode());print(json.dumps({k:r[k] for k in ['passed','failure','protocol_positive_cases','protocol_negative_cases'] if k in r}))
if not r['passed']:raise SystemExit(1)
