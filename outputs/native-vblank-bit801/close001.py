"""Close collected801 and pin the next source operation; no console access."""
from pathlib import Path
import json,hashlib,datetime
K=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda n:json.loads((K/n).read_text())
assert read('audit001.json')['passed'] and read('photo-review002.json')['passed']
assert read('collection001.json')['completed'] and read('dashboard002.json')['authenticated']
assert read('audit001.json')['native_CR09_blank_before_after_restored']==[96,64,96]
assert not (K/'closed001.json').exists()
r={'closed':True,'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
'pins':{n:sha(K/n) for n in ['audit001.json','photo002.json','photo-review002.json','collection001.json','dashboard002.json','launch001.json','sources001.json']},
'single_launch':True,'single_collection':True,'hook':False,'console':'Authenticated dashboard after standing photo/manual-reset workflow',
'owned_host_processes':[],'owned_running_vms':[],'normal_windows_shutdown':False,
'native_CR09_before_after_restored':[96,64,96],'displayed_masks_clear':8,'omitted_masks_aggregate_only':20,
'no_relaunch_recollection_or_runtime_parent':True,
'preserved_failures':['qualification-failure001.json','qualification-failure002.json','qualification-failure003.json','photo001.json','photo-debug001.json'],
'limits':['Native result photo-only; nine persisted reports end at handoff_armed','No full mode switch, Windows1.6 desktop, acceleration or normal shutdown proof']}
(K/'closed001.json').write_text(json.dumps(r,indent=2)+'\n')
source=K.parent/'xcal-transaction704/gpu_legacy.c';lines=source.read_text().splitlines()
needle='NvSetCrtc(pbRegs, 7, b | (((gpu->yres - 1) >> 5) & 0x08));'
line=next(i+1 for i,s in enumerate(lines) if s.strip()==needle)
assert lines[line-2].strip()=='b = NvGetCrtc(pbRegs, 7) & 0xf7;'
old=K.parent/'crtc-vblank-bit800/collection001.json';reports=json.loads(old.read_text())['reports']
v=next(x['data']['kernel_sample_words'] for x in reports.values() if x['data']['phase']=='crtc_vblank_bit_control_returned')
assert v[649:652]==[54,54,54] and v[640:646]==[96,64,1,64,96,0]
plan={'preparation_only':True,'physical_access':False,'source':source.relative_to(K.parents[1]).as_posix(),'source_sha256':sha(source),'source_line':line,'operation':needle,
'next_attempt':'Fresh kernel802 CR07 vertical-blank-start bit3, then separately qualified native803',
'baseline_evidence':'Closed800 saved preparation/control report, source-only analysis;801 photo proves CR09 change/recovery but does not expose CR07 raw',
'baseline_evidence_sha256':sha(old),'kernel800_CR07_neighbor_values':v[649:652],
'expected_before_after_restored':[54,(54&0xf7)|(((480-1)>>5)&8),54],
'neighbor_admission':{'CR06':12,'CR09':64,'CR10':233,'CR12':223,'CR15':207,'CR16':140,'CR18':255,'CR25':16},
'required':['New actual baseline admission before CR07 write','Reverse own CR07 saved value before CR09 recovery','Fresh mismatch/drop/coupling/cleanup fault coverage and all prior masks','Source/binary/layout/clock/controller qualification before staging','Unique E namespace, exact readback, one bounded SITE, collect/audit automatic return','Native803 must independently remeasure code/result/stack bounds;801 payload has only72 bytes margin'],
'new_build_stage_launch':False,'closed_runtime_reuse':False}
assert plan['expected_before_after_restored']==[54,62,54]
(K/'next-control-plan001.json').write_text(json.dumps(plan,indent=2)+'\n')
note="""# Test801 CLOSED PASS: native CR09 vertical-blank-start bit5

Photo decoded60 ->40 ->60; eight displayed recovery masks clear and final801
passed. Twenty omitted masks remain aggregate-only. Independent review checks
416bits at five offsets/three thresholds plus352 adjacent-row sample checks.
One accepted launch and one collection of nine preparation reports through
handoff_armed; audit001PASS exact source/build/stage and allocation boundaries.
Native result is photo-only. Dashboard002 authenticated after standing photo/
manual-reset workflow. No hook, owned host process or running VM. No normal
Windows shutdown, full-mode switching or Windows1.6 desktop claim.

Preserve qualification-failure001..003 and initial photo001/photo-debug001
component-size rejection. Decoder002 widened isolated-cell geometry bounds;
classification thresholds and independent pixel checks stayed unchanged.

Next source operation: CR07 vertical-blank-start bit3, pinned704 line102.
Fresh kernel802 should admit36, calculate3E for yres480 and restore its saved36
before CR09. Eight neighbors include CR09=40. Source-only derivation from closed
800; independently qualify before stage/launch. Native803 then needs fresh size/
layout qualification:801 raw22968/padded23040 has only72bytes margin.
See next-control-plan001.json. No802 build/stage/launch yet. All earlier runtime
attempts CLOSED; never relaunch/recollect/runtime-parent.
"""
(K/'NEXT.md').write_bytes(note.encode())
for name in ['CONTINUATION.md','STATUS.md']:
 p=K.parent/'engineering-notes'/name;p.write_bytes(note.encode()+b'\n'+p.read_bytes())
print(json.dumps({'closed':True,'CR09':[96,64,96],'next_CR07':[54,62,54]}))
