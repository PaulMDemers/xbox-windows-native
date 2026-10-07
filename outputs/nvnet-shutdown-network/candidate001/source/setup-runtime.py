"""Derive fresh normal controls with identical storage and bounded TCP coverage."""
from pathlib import Path
k=Path(__file__).resolve().parent;old=k.parent/'fatx-dump-map'
assert not (k/'control001').exists() and not (k/'probe.c').exists()
files=['probe.c','Build.ps1','common.py','prepare.py','preflight.py','Run.ps1','supervise.py','audit.py','configuration.py','check-oracle.py','review.py','record-closure.py','verify-evidence.py','atomic_json.py']
for name in files:
    s=(old/name).read_text().replace('fatx-dump-map','nvnet-shutdown-resident').replace('xwndm01','xwnnv104')
    if name=='probe.c':
        s=s.replace('#include <windows.h>','#include <winsock2.h>\n#include <windows.h>')
        s=s.replace('static void checkService(', '#include "network.inc"\nstatic void checkService(')
        s=s.replace('checkService("HIDSERV_START");','checkService("HIDSERV_START");networkCheck("NETWORK_START",0);')
        s=s.replace('checkService("HIDSERV_END");','checkService("HIDSERV_END");networkCheck("NETWORK_END",1);')
    if name=='Build.ps1':s=s.replace('-lkernel32 -ladvapi32 -luser32','-lkernel32 -ladvapi32 -luser32 -lws2_32')
    if name=='common.py':
        s=s.replace("['xwnfatx.sys','xboxvnt5.sys']","['xwnfatx.sys','xboxvnt5.sys','nvnetnt5.sys','ndis.sys','tcpip.sys']")
        s=s.replace("take('HIDSERV_START',[4,0,0])","take('HIDSERV_START',[4,0,0]);take('NETWORK_START',[32,131072,131072])")
        s=s.replace("take('HIDSERV_END',[4,0,0]);","take('HIDSERV_END',[4,0,0]);take('NETWORK_END',[32,131072,131072]);")
    if name=='prepare.py':
        s=s.replace("fatx_record=read(k/'fatx-review.json')[case];fatx=k/'artifacts'/fatx_record['name']", "fatx_record=read(k/'fatx-review.json')['candidate001'];fatx=k.parent/'fatx-dump-map/artifacts'/fatx_record['name']")
        s=s.replace("hid=Path(","nvnet_record=read(k/'nvnet-review.json')[case];nvnet=k/'artifacts'/nvnet_record['name'];assert sha(nvnet)==nvnet_record['sha256']\nhid=Path(")
        s=s.replace("w.flush()\ne=m.Writer", "nvnet_row=next(row for row in protected if row['volume']=='F' and row['path']=='winnt/system32/drivers/nvnetnt5.sys')\nnvnet_before=nvnet_row['sha256'];m.replace(w,nvnet_row['path'],nvnet.read_bytes());nvnet_row['sha256']=sha(nvnet)\nw.flush()\ne=m.Writer")
        s=s.replace('fatx_review_sha256=',"nvnet_review_sha256=sha(k/'nvnet-review.json'),nvnet_before_sha256=nvnet_before,nvnet_after_sha256=sha(nvnet),fatx_review_sha256=")
        s=s.replace('Both cases use identical candidate0102 HAL; rebuilt FATX control0101/candidate0103 and helper payloads differ. Video0093 unchanged.', 'Both cases use identical FATX0103, HAL0102, video0093 and helper. Only rebuilt NVNet control/candidate differs.')
    if name=='preflight.py':
        s=s.replace("fatx=read(k/'fatx-review.json')[case]", "fatx=read(k/'fatx-review.json')['candidate001']")
        s=s.replace("sha(k/'artifacts'/fatx['name'])", "sha(k.parent/'fatx-dump-map/artifacts'/fatx['name'])")
        s=s.replace("assert sha(k/'probe.c')", "assert sha(k/'nvnet-review.json')==f['nvnet_review_sha256']\nnvnet=read(k/'nvnet-review.json')[case]\nassert sha(k/'artifacts'/nvnet['name'])==f['nvnet_after_sha256']==nvnet['sha256']\nassert sha(k/'probe.c')")
        start=s.index('paths+=');end=s.index('\nr=dict',start)
        s=s[:start]+"paths+=['hal-review.json','fatx-review.json','nvnet-review.json','0104-nvnet-resident-shutdown-helper.patch','inputs.json','control-inputs.json','manifest.json','prepare-source.py','finalize-source.py','setup-runtime.py','build.py','build-control.py','review-nvnet.py','nvnet-build-candidate001.json','nvnet-build-control001.json','atomic_json.py','network.inc','network-server.py']"+s[end:]
    if name=='check-oracle.py':
        s=s.replace("'HIDSERV_START 4 0 0']","'HIDSERV_START 4 0 0','NETWORK_START 32 131072 131072']")
        s=s.replace("'HIDSERV_END 4 0 0','NORMAL_RESTART", "'HIDSERV_END 4 0 0','NETWORK_END 32 131072 131072','NORMAL_RESTART")
        s=s.replace("bad={", "bad={\n 'network-short':sample(0).replace(b'NETWORK_START 32 131072 131072',b'NETWORK_START 31 126976 126976'),\n 'network-missing':sample(0).replace(b'NETWORK_END 32 131072 131072\\r\\n',b''),")
    if name=='audit.py':
        s=s.replace("r['strict_qualification_passed']=", "network=read(out/'network-host.json');r['network_host_sha256']=sha(out/'network-host.json');r['network_passed']=network['complete'] and len(network['connections'])==2 and all(v['rounds']==32 and v['received']==131072 and v['sent']==131072 and v['peer_send_closed'] for v in network['connections'])\nr['strict_qualification_passed']=r['network_passed'] and ")
        s=s.replace('rebuilt control and FATX dump mapping; both serial mode, identical candidate0102 HAL/video0093','rebuilt NVNet control and resident shutdown candidate; both serial mode, identical FATX0103/HAL0102/video0093 with bounded bidirectional TCP')
    if name=='verify-evidence.py':
        s=s.replace("(a['workload_and_persistence_passed']", "(a['network_passed'] and a['workload_and_persistence_passed']")
        s += "\nassert sha(out/'network-host.json')==a['network_host_sha256']\n"
    (k/name).write_text(s)
for n in ['hal-review.json','fatx-review.json']:(k/n).write_bytes((old/n).read_bytes())
print('Runtime kit prepared; no guest launched')
