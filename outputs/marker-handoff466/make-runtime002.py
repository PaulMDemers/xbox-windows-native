"""Preserve failed001 and prepare fresh002 with offline staging; no FTP data channel."""
from pathlib import Path
K=Path(__file__).resolve().parent
assert not (K/'Run002.ps1').exists()
s=(K/'collect.py').read_text();a=s.index('with ColdIO(child) as io:');z=s.index('r=dict(',a)
s=s[:a]+s[z:];s=s.replace('candidate_exact=True,primary=decoded,','candidate_never_staged=True,')
(K/'audit-failed001.py').write_text(s)
s=(K/'Run.ps1').read_text().replace('emu001','emu002').replace('preparation001','preparation002').replace('Invoke.ps1','Invoke002.ps1')
(K/'Run002.ps1').write_text(s)
s=(K/'Invoke.ps1').read_text().replace('preparation001','preparation002')
(K/'Invoke002.ps1').write_text(s)
s=(K/'trace.py').read_text().replace('emu001','emu002').replace('trace001','trace002')
a=s.index("    r['stage']={'directory'");z=s.index("    mon('stop')",a)
s=s[:a]+'''    prepared=json.loads((K/'preparation002.json').read_text());assert prepared['status']=='prepared'
    r['stage']={'directory':'E:/Applications/XWNBoot466a','offline_prepared':True,'readback_sha256':prepared['change']['sha256']}
    assert r['stage']['readback_sha256']==sha(xbe);save()
'''+s[z:]
(K/'trace002.py').write_text(s)
s=(K/'collect.py').read_text().replace('emu001','emu002').replace('cold001','cold002').replace('preparation001','preparation002')
(K/'collect002.py').write_text(s)
s=(K/'preflight001.py').read_text().replace("K/'emu001'","K/'emu002'")
(K/'preflight002.py').write_text(s)
(K/'emu002').mkdir()
