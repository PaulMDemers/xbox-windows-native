"""Independent HID short-item layout inspection and authored Python syntax check."""
import ast,hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent
source=(k/'xid_hid.c').read_text();body=source.split('xwn_report_descriptor[] = {',1)[1].split('};',1)[0]
data=bytes(int(v,16) for v in re.findall(r'0x([0-9a-fA-F]+)',body))
at=0;globals_={};local={};inputs=[];depth=0
while at<len(data):
    prefix=data[at];at+=1;size=(0,1,2,4)[prefix&3];kind=(prefix>>2)&3;tag=prefix>>4
    assert at+size<=len(data) and prefix!=0xfe
    value=int.from_bytes(data[at:at+size],'little');signed=int.from_bytes(data[at:at+size],'little',signed=True);at+=size
    if kind==1:
        if tag==1:globals_[tag]=signed
        elif tag==2:globals_[tag]=signed if globals_.get(1,0)<0 else value
        else:globals_[tag]=value
    elif kind==2:
        if tag==0:local.setdefault('usages',[]).append(value)
        else:local[tag]=value
    elif kind==0:
        if tag==10:
            assert depth==0 and globals_[0]==1 and local['usages']==[5] and value==1;depth+=1
        elif tag==12:depth-=1;assert depth==0
        elif tag==8:
            assert depth==1
            inputs.append(dict(page=globals_[0],bits=globals_[7],count=globals_[9],report_id=globals_[8],logical_min=globals_[1],logical_max=globals_[2],flags=value,local=local.copy()))
        else:raise AssertionError(('unexpected main item',tag))
        local={}
assert depth==0 and at==len(data) and len(inputs)==4
buttons,pad,sticks,triggers=inputs
assert (buttons['page'],buttons['bits'],buttons['count'],buttons['flags'],buttons['local'])==(9,1,14,2,{1:1,2:14})
assert (pad['bits'],pad['count'],pad['flags'])==(1,2,3)
assert (sticks['page'],sticks['bits'],sticks['count'],sticks['logical_min'],sticks['logical_max'],sticks['local'])==(1,16,4,-32768,32767,{'usages':[0x30,0x31,0x33,0x34]})
assert (triggers['page'],triggers['bits'],triggers['count'],triggers['logical_min'],triggers['logical_max'],triggers['local'])==(1,8,2,0,255,{'usages':[0x32,0x35]})
assert all(i['report_id']==1 for i in inputs)
assert sum(i['bits']*i['count'] for i in inputs)==96
syntax={}
for p in k.glob('*.py'):ast.parse(p.read_text());syntax[p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(passed=True,descriptor_sha256=hashlib.sha256(data).hexdigest(),descriptor_length=len(data),input_report_bytes=13,inputs=inputs,python_syntax=syntax,scope='Static descriptor semantics and Python syntax only; no compiled driver or NT5 runtime claim.')
(k/'source-check.json').write_text(json.dumps(r,indent=2)+'\n');print('PASS independent HID descriptor inspection and Python syntax')
