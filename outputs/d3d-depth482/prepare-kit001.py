"""One fresh bounded482 comparison; closed481 stays failed and immutable."""
import re
from pathlib import Path
K=Path(__file__).resolve().parent;W=K.parents[1];old=K.parent/'d3d-depth481'
for name in ('build001.py','host001.py','test-wrapper.c','decode.py','refusal_decode.py','failure_marker.py','controller-host001.py','binary-review001.py','package001.py','physical.py','runner.c','review001.py','module-read001.py','closeout001.py','cold-review001.py','archive-inputs001.py','actual-controls001.py'):
 s=(old/name).read_text(encoding='utf-8').replace('0x48100101','0x48200101').replace("cookie='48100101'","cookie='48200101'")
 s=re.sub(r'(?<![0-9])481(?![0-9])','482',s)
 s=s.replace('0x31383458','0x32383458').replace('0x31383452','0x32383452')
 p=K/name;assert not p.exists();p.write_text(s,encoding='utf-8',newline='\n')
with (W/'.gitattributes').open('a',encoding='utf-8',newline='\n') as f:f.write('\n/outputs/d3d-depth482/** -text whitespace=cr-at-eol\n/outputs/d3d-depth482/review001.py -text whitespace=cr-at-eol,-blank-at-eof\n')
(K/'DESIGN.md').write_text('One new comparison after481 no-receipt launch. Exact480 sample/oracle and481 protocol; only owned namespace/cookie change. No old case rerun or new boot-fix claim. Same two90-second sample deadlines,480-second observer and20-second single SITE request. Remove hook first; preserve partial evidence. Stop further physical retries if no Windows receipts. All depth/format/attachment/module/hive/event gates retained. No baseline/driver/SDK/consoleC change.\n',encoding='utf-8')
