"""Cross-check runtime pairs, resident callers, trace MSRs and full alias inventory."""
import hashlib,json,struct,sys
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];out=k/'trace002'
sys.path.insert(0,str(ws/'work/python-packages'));import pefile
from walk import read_virtual
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
t=read(out/'trace.json');m=read(k/'mapping.json');s=read(k/'alias-summary.json');v=read(k/'verification.json');replay=read(k/'map-replay.json');maps=read(k/'map-sites.json')
assert v['passed'] and s['passed'] and replay['passed'] and t['status']=='desktop_snapshot_captured' and not t.get('error')
assert not t['armed_breakpoints_remaining'] and t['guest_resumed'] and t['mapping_stops']<=2048
assert replay['trace_sha256']==sha(out/'trace.json') and replay['source_sha256']==sha(k/'replay-map.py')
assert s['verification_sha256']==sha(k/'verification.json')
assert sha(out/'artifacts/video-trace.bin')==m['trace_sha256']==read(out/'audit.json')['video_trace_sha256']
ram=Path(t['private_memory']);assert sha(ram)==s['snapshot_sha256'];data=ram.read_bytes();cr3=t['control_registers']['CR3']
early=Path(t['early_snapshot']['path']);assert sha(early)==replay['early_snapshot_sha256'];edata=early.read_bytes();ecr3=t['early_snapshot']['control_registers']['CR3']
def bytes_at(raw,root,address,n):return read_virtual(raw,root,address,n)
def relocated(p,rva,n,base):
 code=bytearray(p.get_data(rva,n));assert len(code)==n
 for block in p.DIRECTORY_ENTRY_BASERELOC:
  for e in block.entries:
   if e.type==3 and rva<=e.rva<rva+n:
    off=e.rva-rva;assert off+4<=n;struct.pack_into('<I',code,off,(struct.unpack_from('<I',code,off)[0]+base-p.OPTIONAL_HEADER.ImageBase)&0xffffffff)
 return bytes(code)
modules={r['name']:r for r in t['module_list']};pins=[]
for name in ['videoprt.sys','xboxvnt5.sys']:
 info=maps['modules'][name];assert sha(Path(info['path']))==info['sha256'];p=pefile.PE(info['path']);base=modules[name]['base']
 assert modules[name]['size']==((p.OPTIONAL_HEADER.SizeOfImage+4095)&~4095)
 nt=struct.unpack('<I',bytes_at(data,cr3,base+60,4))[0];assert bytes_at(data,cr3,base,2)==b'MZ' and struct.unpack('<I',bytes_at(data,cr3,base+nt+8,4))[0]==info['timestamp']
 if name=='xboxvnt5.sys':
  sec=next(v for v in p.sections if v.Name.rstrip(b'\0')==b'.text');rva=sec.VirtualAddress;n=sec.Misc_VirtualSize
 else:
  caller=t['mapping_calls'][1]['return_address'];rva=caller-base;n=16
  assert t['mapping_calls'][1]['caller_bytes']==t['mapping_returns'][-1]['caller_bytes']
 code=relocated(p,rva,n,base);assert bytes_at(data,cr3,base+rva,n)==code
 if name=='videoprt.sys':assert code.hex()==t['mapping_calls'][1]['caller_bytes']
 pins.append(dict(name=name,base=base,rva=rva,bytes=n,source_sha256=info['sha256'],resident_sha256=hashlib.sha256(code).hexdigest()))
assert [(r['api'],r['physical'],r['length'],r['cache_type']) for r in t['mapping_calls']]==[('MmMapIoSpace',0x03c00000,0x400000,0),('MmMapVideoDisplay',0xf3c00000,0x400000,0),('MmMapIoSpace',0xf3c00000,0x400000,0)]
rets={r['call_id']:r for r in t['mapping_returns']};assert len(rets)==len(t['mapping_calls'])==3
for call in t['mapping_calls']:
 ret=rets[call['id']];assert ret['thread']==call['thread'] and ret['esp']==call['esp']+20 and ret['address']==call['return_address'] and ret['caller_bytes']==call['caller_bytes']
 assert bytes_at(data,cr3,ret['address'],16).hex()==ret['caller_bytes']
 raw,root=(edata,ecr3) if call['id']==0 else (data,cr3)
 g=call['kernel_cache_globals'];K=t['kernel_base'];assert struct.unpack('<I',bytes_at(raw,root,K+0x73cfc,4))[0]==g['KeFeatureBits']
 assert bytes_at(raw,root,K+0x73d50,1).hex()==g['MiWriteCombiningPtes']
 assert struct.unpack('<I',bytes_at(raw,root,K+0x72eb0,4))[0]==g['ValidKernelPte']
assert rets[0]['value']==v['bootvid']['globals']['_FrameBufferStart']['value'] and rets[1]['value']==rets[2]['value']
assert len(m['mapping_observations'])==1;obs=m['mapping_observations'][0];assert obs['virtual']==rets[1]['value'] and obs['physical']==0xf3c00000 and obs['length']==0x400000
assert obs['msrs']['0x277']==0x0007010600070106 and obs['msrs']['0x2ff']==0x800 and not obs['cr0']&(1<<30)
for directory in s['directories']:
 assert len(directory['ranges'])==2
 for region in directory['ranges']:
  assert region['length']==0x400000 and region['flags'][2:5]==[True,True,False]
  expected=rets[0]['value'] if region['physical']==0x03c00000 else rets[1]['value'];assert region['virtual']==expected
assert not replay['early_current_root']['ranges']
dest=k/'contract-verification.json';assert not dest.exists();dest.write_text(json.dumps(dict(passed=True,ordinary_qualified=False,physical_access=False,runtime_pairs=3,mapping_stops=t['mapping_stops'],resident_pins=pins,kernel_mapping_function_resident_sha256=replay['resident_function_sha256'],bootvid_wc_ready=0,desktop_wc_ready=1,baseline_mapping_cache_type=0,pat_index=3,pat_entry_type='UC',mapping_time_msr_pat=obs['msrs']['0x277'],desktop_alias_roots=s['directory_count'],early_current_root_has_target_aliases=False,evidence={p:sha(k/p) for p in ['trace002/trace.json','trace002/audit.json','trace002/closure.json','alias-summary.json','verification.json','map-replay.json','mapping.json','map-sites.json']},source_sha256=sha(Path(__file__)),limits='No real guest WC request/transition. MSRs sampled at desktop mapping; PTEs in later full snapshot. Early aliases cover current root only. Isolated replay has modeled helpers. Diagnostic PASS is not ordinary speed or physical qualification.'),indent=2)+'\n')
print('Contract verified: 3 paired calls, resident0094/videoprt, early/late cache globals, full desktop aliases')
