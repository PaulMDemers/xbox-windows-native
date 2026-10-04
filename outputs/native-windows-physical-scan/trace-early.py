"""Observe exact early entry in an owned xemu snapshot; never target the Xbox."""
import argparse, ftplib, json, pathlib, socket, struct, sys, time
kit=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(kit.parents[1]/'work/python-packages'))
sys.path.insert(0,str(kit.parent/'native-windows-prebuild'))
import pefile
from monitor_capture import command, acquire_monitor_lock

class Remote:
    def __init__(self,port):
        self.s=socket.create_connection(('127.0.0.1',port),timeout=20)
        self.s.settimeout(20)
    def recv(self):
        while True:
            c=self.s.recv(1)
            if not c:raise EOFError('Debugger disconnected')
            if c!=b'$':continue
            b=bytearray()
            while True:
                c=self.s.recv(1)
                if not c:raise EOFError('Incomplete debugger packet')
                if c==b'#':break
                b+=c
            checksum=self.s.recv(2)
            assert int(checksum,16)==sum(b)%256
            self.s.sendall(b'+')
            if b.startswith(b'O') and b!=b'OK':continue
            return b.decode()
    def send(self,s):
        b=s.encode();self.s.sendall(b'$'+b+b'#'+f'{sum(b)%256:02x}'.encode())
    def ask(self,s):self.send(s);return self.recv()
    def bp(self,addr,on=True):assert self.ask(f'{"Z" if on else "z"}0,{addr:x},1')=='OK'
    def regs(self):
        raw=bytes.fromhex(self.ask('g'))
        values=struct.unpack_from('<10I',raw)
        return {k:values[i] for i,k in enumerate(['eax','ecx','edx','ebx','esp','ebp','esi','edi','eip','eflags'])}
    def read(self,addr,size):return bytes.fromhex(self.ask(f'm{addr:x},{size:x}'))

p=argparse.ArgumentParser()
for flag in ['gdb','monitor','ftp']:p.add_argument('--'+flag,type=int,required=True)
p.add_argument('--reference',type=pathlib.Path,required=True)
p.add_argument('--output',type=pathlib.Path,required=True)
a=p.parse_args();reference=json.loads(a.reference.read_text())
assert reference['status']=='kernel_ram_scan_verified'
e=reference['entry_record']['words']
pe=pefile.PE(str(kit/'package/loader/halxboxnt5.dll'))
exports={x.name.decode():e[8]+x.address for x in pe.DIRECTORY_ENTRY_EXPORT.symbols if x.name}
points={e[5]:'KernelEntry',exports['HalInitializeProcessor']:'HalInitializeProcessor',exports['HalInitSystem']:'HalInitSystem'}
boundary=json.loads((kit/'hal-boundary-audit.json').read_text())
for symbol in ['@HalpXboxExamineMBR@16','@HalpXboxIoReadPartitionTable@16','@HalpXboxIoSetPartitionInformation@16','@HalpXboxIoWritePartitionTable@20']:
    points[e[8]+int(boundary['symbols_rva'][symbol],16)]='FORBIDDEN_'+symbol
points[e[8]+int(boundary['symbols_rva']['_HalpXwnBaseReady'],16)]='BaseHalReady'
for symbol,name in [('_HalpCalibrateStallExecution@0','CalibrationEntry'),('OnlyOnePersonCanWriteHalCode','FirstRtcInterrupt'),('ComputeStall','SecondRtcInterrupt'),('_HalpXwnTimerReady','TimerReady')]:
    points[e[8]+int(boundary['symbols_rva'][symbol],16)]=name
for symbol,name in [('_HalpInitializeClock@0','ClockInitialize'),('_HalStopProfileInterrupt@4','ProfileStop'),('_HalpXwnClockReady','ClockReady'),('_HalpInitPhase0','XboxPhase0'),('_HalpXboxInitPartIo','PartitionRegistration'),('_HalpXwnHooksReady','HooksReady'),('_HalInitializeBios@8','BiosInitialize'),('_HalpXwnBiosReady','BiosReady')]:
    points[e[8]+int(boundary['symbols_rva'][symbol],16)]=name
for instruction,name in zip(boundary['inlined_pit_writes'],['PitModeWrite','PitLowWrite','PitHighWrite']):
    points[e[8]+int(instruction['rva'],16)]=name
pub=json.loads((kit.parent/'native-windows-nt5-kernel/kernel-publics.json').read_text())['symbols']
points[e[6]+pub['_ExInitSystem@0']['rva']]='ExecutiveInit'
points[e[6]+pub['_CmGetSystemControlValues@8']['rva']]='RegistryControls'
points[e[6]+pub['_MmInitSystem@12']['rva']]='MemoryManagerEntry'
points[e[6]+0x157d78]='MachineDependentEntry'
points[e[6]+0x157f27]='LowClearBegin'
points[e[6]+0x157f3e]='LowMappingsCleared'
points[e[80]]='RamScanCompleted'
points[e[6]+pub['_MmInitializeMemoryLimits@12']['rva']]='MemoryLimits'
points[e[6]+pub['_MiTriageSystem@4']['rva']]='TriageSystem'
points[e[88]]='MapCheckpoint'
points[e[80]+5]='FORBIDDEN_PostScanSelection'
kpe=pefile.PE(str(kit/'package/WINNT/system32/ntoskrnl.exe'))
points[e[6]+next(s.address for s in kpe.DIRECTORY_ENTRY_EXPORT.symbols if s.name==b'KeSetTimeIncrement')]='KernelSetTimeIncrement'
for m in reference['modules']:
    if m['name'].lower().endswith('.sys'):points[int(m['entry'],16)]='FORBIDDEN_DriverEntry_'+m['name']
result={'scope':'Native kernel entry observed using emulator breakpoints; all disk writes isolated in snapshot.','events':[],'forbidden_breakpoints':{hex(k):v for k,v in points.items() if v.startswith('FORBIDDEN')},'passed':False}
lock=acquire_monitor_lock(a.monitor);g=None
def save():a.output.write_text(json.dumps(result,indent=2)+'\n')
def memory_descriptors():
    head=e[4]+8;node=struct.unpack('<I',g.read(head,4))[0];previous=head;items=[]
    while node!=head:
        assert len(items)<128
        words=struct.unpack('<5I',g.read(node,20));assert words[1]==previous
        items.append(list(words[2:]));previous=node;node=words[0]
    assert struct.unpack('<I',g.read(head+4,4))[0]==previous
    return items

try:
    command(a.monitor,'stop')
    g=Remote(a.gdb);g.ask('qSupported');g.ask('?')
    # Low loader callback addresses can overlap dashboard code before launch.
    # Arm only native kernel entry until the dashboard has handed off.
    g.bp(e[5])
    g.send('c')
    with ftplib.FTP() as ftp:
        ftp.connect('127.0.0.1',a.ftp,timeout=8);ftp.login('xbox','xbox')
        result['launch_response']=ftp.sendcmd(r'SITE EXEC E:\Applications\XWNLoader\default.xbe')
    for expected in ['KernelEntry','HalInitializeProcessor','ProcessorReturned','HalInitSystem','BaseHalReady','CalibrationEntry','FirstRtcInterrupt','SecondRtcInterrupt','CalibrationReturned','TimerReady','ClockInitialize','KernelSetTimeIncrement','PitModeWrite','PitLowWrite','PitHighWrite','ClockReturned','ProfileStop','ProfileReturned','ClockReady','XboxPhase0','PartitionRegistration','HooksReady','BiosInitialize','BiosAllocateFirst','BiosAllocatedFirst','BiosAllocateSecond','BiosAllocatedSecond','BiosReturned','BiosReady','LoaderCheckpoint','HalPhase0Return','RegistryControls','RegistryControlsReturned','ExecutiveInit','ExecutiveReturned','MemoryManagerEntry','MemoryLimits','MemoryLimitsReturned','TriageSystem','TriageReturned','MachineDependentEntry','LowClearBegin','LowMappingsCleared','RamScanCompleted','MapCheckpoint']:
        stop=g.recv();r=g.regs();name=points.get(r['eip'],'unexpected')
        event={'name':name,'stop':stop,'registers':{k:hex(v) for k,v in r.items()},'stack':list(struct.unpack('<4I',g.read(r['esp'],16)))}
        result['events'].append(event);save()
        assert name==expected,event
        g.bp(r['eip'],False)
        if name=='KernelEntry':
            for addr,label in points.items():
                if addr!=e[5] and label not in ('MemoryLimits','TriageSystem'):g.bp(addr)
        if name=='HalInitializeProcessor':
            assert event['stack'][1:3]==[0,e[4]]
            assert e[6]<=event['stack'][0]<e[6]+e[7]
            points[event['stack'][0]]='ProcessorReturned';g.bp(event['stack'][0])
        if name=='HalInitSystem':
            assert event['stack'][1:3]==[0,e[4]]
            points[event['stack'][0]]='HalPhase0Return';g.bp(event['stack'][0])
        if name=='CalibrationEntry':
            points[event['stack'][0]]='CalibrationReturned';g.bp(event['stack'][0])
        if name=='FirstRtcInterrupt':
            event['rtc_interrupt_count_before_increment']=struct.unpack('<I',g.read(r['ebp']-12,4))[0]
            assert event['rtc_interrupt_count_before_increment']==0
        if name=='SecondRtcInterrupt':
            event['rtc_interrupt_count']=struct.unpack('<I',g.read(r['ebp']-12,4))[0]
            assert event['rtc_interrupt_count']==2
        if name=='KernelSetTimeIncrement':assert event['stack'][1:3]==[150000,10000]
        if name in ['PitModeWrite','PitLowWrite','PitHighWrite']:
            assert r['eax']&255=={'PitModeWrite':0x34,'PitLowWrite':16875&255,'PitHighWrite':16875>>8}[name]
        if name=='ProfileStop':assert event['stack'][1]==0
        if name in ['ClockInitialize','ProfileStop']:
            returned={'ClockInitialize':'ClockReturned','ProfileStop':'ProfileReturned'}[name]
            points[event['stack'][0]]=returned;g.bp(event['stack'][0])
        if name=='PartitionRegistration':
            dispatch=e[6]+next(s.address for s in kpe.DIRECTORY_ENTRY_EXPORT.symbols if s.name==b'HalDispatchTable')
            originals=[struct.unpack('<I',g.read(dispatch+off,4))[0] for off in [0x14,0x1c,0x20,0x24]]
            event['original_partition_handlers']=[hex(x) for x in originals]
            assert all(e[6]<=x<e[6]+e[7] for x in originals)
        if name=='HooksReady':
            installed=[struct.unpack('<I',g.read(dispatch+off,4))[0] for off in [0x14,0x1c,0x20,0x24]]
            symbols=['@HalpXboxExamineMBR@16','@HalpXboxIoReadPartitionTable@16','@HalpXboxIoSetPartitionInformation@16','@HalpXboxIoWritePartitionTable@20']
            assert installed==[e[8]+int(boundary['symbols_rva'][s],16) for s in symbols]
            saved=[struct.unpack('<I',g.read(e[8]+int(v,16),4))[0] for v in boundary['saved_handler_globals_rva'].values()]
            assert saved==originals
            event['installed_partition_handlers']=[hex(x) for x in installed]
            event['saved_originals_equal_pre_registration']=True
        if name=='BiosInitialize':
            before_descriptors=memory_descriptors();event['memory_descriptors_before']=before_descriptors
            assert event['stack'][1:3]==[0,e[4]]
            points[event['stack'][0]]='BiosReturned';g.bp(event['stack'][0])
            allocator=e[8]+int(boundary['symbols_rva']['_HalpAllocPhysicalMemory@20'],16)
            points[allocator]='BiosAllocateFirst';g.bp(allocator)
        if name in ['BiosAllocateFirst','BiosAllocateSecond']:
            args=list(struct.unpack('<6I',g.read(r['esp'],24)))
            assert args[1:]==[e[4],0x100000,0,1,0],args
            event['allocation_arguments']=args[1:]
            returned='BiosAllocatedFirst' if name=='BiosAllocateFirst' else 'BiosAllocatedSecond'
            points[args[0]]=returned;g.bp(args[0])
        if name in ['BiosAllocatedFirst','BiosAllocatedSecond']:
            assert r['edx']==0 and r['eax']==(0x1000 if name=='BiosAllocatedFirst' else 0x2000)
            event['allocated_physical_address']=hex(r['eax'])
            if name=='BiosAllocatedFirst':
                points[allocator]='BiosAllocateSecond';g.bp(allocator)
        if name=='BiosReturned':
            after_descriptors=memory_descriptors();event['memory_descriptors_after']=after_descriptors
            expected_descriptors=[list(d) for d in before_descriptors]
            assert expected_descriptors[1]==[5,1,7]
            expected_descriptors[1:2]=[[26,1,1],[26,2,1],[5,3,5]]
            assert after_descriptors==expected_descriptors
            event['exact_descriptor_transition_verified']=True
        if name=='BiosReady':
            points[e[10]]='LoaderCheckpoint';g.bp(e[10])
        if name=='LoaderCheckpoint':assert event['stack'][1:3]==[80,e[4]]
        if name=='HalPhase0Return':assert r['eax']&255==1
        if name=='RegistryControls':
            event['init_data_before']=g.read(e[6]+0x164f54,0x5c).hex()
            points[event['stack'][0]]='RegistryControlsReturned';g.bp(event['stack'][0])
        if name=='RegistryControlsReturned':
            data=g.read(e[6]+0x164f54,0x5c);event['init_data_after']=data.hex()
            assert struct.unpack_from('<I',data,0)[0]==0xffffffff
            assert data[0x14:0x1e]==bytes.fromhex('30003400300039000000')
            assert data[0x34:0x3e]==bytes.fromhex('30003400300039000000')
            assert struct.unpack_from('<2I',data,0x2c)==(10,1)
            assert struct.unpack_from('<2I',data,0x4c)==(10,1)
            assert struct.unpack_from('<2I',data,0x54)==(2,7)
            event['registry_control_data_verified']=True
        if name=='ExecutiveInit':
            points[event['stack'][0]]='ExecutiveReturned';g.bp(event['stack'][0])
        if name=='ExecutiveReturned':assert r['eax']&255==1
        if name=='MemoryManagerEntry':
            assert event['stack'][1:3]==[0,e[4]]
            # The executive also calls MemoryLimits before HAL initialization.
            # Watch the MM-prefix invocation only after MmInitSystem starts.
            for addr,label in points.items():
                if label in ('MemoryLimits','TriageSystem'):g.bp(addr)
            assert g.read(r['eip'],9)==bytes.fromhex('558bec81ecf0000000')
            event['original_mm_entry_unchanged']=True
            event['memory_descriptors_before_mm']=memory_descriptors()
        if name=='MemoryLimits':
            args=event['stack'];assert args[1]==e[4]
            limits=args[3]
            points[args[0]]='MemoryLimitsReturned';g.bp(args[0])
        if name=='MemoryLimitsReturned':
            count,total=struct.unpack('<2I',g.read(limits,8));assert 0<count<20
            event['memory_limits']={'count':count,'pages':total,'runs':[list(struct.unpack('<2I',g.read(limits+8+i*8,8))) for i in range(count)]}
            expected_total=sum(d[2] for d in after_descriptors if d[0]<24 and d[0] not in (3,6,22,23))
            assert total==expected_total
            assert sum(d[1] for d in event['memory_limits']['runs'])==total
            event['descriptor_filter_total_verified']=True
        if name=='TriageSystem':
            assert event['stack'][1]==e[4]
            ext=struct.unpack('<I',g.read(e[4]+88,4))[0]
            assert struct.unpack('<I',g.read(ext+36,4))[0]==0
            points[event['stack'][0]]='TriageReturned';g.bp(event['stack'][0])
        if name=='TriageReturned':assert r['eax']==0
        if name=='MachineDependentEntry':
            assert event['stack'][0:2]==[e[6]+0x155b55,e[4]]
            assert memory_descriptors()==after_descriptors
            event['memory_descriptors_unchanged_by_mm_prefix']=True
            patched=g.read(e[80],5);assert patched[0]==0xe9
            assert (e[80]+5+struct.unpack('<i',patched[1:5])[0])&0xffffffff==e[88]
            event['temporary_jump_target']=hex(e[88])
        if name=='LowClearBegin':
            before_pdes=list(struct.unpack('<512I',g.read(0xc0300000,2048)))
            assert sum(bool(x&1) for x in before_pdes)>0
            event['present_low_pdes_before']=sum(bool(x&1) for x in before_pdes)
        if name=='LowMappingsCleared':
            after_pdes=list(struct.unpack('<512I',g.read(0xc0300000,2048)))
            assert not any(x&1 for x in after_pdes)
            event['absent_low_pdes_after']=512
            assert memory_descriptors()==after_descriptors
        if name=='RamScanCompleted':
            assert memory_descriptors()==after_descriptors
            total,low,high=[struct.unpack('<I',g.read(e[6]+rva,4))[0] for rva in [0x823d8,0x72734,0x81bb4]]
            assert (total,low,high)==(0x3bff,1,0x3bff)
            event['native_ram_totals']={'pages':total,'lowest':low,'highest':high}
            event['native_largest_candidate']=hex(r['ebx'])
            event['descriptor_list_unchanged']=True
        if name=='MapCheckpoint':
            frame=list(struct.unpack('<3I',g.read(r['ebp'],12)))
            assert frame[1:]==[e[6]+0x155b55,e[4]]
            event['native_mi_frame_verified']=True
        g.send('c')
    time.sleep(1)
    regs=command(a.monitor,'info registers')
    assert 'HLT=1' in regs
    result['final_registers']=regs
    result['passed']=True;save()
finally:
    if g:g.s.close()
    lock.close()
print('RTC calibration, native time-increment call, PIT programming and profile stop observed; partition hooks and BIOS page allocations verified; HAL returned, executive initialized and memory-manager prefix executed; native low-PDE clearing completed; high HAL checkpoint reached after RAM scan and before MM allocation or storage.')
