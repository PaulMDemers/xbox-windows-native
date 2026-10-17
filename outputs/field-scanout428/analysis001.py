"""Independent complete record shape/identity review and actual event deltas."""
import collections,hashlib,json,subprocess,sys
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];P=Path('E:/xwn428')
from oracle import verify_log
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def validate(text,w,h):
 verify_log(text)
 rows=[(r[0],*(int(v) for v in r[1:])) for r in (s.split() for s in text.splitlines())]
 expected=['START428']+['IDENTITY']*8
 for p in range(4):expected+=['SCANOUT']+['SCANOUT_WORD']*32+['PIXELS','PHASE','SCANOUT']+['SCANOUT_WORD']*32+['PIXELS','PHASE_DONE']
 expected+=['COMPLETE']
 if [r[0] for r in rows]!=expected:raise ValueError('record ordering')
 if rows[0][1:3]!=(w,h):raise ValueError('mode')
 ident=[0x44525758,112,w,h,w*4,32,w*h*4,1]
 if rows[1:9]!=[('IDENTITY',i,v,0) for i,v in enumerate(ident)]:raise ValueError('identity')
 for n in range(8):
  words=[r for r in rows if r[0]=='SCANOUT_WORD' and r[1]==n]
  if len(words)!=32 or [r[2] for r in words]!=list(range(32)):raise ValueError('words')
  d=[r[3] for r in words]
  if d[0:2]!=[0x53525758,112] or d[19:21]!=[0,1] or any(d[21:]):raise ValueError('scanout')
 for p in range(4):
  done=[r for r in rows if r[0]=='PHASE_DONE' and r[1]==p]
  if len(done)!=1 or not 15000<=done[0][3]<=30000:raise ValueError('duration')
  if bool(done[0][2])!=(p==2):raise ValueError('movement')
 return True
def main():
 out=K/'analysis001.json';assert not out.exists()
 decoder=W/'outputs/native-windows-physical-f/decode-legacy-events.py'
 result=dict(passed=True,decoder_sha256=sha(decoder),cases={},physical_access=False)
 for case,w,h in [('control001',1280,720),('interlace001',1920,1080)]:
  r=json.loads((K/(case+'-collection.json')).read_text());assert r['completed']
  for name,e in r['files'].items():assert sha(Path(e['path']))==e['sha256']
  text=(P/case/'after/result.log').read_text();validate(text,w,h)
  lines=text.splitlines();negative=0
  for i,line in enumerate(lines):
   if line.startswith(('IDENTITY ','SCANOUT_WORD ')):
    parts=line.split();word=int(parts[2]) if parts[0]=='SCANOUT_WORD' else None
    if word is not None and word not in (0,1,19,20,*range(21,32)):continue
    parts[-1]=str(int(parts[-1])+1);v=lines.copy();v[i]=' '.join(parts)
    try:validate('\n'.join(v),w,h)
    except ValueError:negative+=1
    else:raise AssertionError(('mutation accepted',i))
  case_r=dict(complete_log_validated=True,captures_rehashed=len(r['files']),record_mutations_rejected=negative,events={})
  all_new=[]
  for name in ('sysevent.evt','appevent.evt'):
   records={}
   for phase,raw in [('before',P/case/name),('after',P/case/'after'/name)]:
    target=raw.with_name(name+'.decoded001.json');assert not target.exists()
    subprocess.run([sys.executable,'-B',str(decoder),str(raw),'--output',str(target)],check=True,stdout=subprocess.DEVNULL,timeout=30)
    records[phase]=json.loads(target.read_text())['records']
   before,after=records['before'],records['after'];boundary=max((x['record'] for x in before),default=0)
   fingerprint=lambda x:json.dumps({k:v for k,v in x.items() if k!='offset'},sort_keys=True)
   preserved={fingerprint(x) for x in before}<={fingerprint(x) for x in after}
   dup=any(any(v>1 for v in collections.Counter(x['record'] for x in rows).values()) for rows in records.values())
   new=[x for x in after if x['record']>boundary];all_new+=new
   case_r['events'][name]=dict(boundary=boundary,prior_preserved=preserved,duplicates=dup,new=new)
  case_r['warning_errors']=[x for x in all_new if x['type'] in (1,2)]
  case_r['eventlog_shutdown_count']=sum(x['source']=='EventLog' and x['event_id']==6006 for x in all_new)
  result['cases'][case]=case_r
 result['limits']='Legacy validated record scan may include inactive ring records. Not full event coverage, full allocation audit, or signal qualification.'
 result['restore720p']=json.loads((P/'mode1080i001/restore-result.json').read_text())
 out.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:{'negative':v['record_mutations_rejected'],'shutdowns':v['eventlog_shutdown_count'],'errors':[(x['source'],x['event_id']) for x in v['warning_errors']]} for k,v in result['cases'].items()}))
if __name__=='__main__':main()
