"""Strict semantic check of recorded six-case native telemetry; no shutdown waiver."""
import argparse,json,re
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--case',required=True);args=ap.parse_args()
k=Path(__file__).resolve().parent;out=k/args.case;dest=out/'telemetry.json';assert not dest.exists()
a=json.loads((out/'audit.json').read_text());rows=[]
for name,log in a['logs'].items():
    if not name.startswith(('probe-','cycle-')):continue
    sections=re.split(r'(?m)^case=',log.replace('\r\n','\n'))
    head=sections[0];valid='XWN_PCI207_BEGIN version=1\n' in head and 'XWN_PCI207_END\n' in log.replace('\r\n','\n')
    fields=dict(re.findall(r'(?m)^(\w+)=(\d+)$',head))
    valid &= fields.get('cm_result')=='0' and fields.get('devnode_problem')=='0' and bool(int(fields.get('devnode_status','0'))&8)
    cases=[]
    for section in sections[1:]:
        lines=section.splitlines();index=int(lines[0]);d={key:int(value) for key,value in re.findall(r'(?m)^(\w+)=(\d+)$','\n'.join(lines[1:]))}
        if index in (3,4):ok=all(d.get(key)==value for key,value in dict(transport_ok=0,error=87,bytes=0).items())
        else:ok=all(d.get(key)==value for key,value in dict(transport_ok=1,error=0,bytes=24,version=1,result=0,data=50 if index in (1,2) else 6,status=16).items()) and 1<=d.get('attempts',0)<=3 and 1<=d.get('polls',0)<=30000
        cases.append(dict(index=index,passed=ok,values=d))
    valid &= [v['index'] for v in cases]==list(range(6)) and all(v['passed'] for v in cases)
    rows.append(dict(log=name,passed=bool(valid),cases=cases))
target=[v for v in a['pci_targets'] if 'DEV_01B4' in v['instance']]
binding=len(target)==1 and target[0]['values'].get('Service',{}).get('decoded')=='xwnsmb' and target[0]['driver_key'].get('InfSection',{}).get('decoded')=='Telemetry' and target[0]['driver_key'].get('MatchingDeviceId',{}).get('decoded')=='pci\\ven_10de&dev_01b4&subsys_00000000&rev_b1'
r=dict(scope=__doc__,logs=rows,binding_valid=bool(binding),telemetry_passed=bool(rows and all(v['passed'] for v in rows)),normal_shutdown_qualified=False,persistence_qualified=False,hardware_ready=False)
dest.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({key:value for key,value in r.items() if key!='logs'}))
