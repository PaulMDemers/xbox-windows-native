"""Derive new host fixtures and unchanged scene review; no network."""
import hashlib,json
from pathlib import Path
K=Path(__file__).resolve().parent;parent=K.parent/'d3d-scene497'
s=(parent/'controller-host001.py').read_text().replace('497','501')
s=s.replace("ROOT.mkdir()","ROOT.mkdir(parents=True)")
s=s.replace("'XWNBoot501a'","'XWNBoot499a'").replace('XWNBoot501a\\','XWNBoot499a\\')
s=s.replace("state[m.HOOK]=m.hook();", "state[m.HOOK]=m.hook();state[m.REMOTE+'/owner.json']=b'modeled owner';")
s=s.replace("{'directory':'/' in rest}","{'directory':'/' in rest,'bytes':len(state[n])}")
s=s.replace(" def send(s):", "  def retrbinary(self,cmd,receive,chunk):\n   assert chunk==1024\n   data=state[cmd[5:]]\n   for at in range(0,len(data),chunk):receive(data[at:at+chunk])\n def send(s):")
s=s.replace("'build002.json'","'launcher-input.json'")
assert not (K/'controller-host001.py').exists();(K/'controller-host001.py').write_bytes(s.encode())
s=(K.parent/'entry-control500/supervisor-host002.py').read_text().replace('500','501').replace('supervisor-host002','supervisor-host001').replace('supervise002.py','supervise.py')
(K/'supervisor-host001.py').write_bytes(s.encode())
s=(parent/'review-physical001.py').read_text().replace('497','501')
(K/'review-physical001.py').write_bytes(s.encode())
# Capture entry status separately; never use it as scene/restart authority.
p=K/'physical-closeout001.py';s=p.read_text().replace('combined_scene_passed=samplepass,','entry_observation=c.get(\'entry\'),combined_scene_passed=samplepass,');p.write_bytes(s.encode())
r=dict(inputs={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [parent/'controller-host001.py',parent/'review-physical001.py',K.parent/'entry-control500/supervisor-host002.py']},network=False)
(K/'test-derivation001.json').write_bytes((json.dumps(r,indent=2)+'\n').encode())
