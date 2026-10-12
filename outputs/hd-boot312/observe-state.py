"""One read-only owned HMP observation; no guest pause or write."""
import datetime,hashlib,json,sys
from pathlib import Path
k=Path(__file__).resolve().parent;run=Path('D:/xwn312/runs/nt5-hd312-candidate001')
out=k/'candidate001/loader-observation.json';assert not out.exists()
assert (run/'instance.json').exists() and not (run/'cleanup.json').exists()
sys.path.insert(0,str(k.parent/'native-windows-prebuild'));from monitor_capture import acquire_monitor_lock,command
review=json.loads((k.parent/'hd-loader311/binary-review001.json').read_text())['rows']['candidate001']['symbols']
r=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),guest_pause=False,guest_writes=False,physical_access=False,queries={},symbols=review,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),limits='Do not interpret historical loader data unless actual resident code and CPU location support it.')
try:
 lock=acquire_monitor_lock(5044);r['registers']=command(5044,'info registers')
 for name,n in [('XwnHdState311',9),('XwnHdTry720',16)]:
  a=review[name]['va'];r['queries'][name]=command(5044,('xp /%d%s '%(n,'wx' if name=='XwnHdState311' else 'bx'))+hex(a))
finally:out.write_text(json.dumps(r,indent=2)+'\n')
import re
print('\n'.join(x for x in r['registers'].splitlines() if 'EIP=' in x or 'EFL=' in x))
for n,v in r['queries'].items():print(n,'\n'.join(re.findall(r'^0[0-9a-f]+:.*',v,re.M)))
