"""Prepare a fresh capacity-only installation check. No console access."""
import hashlib,json
from pathlib import Path
W=Path(__file__).resolve().parents[2];K=W/'outputs/boot720-capacity834';K.mkdir(exist_ok=False)
old=W/'outputs/stock-installer343'
source=(old/'capacity.c').read_text().replace('XVideoSetMode(640,480,32,REFRESH_DEFAULT);','')
source=source.replace('XWN-CAPACITY-333','XWN-CAPACITY-834').replace('COMPLETE 333','COMPLETE 834')
(K/'main.c').write_text(source)
(K/'report-path.h').write_bytes((old/'report-path.h').read_bytes())
(K/'Makefile').write_text('XBE_TITLE = XWN 720p installation capacity834\nGEN_XISO =\nSRCS = main.c\nNXDK_DIR = C:/nxdk\ninclude $(NXDK_DIR)/Makefile\n')
(K/'reuse001.json').write_text(json.dumps({'source_only':True,'parent_sources':{str(p.relative_to(W)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [old/'capacity.c',old/'report-path.h']},'changes':'Fresh namespace and marker; retain current mode. Read-only E/F capacity, create report only, automatic return.'},indent=2)+'\n')
