import copy,hashlib,json,re,struct
from pathlib import Path
K=Path(__file__).resolve().parent;out=K/'emu001';r=json.loads((out/'trace.json').read_text());p=json.loads((K/'preparation002.json').read_text());s=p['symbols'];xbe=Path('E:/xwn374/build001/default.xbe').read_bytes()
blobs={}
for item in r['reads']:
    data=Path(item['private_file']).read_bytes();assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256'];assert item['label'] not in blobs;blobs[item['label']]=data
assert blobs['loaded-original-wrapper']==xbe[0x1100:0x3000]
assert blobs['loaded-original-payload']==blobs['allocated-payload']==blobs['relocated-cromwell']==xbe[0x3000:0x3000+288316]
rows=r['checkpoints'];alias=rows[1]['variables']['phys_bootloaderram'];target=alias+s['newloc']-s['blentry']
expected=bytearray(blobs['loader-source']);struct.pack_into('<I',expected,s['ptr_newloc']-s['blentry'],target)
assert all(blobs[n]==expected for n in ['high-loader','low-loader','low-physical','high-physical'])
pde=struct.unpack('<I',blobs['low-loader-pde'])[0];pte=struct.unpack('<I',blobs['low-loader-pte'])[0]
assert pde&1 and not pde&128 and pte&1 and (pte&0xfffff000)==rows[1]['low_physical']
assert rows[1]['high_physical']==alias

def qualify(t):
    assert t['passed'] and not t.get('error') and not t.get('cleanup_error')
    assert not t['remaining_breakpoints'] and not t['physical_mode_remaining'] and t['physical_mode_restored']
    assert not t['guest_memory_or_register_writes'] and not t['physical_access'] and not t['ordinary_qualified']
    assert t['stopped_before_first_cromwell_instruction'] and not t['windows_started']
    c=t['checkpoints'];assert len(c)==6
    expected_ips=[0x11100,0x111f2,alias,alias+12,target,0x2600000]
    expected_names=['original_entry','before_original_indirect_jump','relocated_entry_paging_on','immediately_after_paging_disabled','far_jump_new_cs','original_cromwell_first_instruction']
    for i,row in enumerate(c):
        assert row['label']==expected_names[i] and row['registers']['EIP']==expected_ips[i]
        assert bool(row['registers']['CR0']&0x80000000)==(i<3)
        if i>=3:assert not row['registers']['EFL']&0x200
        if i>=4:assert row['registers']['CR3']==0
    assert re.search(r'CS =0008 00000000 ffffffff',c[4]['raw_registers'])
    base=alias+s['bootloader_gdt']-s['blentry']
    assert re.search(r'GDT=\s*'+f'{base:08x}'+r' 00008000',c[4]['raw_registers'])
    armed=set()
    for b in t['breakpoints']:
        assert b['reply']=='OK'
        command=b['command'];point=int(command.split(',')[1],16)
        if command.startswith('Z1,'):assert point not in armed;armed.add(point)
        else:assert command.startswith('z1,') and point in armed;armed.remove(point)
    assert not armed and len(t['breakpoints'])==12
qualify(r);negatives=0
for idx in range(6):
    for field,value in [('EIP',0),('CR0',r['checkpoints'][idx]['registers']['CR0']^0x80000000)]:
        t=copy.deepcopy(r);t['checkpoints'][idx]['registers'][field]=value
        try:qualify(t)
        except AssertionError:negatives+=1
        else:raise AssertionError('Mutated checkpoint accepted')
for key,value in [('passed',False),('remaining_breakpoints',[0x11100]),('physical_mode_remaining',True),('physical_mode_restored',False),('guest_memory_or_register_writes',True),('physical_access',True),('ordinary_qualified',True),('windows_started',True)]:
    t=copy.deepcopy(r);t[key]=value
    try:qualify(t)
    except AssertionError:negatives+=1
    else:raise AssertionError('Mutated qualification accepted')
result=dict(scoped_original_handoff_trace_passed=True,actual_checkpoints=6,private_captures_rehashed=len(blobs),actual_report_mutations_rejected=negatives,actual_low_physical=rows[1]['low_physical'],actual_loader_physical=alias,actual_cromwell_entry=0x2600000,physical_failure_reproduced=False,ordinary_qualified=False,all_breakpoints_removed=True,physical_mode_restored=True,kernel_header_and_IDT_handlers_captured_not_full_symbol_match=True)
with (out/'trace-review.json').open('x',encoding='utf-8') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result))
