"""Derive E16KiB read-only scanner; reports must live on the separate F volume."""
from pathlib import Path
import json,hashlib
K=Path(__file__).resolve().parent;old=K.parent/'native-windows-fatx-preflight';t=(old/'main.c').read_text()
t=t.replace('Read-only Partition6 snapshot. All output files are beside this XBE on E:', 'Read-only Partition1 snapshot. All output files are beside this XBE on F:')
t=t.replace('Partition6','Partition1')
t=t.replace('part.StartingOffset.QuadPart!=15633072ULL*512 || (length!=472764096ULL*512 && length!=129434820096ULL)', 'part.StartingOffset.QuadPart!=5633024ULL*512 || length!=10000048ULL*512')
t=t.replace('spc!=128','spc!=32')
t=t.replace('(unsigned long long)(c-1)*65536,65536,buf', '(unsigned long long)(c-1)*16384,16384,buf').replace('off<65536;off+=64','off<16384;off+=64')
t=t.replace('count=(472764096ULL*512)/65536;', 'count=(ULONG)(length/16384);')
t=t.replace('fat=malloc((size_t)(data_offset-4096));', 'count=(ULONG)((length-data_offset)/16384+1);\n fat=malloc((size_t)(data_offset-4096));')
t=t.replace('Reading F; reports beside this app on E.', 'Reading E; reports beside this app on F.')
t=t.replace('XWN-FAT-PREFLIGHT-001','XWN-E-FAT-PREFLIGHT-341')
# Correct end-of-directory state must persist across every cluster in one chain.
t=t.replace('ULONG head=queue[q],c=head,steps=0;', 'ULONG head=queue[q],c=head,steps=0;int ended=0;')
t=t.replace('if(e[0]==0 || e[0]==255)break;', 'if(e[0]==0 || e[0]==255)ended=1;\n    if(ended)continue;')
(K/'main.c').write_text(t,newline='\n')
make=(K.parent/'stock-drive333/Makefile').read_text().replace('Capacity333','E Allocation341').replace('capacity333','allocation341').replace('capacity.c','main.c').replace('capacity.map','allocation.map');(K/'Makefile').write_text(make,newline='\n')
t=(K.parent/'stock-drive333/build-capacity002.py').read_text().replace('xwn333/capacity-build002','xwn341/build001').replace('capacity-build002.json','build001.json').replace("['capacity002.c','Makefile']","['main.c','Makefile']").replace("out/('capacity.c' if name=='capacity002.c' else name)",'out/name').replace("['capacity002.c','Makefile','build-capacity002.py']","['main.c','Makefile','build.py']").replace("out/'capacity333.iso'","out/'allocation341.iso'").replace("out/'capacity.map'","out/'allocation.map'")
(K/'build.py').write_text(t,newline='\n')
(K/'analyze.py').write_bytes((K.parent/'stock-runtime335/analyze-allocation002.py').read_bytes())
(K/'DESIGN.md').write_text('Read only native Partition1 with exact measured standard E geometry: start5633024 sectors,length10000048 sectors,16KiB clusters. FAT read/allocation is bounded by this geometry and actual data area. Reports are written to D: beside this XBE, which MUST launch from a new owned F app folder. This keeps allocation/readback output off the E volume being scanned. No C access, raw write handle, repair, format or ATA command. Snapshot parser is byte-identical to335 corrected standard-E analyzer. Existing original F scanner remains unchanged. Live deployment is permitted only after a private stock fixture demonstrates expected allocation output and orderly dashboard return.\n')
(K/'source-review.json').write_text(json.dumps(dict(parent_sha256=hashlib.sha256((old/'main.c').read_bytes()).hexdigest(),source_sha256=hashlib.sha256((K/'main.c').read_bytes()).hexdigest(),raw_access='GENERIC_READ|SYNCHRONIZE',partition='Partition1',report_volume_required='F',physical_access=False),indent=2)+'\n')
