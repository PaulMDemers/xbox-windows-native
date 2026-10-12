"""Execute the actual PRAMDAC functions with modeled containing-device/logging."""
import hashlib,json,re,subprocess
from pathlib import Path

def run(control,candidate,out):
    assert not out.exists();out.mkdir()
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    report={'passed':False,'scope':'Actual aligned32-bit register functions; modeled NV2A container and log calls; no scanout or migration runtime claim','cases':[]}
    for label,files in [('control',control),('candidate',candidate)]:
        d=out/label;d.mkdir()
        header=files['hw/xbox/nv2a/nv2a_int.h']
        fields=header.split('    struct {\n        uint32_t core_clock_coeff;',1)[1].split('    } pramdac;',1)[0]
        stub='#include <stdint.h>\n#include <stdio.h>\n#include <stdlib.h>\n#include "regs.h"\ntypedef uint64_t hwaddr;\n#define NV2A_CRYSTAL_FREQ 16666666\n#define nv2a_reg_log_read(a,b,c,d) ((void)(b),(void)(c),(void)(d))\n#define nv2a_reg_log_write(a,b,c,d) ((void)(b),(void)(c),(void)(d))\ntypedef struct { struct { uint32_t core_clock_coeff;'+fields+' } pramdac; } NV2AState;\n'
        (d/'nv2a_int.h').write_text(stub);(d/'regs.h').write_text(files['hw/xbox/nv2a/nv2a_regs.h'])
        (d/'pramdac.c').write_text(files['hw/xbox/nv2a/pramdac.c'])
        test=r'''
#include "pramdac.c"
static unsigned checks;
#define CHECK(x) do { ++checks; if (!(x)) { fprintf(stderr,"line %d\n",__LINE__); abort(); } } while(0)
int main(void) {
    NV2AState d={0};
    const uint32_t offsets[]={0x804,0x80c,0x824,0x800,0x808,0x810,0x818,0x820,0x828,0x838};
    uint32_t values[10]={0};
    for(unsigned j=0;j<10;++j) CHECK(pramdac_read(&d,offsets[j],4)==0);
    for(unsigned n=0;n<4096;++n) {
        for(unsigned i=0;i<10;++i) {
            uint32_t v=(n*0x9e3779b9u)^(i*0x1234567u);
            pramdac_write(&d,offsets[i],v,4);
            values[i]=(CANDIDATE || i>=3)?v:0;
            for(unsigned j=0;j<10;++j) CHECK(pramdac_read(&d,offsets[j],4)==values[j]);
        }
    }
    pramdac_write(&d,0x804,1124,4);
    pramdac_write(&d,0x80c,1083,4);
    pramdac_write(&d,0x824,2199,4);
    CHECK(pramdac_read(&d,0x804,4)==(CANDIDATE?1124:0));
    CHECK(pramdac_read(&d,0x80c,4)==(CANDIDATE?1083:0));
    CHECK(pramdac_read(&d,0x824,4)==(CANDIDATE?2199:0));
    pramdac_write(&d,0x8f0,0xffffffffu,4);CHECK(pramdac_read(&d,0x8f0,4)==0);
    printf("checks %u\n",checks);return 0;
}
'''
        (d/'host.c').write_text(test)
        command=['gcc','-std=c11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-DCANDIDATE='+str(int(label=='candidate')),str(d/'host.c'),'-o',str(d/'host')]
        p=subprocess.run(command,capture_output=True);(d/'compile.log').write_bytes(p.stdout+p.stderr);assert p.returncode==0,p.stderr.decode()
        p=subprocess.run([str(d/'host')],capture_output=True,timeout=60);(d/'result.txt').write_bytes(p.stdout);(d/'stderr.txt').write_bytes(p.stderr);assert p.returncode==0 and not p.stderr,p.stderr.decode()
        report['cases'].append({'case':label,'checks':int(p.stdout.split()[1]),'command':command})
    # Exact schema/reset review; not a serialization-runtime simulation.
    v=candidate['hw/xbox/nv2a/nv2a.c']
    for field in ['fp_vtotal','fp_vsync_start','fp_htotal']:
        assert v.count(f'd->pramdac.{field} = 0;')==2
        assert v.count(f'VMSTATE_UINT32_V(pramdac.{field}, NV2AState, 4),')==1
    assert '.name = "nv2a",\n    .version_id = 4,\n    .minimum_version_id = 1,' in v
    report.update(passed=True,files={str(p):sha(p) for p in out.rglob('*') if p.is_file()})
    return report
