"""Add bounded header observation and an original invalid-memory probe."""
from pathlib import Path
K=Path(__file__).resolve().parent
p=K/'fixture.c';s=p.read_text();s+='\nDWORD __cdecl probe_dib604(const void *header) {(void)header;return 0x604d1b00u;}\n';p.write_text(s,newline='\n')
p=K/'subject002.c';s=p.read_text().replace('#include "graphics002.h"','#include "graphics002.h"\n#include "dib_control.h"');s=s.replace('if(!graphics601())','if(!dibcontrol604())InterlockedIncrement(&failures);\n    if(!graphics601())');p.write_text(s,newline='\n')
p=K/'trace.c';s=p.read_text().replace('#include "calls.h"','#include "calls.h"\n#include "dib_header.h"')
s=s.replace('seen[15],resolved[15]','seen[16],resolved[16]').replace('nargs[15]={0,1,2,9,6,3,1,3,4,1,2,13,0,6,2}','nargs[16]={0,1,2,9,6,3,1,3,4,1,2,13,0,6,2,1}')
addition='''static int dibread604(void*ctx,DIBU address,void*dest,DIBU n) {
    (void)ctx;return readmem(address,dest,n);
}
static BOOL dibobserve604(DWORD id,DWORD address) {
    DIBSNAP d;DWORD i;char s[100];dib_snapshot604(dibread604,0,address,&d);
    wsprintfA(s,"DIB %08lx %08lx %08x %08x %08x %08x",id,address,d.status,d.count,d.stride,d.bytes);line(s);
    for(i=0;i<d.count;i++){wsprintfA(s," %08x",d.words[i]);line(s);}line("\\r\\n");return !failed;
}
'''
s=s.replace('static BOOL bytewrite(',addition+'static BOOL bytewrite(')
s=s.replace('if(!lstrcmpA(text,"probe601"))return 14;','if(!lstrcmpA(text,"probe601"))return 14;\n    if(!lstrcmpA(text,"probe_dib604"))return 15;')
s=s.replace('cleanup=f.api==14?0:', 'cleanup=(f.api==14||f.api==15)?0:')
anchor='if(f.api==8&&!words601(f.id,0,f.args[1],27))return FALSE;'
assert anchor in s
s=s.replace(anchor,anchor+'\n        if((f.api==4||f.api==11||f.api==15)&&!dibobserve604(f.id,f.args[f.api==4?1:f.api==11?10:0]))return FALSE;')
p.write_text(s,newline='\n')
