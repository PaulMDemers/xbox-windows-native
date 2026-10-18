"""Extend the actual-wrapper harness; all hardware and kernel effects modeled."""
import json
from pathlib import Path
K=Path(__file__).resolve().parent;P=K.parent/'marker-handoff466'
b=json.loads((K/'build001.json').read_text());s=(P/'test-wrapper.c').read_text().replace('466','468').replace('0x363634','0x383634')
def sub(a,z):
 global s
 assert s.count(a)==1,a
 s=s.replace(a,z)
sub('static int case_id,fc,fw,ff,fcl;','static int case_id,fmode,fc,fw,ff,fcl;\nstatic unsigned char frozen_marker[96];\nstatic unsigned marker_io_at_snapshot;')
s=s.replace('fallback[96]','fallback[192]')
# Preserve inherited primary failures; apply fallback failures also after marker failure.
for i in range(45,55):s=s.replace(f'case_id=={i}',f'fmode=={i}')
s=s.replace('bytes==96','bytes==192').replace('?95:96','?191:192').replace('fallback_size==96','fallback_size==192')
sub('q[1]==1 && q[2]==96','q[1]==2 && q[2]==192')
sub('q[20]==0x454e4f44 && q[21]==1 && q[22]==0x46800101 && q[23]==96','q[44]==0x454e4f44 && q[45]==2 && q[46]==0x46800101 && q[47]==192')
sub('case_id<57','case_id<85')
sub('        pmode=case_id>=55?', '        fmode=case_id>=74 && case_id<84?45+case_id-74:case_id;\n        pmode=case_id>=55?')
sub('        mode=case_id==55?2:case_id==56?4:0;stage=1;','''        static const int modes[]={2,4,3,5,6,7,8,9,10,11,12,13,14,15,16,17,18,29,30};
        mode=case_id>=74?8:case_id>=55?modes[case_id-55]:0;stage=1;''')
sub('    clear_df();\n    assert(access==','''    clear_df();
    assert(access==''')
sub('        fc++;assert(fc==1',f'''        memcpy(frozen_marker,(void*){b['wrapper_symbols']['before_marker_record']},96);
        marker_io_at_snapshot=*(uint32_t *)(frozen_marker+76);
        if(case_id==84)memset((void*){b['wrapper_symbols']['before_marker_record']},0xa7,96);
        fc++;assert(fc==1''')
sub('if(case_id>=55)assert(q[5]==(case_id==55?3u:5u) && q[9]==2);','if(case_id>=55)assert(q[5]==((uint32_t*)frozen_marker)[5] && q[9]==2);\n                assert(!memcmp(fallback+80,frozen_marker,96));')
sub('const uint32_t *marker=(void*)72848;',f'const uint32_t *marker=case_id==84?(void*)frozen_marker:(void*){b["wrapper_symbols"]["before_marker_record"]};')
sub('else if(case_id>=55)assert(marker[5]==(case_id==55?3u:5u) && marker[22]==1 && !starts);','''else if(case_id>=55) {
            assert(marker[5]>=3 && marker[5]<=7 && marker[22]==1);
            assert(marker[19]==(unsigned)port_writes && marker_io_at_snapshot==(unsigned)port_writes);
            if(case_id==84)assert(*(uint32_t*)'''+str(b['wrapper_symbols']['before_marker_record'])+'''==0xa7a7a7a7u);
        }''')
sub('    printf("PASS %u actual-wrapper cases;', '    printf("PASS %u actual-wrapper cases;')
assert not (K/'test-wrapper.c').exists();(K/'test-wrapper.c').write_text(s)
s=(P/'host001.py').read_text().replace('xwn466','xwn468').replace('57','85')
(K/'host001.py').write_text(s)
s=(K/'Build001.ps1').read_text().replace('build001.py','host001.py')
(K/'Host001.ps1').write_text(s)
# Primary format is unchanged apart from the new attempt identity.
(K/'decode.py').write_text((P/'decode.py').read_text().replace('466','468').replace('0x363634','0x383634'))
(K/'marker_decode.py').write_bytes((P/'marker_decode.py').read_bytes())
# Keep the preceding decoder separate; adapt only the versioned envelope layout.
s=(P/'refusal_decode.py').read_text().replace('466','468').replace('0x363634','0x383634')
s=s.replace('len(data)!=96','len(data)!=192').replace("struct.unpack('<24I',data)","struct.unpack('<20I',data[:80])+struct.unpack('<4I',data[176:])")
s=s.replace('(0x38363452,1,96,0x46800101)','(0x38363452,2,192,0x46800101)').replace('(0x454e4f44,1,0x46800101,96)','(0x454e4f44,2,0x46800101,192)')
s=s.replace(' return dict(record_complete=True,',' marker=decode_marker(data[80:176], reason, r[5])\n return dict(marker=marker,record_complete=True,')
s=s.replace('import struct','import struct\nfrom failure_marker import decode_marker')
(K/'refusal_decode.py').write_text(s)
