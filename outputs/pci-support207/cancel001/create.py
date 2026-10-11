"""Fresh native cancellation trial; no telemetry or physical changes."""
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'halboot001'
names='xwnrsc.c resources.h install.c probe.c restart.h power-test.h remove-test.h resource-log.h xwnrsc.inf Build-001.ps1 review-build.py prepare-emulator002.py run-emulator002.py audit-emulator002.py review-pnp002.py Continue-001.ps1 e_allocation.py test-start.c resource-tests.h vectors.h start-vector.h'.split()
for name in names:
    p=k/name;assert not p.exists()
    s=(old/name).read_text().replace('halboot001','cancel001').replace('xwnpcihal1','xwnpcican1').replace('4784','4794').replace('4786','4796').replace("variant+'002'","variant+'001'")
    if name=='xwnrsc.inf':s=s.replace('0.1.0.225','0.1.0.226')
    if name=='Continue-001.ps1':
        s=s.replace("@('control','candidate')","@('candidate')")
        for base in ('prepare-emulator','run-emulator','audit-emulator','review-pnp'):s=s.replace(base+'.py',base+'002.py')
        s=s.replace('!$r.lifecycle_completed','!$r.lifecycle_completed -or !$r.cancel_remove_qualified')
    if name=='probe.c':s=s.replace('#include "remove-test.h"','#include "cancel-test.h"\n#include "remove-test.h"')
    if name=='remove-test.h':
        needle='    clear_bytes(name,sizeof(name));'
        assert s.count(needle)==1
        s=s.replace(needle,'    if(!exercise_cancel(instance))return FALSE;\n'+needle)
    if name=='review-pnp002.py':
        needle="r['pnp_restart_api_succeeded']="
        s=s.replace(needle,"r['cancel_remove_qualified']=all(x in log.splitlines() for x in ('cancel_remove_result=23','cancel_remove_veto=5','CANCEL_REMOVE_RECOVERED')) and any(x['stage']==5 and x['profile']==3 for x in records)\n"+needle)
        s=s.replace('terminal takeover, ordinary cold-boot','terminal takeover, STOP/CANCEL_STOP, ordinary cold-boot')
    p.write_text(s,newline='\n')
(k/'.gitattributes').write_text('* -text whitespace=cr-at-eol\n')
