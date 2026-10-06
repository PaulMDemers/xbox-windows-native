"""Summarize actual captured installer transitions without filling undecoded commands."""
import collections,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;case=sys.argv[1];assert case in ['001','002','003'];out=k/case
d=json.loads((out/'trace.json').read_text());assert d.get('status')
events=d['events'];installers={}
for event in events:
    for role in ['owner','target']:
        p=event.get(role,{})
        if p.get('image','').lower()!='rundll32.exe':continue
        key=p['eprocess']+'/'+str(p['pid'])
        item=installers.setdefault(key,dict(eprocess=p['eprocess'],pid=p['pid'],observations=[],decoded_commands=[]))
        item['observations'].append(dict(index=event['index'],utc=event['utc'],tick_count=event.get('tick_count'),function=event['function'],role=role,command_line=p.get('command_line'),decode_error=p.get('decode_error'),caller_owner=event.get('owner'),arguments=event['arguments']))
        if p.get('command_line') and p['command_line'] not in item['decoded_commands']:item['decoded_commands'].append(p['command_line'])
csrss=[e for e in events if e['function']=='NtTerminateProcess_AfterReference' and e.get('owner',{}).get('image','').lower()=='csrss.exe']
hard=[e for e in events if 'HardError' in e['function']]
r=dict(scope=__doc__,physical_access=False,ordinary_boot_qualified=False,status=d['status'],event_counts=dict(collections.Counter(e['function'] for e in events)),installers=list(installers.values()),csrss_terminations=csrss,hard_errors=hard,
       limits='A resume request does not prove execution; an entry into NtCreateProcess does not prove success. Commands remain unknown at observations where decode failed. CSRSS termination is an observed ordering landmark, not a complete shutdown state machine. Kernel hard-error capture does not cover every user-mode popup route. Breakpoints change scheduling.')
if (out/'audit.json').exists():
    a=json.loads((out/'audit.json').read_text());r['cold_result']={key:a[key] for key in ['completed','dashboard_return','diagnostic_checks_passed','normal_shutdown_count','popups','unexpected_errors']}
(out/'lifecycle.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps({key:r[key] for key in ['status','event_counts','cold_result'] if key in r},indent=2))
for p in r['installers']:print('installer',p['pid'],p['decoded_commands'])
