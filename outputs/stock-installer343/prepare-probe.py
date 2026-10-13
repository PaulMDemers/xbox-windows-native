"""Preserve the rejected fixed-path bundle; derive a unique-path probe with unchanged queries."""
import json,shutil
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1]
prior=K/'prior001';assert not prior.exists();prior.mkdir()
for q in ['assemble.py','USAGE.md']:
    shutil.copyfile(K/q,prior/q)
shutil.copyfile(W/'tools/stock-e-profile.json',prior/'stock-e-profile.json')
(W/'tools/stock-e-profile.json').unlink()
(K/'review-failure001.json').write_text(json.dumps(dict(passed=False,physical_access=False,reason='Old333 binary uses fixed native report path; proposed random folder could not receive a fresh report. No guest launched. bundle001 retained and rejected.',assembly='assembly001.json'),indent=2)+'\n')
s=(W/'outputs/stock-drive333/capacity002.c').read_text()
s=s.replace('#include <string.h>','#include <string.h>\n#include "report-path.h"')
needle='    RtlInitAnsiString(&reportName,"\\\\Device\\\\Harddisk0\\\\Partition1\\\\Applications\\\\XWNCapacity333\\\\capacity.txt");'
assert s.count(needle)==1
s=s.replace(needle,'    char reportPath[256];\n    if(!xwn343_report_path(XeImageFileName->Buffer,XeImageFileName->Length,reportPath,sizeof(reportPath))){debugPrint("Launch namespace refused\\n");Sleep(3000);XReboot();return 1;}\n    RtlInitAnsiString(&reportName,reportPath);')
(K/'capacity.c').write_text(s)
shutil.copyfile(W/'outputs/stock-drive333/Makefile',K/'Makefile')
b=(W/'outputs/stock-drive333/build-capacity002.py').read_text().replace('E:/xwn333/capacity-build002','E:/xwn343/capacity-build001').replace("K/'capacity-build002.json'","K/'capacity-build001.json'")
b=b.replace("['capacity002.c','Makefile']","['capacity.c','Makefile','report-path.h']").replace("['capacity002.c','Makefile','build-capacity002.py']","['capacity.c','Makefile','report-path.h','build-capacity.py']")
(K/'build-capacity.py').write_text(b)
