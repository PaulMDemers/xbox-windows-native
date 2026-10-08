"""Create explicit mapped-page observation protocol; preserve prior strict failure."""
from pathlib import Path
w=Path(__file__).resolve().parents[2];old=w/'outputs/video-ram-crash2';k=w/'outputs/video-ram-crash3'
assert (old/'failure-verification.json').exists();k.mkdir(exist_ok=False);(k/'artifacts').mkdir()
names=['common.py','prepare.py','preflight.py','Run.ps1','Invoke-Lba.ps1','supervise.py','trace.py','audit-crash.py','configuration.py','cold-map.py','record-closure.py','verify.py','verify-payload.py','verify-render.py','verify-ram.py','atomic_json.py','discover_kernel.py','modules.json','layouts.json','kernel-review.json','fatx-review.json','nvnet-review.json','atapi-review.json','address-review.json','video-sites.json','DESIGN.md','NEXT.md','test-pin.py']
for n in names:(k/n).write_text((old/n).read_text().replace('video-ram-crash2','video-ram-crash3'),encoding='utf-8')
for n in ['build-review.json','Build.ps1','review.py','probe.c','trigger.c']:(k/n).write_bytes((old/n).read_bytes())
for n in ['probe.exe','trigger.sys']:(k/'artifacts'/n).write_bytes((old/'artifacts'/n).read_bytes())
p=k/'trace.py';s=p.read_text();s=s.replace('from discover_kernel import discover','from discover_kernel import discover\nfrom residency import inspect_display')
start=s.index("            sec=next(v for v in pes['xwnown.dll'].sections")
end=s.index("            r['ram_before']=ram_state()",start)
s=s[:start]+"""            text=command(4594,'info registers');controls={n:int(re.search(n+r'=([0-9a-fA-F]+)',text).group(1),16) for n in ['CR0','CR3','CR4']}
            assert controls['CR0']&0x80000000 and not controls['CR4']&0x20
            raw=out/'artifacts/crash-before.ram';assert not raw.exists()
            reply=command(4594,'pmemsave 0 67108864 '+json.dumps(raw.resolve().as_posix()));assert raw.stat().st_size==67108864
            r['before_memory']=dict(path=str(raw.resolve()),sha256=sha(raw),control_registers=controls,monitor_reply=reply)
            r['ram_residency_before']=inspect_display(raw.read_bytes(),controls['CR3'],rambase,pes['xwnown.dll'],ram_symbols)
            r['ram_live_function_pins']=[pin(rambase+ram_symbols[label]) for label in ['XwnUpload','DrvAssertMode']]
"""+s[end:]
s=s.replace("r['private_memory']=str(raw.resolve());r['private_memory_sha256']=sha(raw)","r['private_memory']=str(raw.resolve());r['private_memory_sha256']=sha(raw)\n            r['ram_residency_after']=inspect_display(raw.read_bytes(),r['control_registers']['CR3'],rambase,pes['xwnown.dll'],ram_symbols)")
s=s.replace("for dependency in [k/'discover_kernel.py',", "for dependency in [k/'discover_kernel.py',k/'residency.py',k.parent/'video-shared-trace2/walk.py',")
p.write_text(s,encoding='utf-8')
p=k/'prepare.py';s=p.read_text().replace("k.parent/'video-ram-crash/failure-verification.json'","k.parent/'video-ram-crash2/failure-verification.json'");p.write_text(s,encoding='utf-8')
p=k/'verify-ram.py';s=p.read_text().replace('from walk import read_virtual','from walk import read_virtual\nfrom residency import inspect_display')
start=s.index("code=bytearray(");end=s.index("dis=t['kernel_discovery']",start)
s=s[:start]+"""before_memory=t['before_memory'];bp=Path(before_memory['path']);assert sha(bp)==before_memory['sha256']
before_res=inspect_display(bp.read_bytes(),before_memory['control_registers']['CR3'],base,pe,symbols)
after_res=inspect_display(ram,cr3,base,pe,symbols)
assert before_res==t['ram_residency_before'] and after_res==t['ram_residency_after']
assert before_res==after_res
pins=[t['runtime_pins'][i] for i in t['ram_live_function_pins']]
assert [int(v['rva'],16) for v in pins]==[symbols[n] for n in ['XwnUpload','DrvAssertMode']]
assert all(v['module']=='xwnown.dll' for v in pins)
"""+s[end:]
s=s.replace('display_text_bytes=len(code)','display_text_bytes=sec.Misc_VirtualSize,mapped_display_text_bytes=after_res[\'mapped_bytes\'],unmapped_display_text_bytes=after_res[\'unmapped_bytes\']')
s=s.replace('full_resident_display_text_before_after=True','whole_display_text_residency_qualified=False,mapped_display_text_before_after_exact=True')
s=s.replace('One debugger-observed desktop-to-crash handoff;', 'One debugger-observed desktop-to-crash handoff; unmapped display code explicitly excluded from residency claim;')
p.write_text(s,encoding='utf-8');print('Third kit created; not prepared/launched')
