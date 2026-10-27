"""Freeze731 sources and checked bytes before E-only staging; no console access."""
from pathlib import Path
import ast,datetime,hashlib,json
K=Path(__file__).resolve().parent;P=Path('C:/xwn731/build001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
save=lambda n,v:(K/n).write_text(json.dumps(v,indent=2)+'\n')
assert not (K/'review001.json').exists()
for p in K.glob('*.py'):ast.parse(p.read_text(),filename=str(p))
body=(K/'probe.c').read_text();main=(K/'main.c').read_text()
for s in ['outb','outw','outl','Sleep(','Hal','Nt','XVideo','malloc(','0x6013d5)=','0x680630)=']:assert s not in body
assert body.count('R8(0xc03cf)=v')==1 and 'o->gr_before>3' in body
assert 'setgr4((uint8_t)o->gr_before)' in body and 'o->cr22_before==o->cr22_after' in body
assert 'words[43]' in main and 'i<43' in main and '_Static_assert(sizeof(result)==sizeof(words)' in main
assert main.index('probe731(&result)')<main.index('kernel_sample_words')<main.index('checkpoint("read_plane_control_returned"')<main.index('Sleep(15000)')
for s in ['CREATE_NEW','NtFlushBuffersFile','!memcmp(report, verify, used)','Partition1','recorded?0xff00ff','0x7315)?0xff8000','XVideoSetMode(1280,720,32,60)']:assert s in main
for n in ['main.c','layout.c','layout.h','probe.c','probe.h','Makefile']:assert sha(K/n)==sha(P/n)
# Scaffold changes are names, report length, status labels and status codes only.
old=(K.parent/'kernel-samples729/main.c').read_text().replace('729','731')
old=old.replace('Kernel-context blank/gate/sequencer sampling731','Kernel-context CR22 observations under bounded GR04 selection731').replace('words[125]','words[43]').replace('i<125','i<43').replace('write_control_armed','read_plane_control_armed').replace('write_control_returned','read_plane_control_returned').replace('(result.code==0x7318 || result.code==0x7315)','(result.code==0x7313 || result.code==0x7315)')
assert main==old
refs=read(K.parent/'setup-review730/references001.json')
for n,v in refs['downloads']['files'].items():assert sha(Path('C:/xwn730/references001')/n)==v['sha256']
envy=Path('C:/xwn730/references001/envy-nv_vga.xml').read_text();bochs=Path('C:/xwn730/references001/bochs-vgacore.cc').read_text()
assert '<reg8 offset="0x4" name="READ_PLANE_SELECT"/>' in envy and '<reg8 offset="0x22" name="MEM_LATCH"/>' in envy
assert 's.graphics_ctrl.read_map_select = value & 0x03' in bochs
save('schema001.json',{'words':43,'ranges':{'0':'status:731 completed/restored,7311 CPU refusal,7312 GR04 high-bit refusal,7313 selection mismatch,7315 cleanup mismatch,7316 selector mismatch','1..3':'entry/critical/restored EFLAGS','4..6':'actual critical CR0/3/4','7..8':'saved CRTC/graphics index','9..10':'GR04 before/after','11..12':'CR22 before/after','13..14':'CR33 before/after','15..16':'680630 before/after','17..18':'CR1b before/after','19..20':'selectors restored/cleanup bool','21..22':'GR04 data-write attempts including restore/completed selections','23..26':'requested planes','27..30':'GR04 readbacks','31..34':'first indexed CR22 reads','35..38':'direct CR22 data rereads','39..42':'reselected CR22 reads'},'unreached':'Array elements ffffffff; other unreached fields zero','green':'Selection/read/cleanup completed, NOT a particular latch model or CR22 write semantics'})
save('source-review001.json',{'passed':True,'primary_reference_manifest_sha256':sha(K.parent/'setup-review730/references001.json'),'references':refs['commit_pins']['pins'],'source_basis':'Envytools GR04 READ_PLANE_SELECT and CR22 MEM_LATCH; Bochs standard two-bit plane selector supplies hypothesis only. No CR22 write is admitted.','main_scaffold_only_reporting_changes':True,'max_GR04_writes':5,'CRTC_data_writes':0,'timing_gate_blank_unlock_writes':0,'memory_aperture_access':False,'complete_saved_byte_restored':True,'unknown_GR04_high_bits_refused':True,'limits':['Unknown NV2A CR22 write behavior unchanged.','Equal plane readouts may mean identical latch contents or lack of selector dependence; inconclusive.','Distinct readouts support selector dependence, not full-mode cause or safe CR22 writes.','Diagnostic does not preload latches from unowned legacy aperture.']})
checks=['build001.json','model001.json','layout-model001.json','link-review001.json','layout-link-review001.json','main-link-review001.json','source-review001.json']
assert all(read(K/n)['passed'] for n in checks)
checks+=['schema001.json','lineage001.json']
save('review001.json',{'passed':True,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':{n:sha(K/n) for n in checks},'model_cases':read(K/'model001.json')['case_count'],'layout_cases':read(K/'layout-model001.json')['case_count'],'max_modeled_critical_instructions':max(c['critical_instructions'] for c in read(K/'model001.json')['cases']),'hardware_proved':False})
save('sources001.json',{p.name:sha(p) for p in K.iterdir() if p.suffix in ['.c','.h','.py'] or p.name in ['Makefile','.gitattributes']})
print('PASS731 freeze, source/access/reporting review and linked byte checks')
