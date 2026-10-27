"""Offline comparison of working722 capture with exact704 source predicates.
Mismatch means different states, not a causal failure or permission to replay.
"""
from pathlib import Path
import json,re,hashlib,datetime
k=Path(__file__).resolve().parent;w=k.parents[1]
out=k/'comparison001.json';assert not out.exists()
src=w/'outputs/xcal-transaction704/transaction003.c'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(src)=='6336794d817f0b801db939b2611c1832736acad598e71437f9ca87bc797a345b'
s=src.read_text();c=json.loads((k/'collection001.json').read_text())
assert json.loads((k/'audit001.json').read_text())['passed']
d=c['reports']['xwn-mode722-05.json']['data'];mm=dict(d['mmio']);cr=dict(d['crtc'])
def array(name):
 body=re.search(r'\b'+name+r'\[\]\[\d\]=\{(.*?)\};',s,re.S).group(1)
 return [[int(v.strip(),0) for v in row.split(',')] for row in re.findall(r'\{([^{}]+)\}',body)]
def compare(rows,values,masked=False):
 result=[]
 for row in rows:
  address=row[0];mask=row[1] if masked else 0xffffffff;target=row[-1];actual=values[address]
  result.append({'register':hex(address),'mask':hex(mask),'expected':hex(target),'actual':hex(actual),'matches':(actual&mask)==target})
 return result
r={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'script_sha256':sha(Path(__file__)),'source_sha256':sha(src),'capture_sha256':c['reports']['xwn-mode722-05.json']['sha256'],'scope':__doc__}
r['common_pramdac']=compare(array('setup'),mm)
r['common_crtc_before_geometry']=compare(array('cs'),cr)
final=[row[:] for row in array('cs')]
for row in final:
 if row[0]==0x19:row[1]=0x30
r['common_crtc_after_geometry']=compare(final,cr)
r['timing']=compare(array('timing'),mm)
r['geometry_crtc_masked']=compare(array('cv'),cr,True)
r['sequencer_during_blanked_transaction']={'expected':[3,0x21,15,0,6],'kernel_visible':d['sequencer'],'limitation':'SEQ1 differs by output blanking bit; visible mode is not a blanked transaction.'}
r['graphics']={'expected':[0,0,0,0,0,0x40,5,15,255],'kernel_visible':d['graphics'],'matches':d['graphics']==[0,0,0,0,0,0x40,5,15,255]}
r['not_compared']=['Encoder table, attribute controller and unrecorded controls','704 per-stage post-write state;722 sampled kernel-created complete modes','Preserved-bit comparisons needing same704 entry state']
r['summary']={group:{'equal':sum(row['matches'] for row in r[group]),'total':len(r[group])} for group in ['common_pramdac','common_crtc_before_geometry','common_crtc_after_geometry','timing','geometry_crtc_masked']}
out.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r['summary']))
