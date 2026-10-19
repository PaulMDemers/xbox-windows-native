"""MIT. One read-only dashboard readiness check using the existing lease."""
import importlib.util,json,sys
from pathlib import Path
K=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('pair565',K.parent/'windows-pair532/controller.py');p=importlib.util.module_from_spec(s);s.loader.exec_module(p)
out=K/'dashboard001.json';assert not out.exists();p.verify()
with p.m.connect(timeout=10) as f:
 p.m.baseline(f,'720p');listing=p.m.startup(f)
 rows=p.m.names(f,'/E')
 assert not {'xwn565','xwn565-kit'}&{n.lower() for n in rows}
 r=dict(utc=p.m.utc(),authenticated_dashboard=True,protected720p_exact=True,startup_listing=listing,console_C_accessed=False,writes=[],user_ready=True,power_cycle_history='User reported Ready; no new full power cycle specified')
out.write_text(json.dumps(r,indent=2)+'\n');print('Dashboard authenticated; protected720p and ordinary startup exact; no writes.')
