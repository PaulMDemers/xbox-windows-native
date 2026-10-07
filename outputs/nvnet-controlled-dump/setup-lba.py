"""Fresh crash004 to observe the dump writer and actual ATA command sequence."""
from pathlib import Path
k=Path(__file__).resolve().parent;out=k.parent/'dump-lba-trace';assert not out.exists();out.mkdir();(out/'artifacts').mkdir()
names=['trigger.c','probe.c','Build.ps1','review.py','build-review.json','hal-review.json','fatx-review.json','nvnet-review.json','layouts.json','kernel-review.json','atomic_json.py','modules.json','modules-review.py','common.py','configuration.py','cold-map.py','prepare.py','Run.ps1','preflight.py','supervise.py','record-closure.py','audit-crash.py','trace.py','verify.py']
for n in names:
    s=(k/n).read_text()
    if n.endswith(('.py','.ps1')):s=s.replace('nvnet-controlled-dump','dump-lba-trace').replace('crash003','crash004')
    if n=='Run.ps1':s=s.replace('../native-windows-nt5-kernel/Invoke-Diagnostic.ps1','Invoke-Lba.ps1')
    if n=='preflight.py':s=s.replace("'setup-origin.py'","'setup-origin.py','Invoke-Lba.ps1'")
    if n=='trace.py':
        s=s.replace("precall=K+0x2b141", "precall=K+0x2b141;writecall=K+0x22100;writeret=K+0x22103")
        s=s.replace('[bc,dump,initret,precall]+list(stages)', '[bc,dump,initret,precall,writecall,writeret]+list(stages)')
        s=s.replace("row['kind']='pre_dump_call';row['context']=dump_context()", "row['kind']='pre_dump_call';row['context']=dump_context();remove(a)")
        s=s.replace("row['kind']='dump_entry';assert", "row['kind']='dump_entry';remove(a);assert")
        s=s.replace("row['kind']='dump_stack_initialized';assert", "row['kind']='dump_stack_initialized';remove(a);assert")
        s=s.replace("elif a==ret:","elif a==writecall:\n            row['kind']='first_write_call';offset_ptr=u32(regs['ESP']);mdl=u32(regs['ESP']+4);raw=g.read(mdl,28)\n            row['volume_offset']=struct.unpack('<Q',g.read(offset_ptr,8))[0];row['mdl_raw']=raw.hex();mapped,start,count,offset=struct.unpack_from('<4I',raw,12);row['byte_count']=count;row['source_prefix']=g.read(mapped,64).hex();row['writer']=hex(u32(regs['EBP']-0x18));row['writer_pin']=callback_pin(u32(regs['EBP']-0x18));remove(a)\n        elif a==writeret:\n            row['kind']='first_write_return';row['status']=hex(regs['EAX']);remove(a)\n        elif a==ret:")
    (out/n).write_text(s)
s=(k.parent/'native-windows-nt5-kernel/Invoke-Diagnostic.ps1').read_text();s=s.replace("'-trace','enable=ide_sector_write'", "'-trace','enable=ide_ioport_write','-trace','enable=ide_bus_exec_cmd','-trace','enable=ide_sector_write'")
(out/'Invoke-Lba.ps1').write_text(s);(out/'setup-origin.py').write_bytes(Path(__file__).read_bytes())
for n in ['probe.exe','trigger.sys']:(out/'artifacts'/n).write_bytes((k/'artifacts'/n).read_bytes())
print('New bounded crash004 scripts; unchanged drivers/settings, no launch')
