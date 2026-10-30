"""Source-only reuse of capacity834; read-only PCI inventory, no mode writes."""
from pathlib import Path
import hashlib,json
K=Path(__file__).resolve().parent; W=K.parents[1]
old=W/'outputs/boot720-capacity834'
sha=lambda b:hashlib.sha256(b).hexdigest()
pins={n:sha((old/n).read_bytes()) for n in ['main.c','report-path.h','Makefile','physical.py']}
main=(old/'main.c').read_text()
start=main.index('static int query('); end=main.index('int main(void)')
main=main[:start]+main[end:]
start=main.index('    debugPrint('); end=main.index('    const char end[]')
main=main[:start]+'''    /* Serialized kernel PCI API, FALSE means read. No BAR sizing writes. */
    const ULONG buses[]={0,0,1};
    const ULONG slots[]={0,30,0};
    for(unsigned device=0;device<3;device++){
        for(unsigned offset=0;offset<64;offset+=4){
            ULONG value=0xffffffff;
            HalReadWritePCISpace(buses[device],slots[device],offset,&value,4,FALSE);
            int n=snprintf(text+used,sizeof(text)-used,"PCI %lu %lu %02x %08lx\\r\\n",
                buses[device],slots[device],offset,value);
            if(n<0||(size_t)n>=sizeof(text)-used){Sleep(1000);XReboot();return 1;}
            used+=(size_t)n;
        }
    }
''' +main[end:]
main=main.replace('char text[1024]="XWN-CAPACITY-834','char text[4096]="XWN-PCI-840').replace('COMPLETE 834','COMPLETE 840').replace('Capacity report','PCI inventory')
main=main[main.index('#include'):]
main='/* PCI inventory840: reads only. Creates one owned report, returns to dashboard. */\n'+main
(K/'main.c').write_text(main)
h=(old/'report-path.h').read_text().replace('XWNECap','XWNEPci').replace('capacity.txt','pci.txt')
(K/'report-path.h').write_text(h)
(K/'Makefile').write_text((old/'Makefile').read_text().replace('720p installation capacity834','PCI inventory840'))
(K/'.gitattributes').write_text('* -text\n')
p=(old/'physical.py').read_text().replace('Capacity834','PCI840').replace('C:/xwn834','C:/xwn840').replace('XWNECap83400001','XWNEPci84000001').replace("'attempt':834","'attempt':840").replace('Read-only E/F capacity for fixed720p Windows installation','Read-only PCI configuration for Windows display discovery').replace('capacity.txt','pci.txt').replace('capacity001.txt','pci001.txt').replace('len(data)<1024','len(data)<4096').replace('XWN-CAPACITY-834','XWN-PCI-840').replace('COMPLETE 834','COMPLETE 840')
start=p.index('   v=lines[1].split()');end=p.index("   r['dashboard_authenticated']",start)
p=p[:start]+'''   assert len(lines)==50
   r['pci']=[]
   for line in lines[1:-1]:
    v=line.split();assert len(v)==5 and v[0]=='PCI'
    r['pci'].append({'bus':int(v[1]),'slot':int(v[2]),'offset':int(v[3],16),'value':int(v[4],16)})
''' +p[end:]
(K/'physical.py').write_text(p)
(K/'reuse001.json').write_text(json.dumps({'source_only':True,'parent':'outputs/boot720-capacity834','pins':pins,'changes':'Fresh840 namespace; replace capacity query with48 serialized PCI DWORD reads. No modeset, no BAR writes, automatic dashboard return.'},indent=2)+'\n')
