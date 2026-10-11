"""Bridge the captured kernel-mode syscall trap into the power-policy callback."""
import hashlib,json,struct,sys,uuid
from pathlib import Path
k=Path(__file__).resolve().parent;repo=k.parents[2]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0,'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
import pefile,capstone
plan=read(k/'preflight001.json');t=read(k/'veto001/trace.json');layout=read(k/'trap-layout001.json')
pub=read(repo/'outputs/native-windows-nt5-kernel/kernel-publics.json')
assert layout['pdb_sha256']==pub['pdb_sha256']==read(k/'stack-layouts001.json')['pdb_sha256']
provider=plan['providers']['ntoskrnl.exe'];assert sha(Path(provider['path']))==provider['sha256']
pe=pefile.PE(provider['path']);K=plan['kernel_base_expected'];cs=capstone.Cs(capstone.CS_ARCH_X86,capstone.CS_MODE_32)
rva=lambda n:pub['symbols'][n]['rva']
expected={'_KiSystemService':0x64f70,'_ZwOpenFile@24':0x2fea4,'_PopConnectToPolicyDevice@8':0xdd9ae,'_PopNotifyPolicyDevice@8':0xdd976,'_IopPnPHydraCallback@4':0xa600e,'_MmDispatchWin32Callout@16':0x1324cc,'_IopNotifyDeviceClassChange@12':0xa5468,'_PiWalkDeviceList@4':0x10c3ec,'_PopSystemButtonHandler@12':0xde13e,'_PopSwitches':0x82960}
for name,address in expected.items():assert rva(name)==address
ranges=[]
for name,end in [('_KiSystemService',0x65034),('_ZwOpenFile@24',0x2feb2),('_PopConnectToPolicyDevice@8',0xddbda),('_PopNotifyPolicyDevice@8',0xdd9ae),('_IopPnPHydraCallback@4',0xa601d),('_MmDispatchWin32Callout@16',0x13251f),('_IopNotifyDeviceClassChange@12',0xa5558),('_PiWalkDeviceList@4',0x10c4d3)]:
    start=rva(name);raw=pe.get_data(start,end-start);ins=list(cs.disasm(raw,start))
    ranges.append(dict(symbol=name,rva=start,raw=raw.hex(),instructions=[dict(rva=x.address,bytes=x.bytes.hex(),mnemonic=x.mnemonic,operands=x.op_str) for x in ins]))
def expect(at,hexbytes):assert pe.get_data(at,len(bytes.fromhex(hexbytes)))==bytes.fromhex(hexbytes),(hex(at),hexbytes)
expect(0x64fac,'8bec') # EBP is the newly constructed trap-frame base.
expect(0x65032,'ffd3') # Native service call returns to 65034.
expect(0x2fea4,'b8640000008d542404cd2ec21800')
expect(0xdda13,'e88c24f5ff') # PopConnect -> ZwOpenFile.
expect(0xdd99a,'e80f000000') # PopNotify -> PopConnect.
expect(0xdd976,'538b5c24085657') # Three saved registers, no EBP frame.
expect(0xa600e,'8b442404ff7008ff7004ff10c20400')
expect(0x132517,'ff550c')
expect(0xa5529,'e89ecf0800')
fields=layout['structures']['_KTRAP_FRAME']['fields'];rows=[]
for c in t['calls']:
    if c.get('status')!=0xc0000043:continue
    st=c['entry_stack'];base=st['esp'];raw=bytes.fromhex(st['raw_stack'])
    def data(a,n):
        assert base<=a and a+n<=base+len(raw)
        return raw[a-base:a-base+n]
    u=lambda a:struct.unpack('<I',data(a,4))[0]
    service=next(f for f in st['frames'] if f['return_address']['address']==K+0x65034)
    trap=service['previous'];saved={name:u(trap+fields[name]['offset']) for name in ('Eip','SegCs','EFlags','Ebp')}
    assert saved['Eip']==K+0x2feaf and saved['SegCs']==8
    # Same-privilege INT 2E pushes EIP/CS/EFLAGS only. HardwareEsp is a
    # layout boundary here, NOT a CPU-pushed ESP value. Its address is the
    # original kernel ESP, whose first word is ZwOpenFile's caller return.
    zw_esp=trap+fields['HardwareEsp']['offset'];assert u(zw_esp)==K+0xdda18
    args=list(struct.unpack('<6I',data(zw_esp+4,24)))
    assert args==list(struct.unpack('<6I',data(service['frame']+8,24)))
    assert args[1]==0x100003 and args[4]==3 and args[5]==0x10
    frame=saved['Ebp'];assert u(frame+4)==K+0xdd99f and u(frame+8)==0
    assert args[0]==frame-12 and args[2]==frame-60 and args[3]==frame-36
    assert u(args[2])==24 and u(args[2]+8)==u(frame+12) and u(args[2]+12)==0x240
    notify_return_slot=frame+28;assert u(notify_return_slot)==K+0xa601a
    notification=u(notify_return_slot+4);context=u(notify_return_slot+8);assert context==0
    hydra_return_slot=notify_return_slot+12;assert u(hydra_return_slot)==K+0x13251a
    bundle=u(hydra_return_slot+4);assert [u(bundle+i) for i in (0,4,8)]==[K+0xdd976,notification,context]
    mm_frame=u(frame);assert u(mm_frame+4)==K+0xa552e
    assert [u(mm_frame+i) for i in (8,12,16)]==[K+0xdd976,K+0xa600e,bundle]
    notify_frame=u(mm_frame);assert notification==notify_frame-0x34
    assert u(notify_frame+4)==K+0x10c4ce
    assert data(notification,4)==bytes.fromhex('01002800')
    event=data(notification+4,16);assert event==pe.get_data(rva('_GUID_DEVICE_INTERFACE_ARRIVAL'),16)
    interface=data(notification+20,16);name_pointer=u(notification+36);assert name_pointer==u(frame+12)
    assert interface==uuid.UUID('4d1e55b2-f16f-11cf-88cb-001111000030').bytes_le
    assert u(frame)>frame and u(mm_frame)>mm_frame
    rows.append(dict(call_id=c['id'],class_driver=c['caller']['module'],thread=c['identity']['thread'],trap_frame=trap,saved_trap_fields=saved,kernel_zw_entry_esp=zw_esp,zw_return_rva='0xdda18',zw_args=args,power_policy_frame=frame,policy_type=0,object_attributes=data(args[2],24).hex(),notify_return_slot=notify_return_slot,hydra_return_slot=hydra_return_slot,mm_frame=mm_frame,pnp_notify_frame=notify_frame,notification=notification,event_guid=str(uuid.UUID(bytes_le=event)),interface_guid=str(uuid.UUID(bytes_le=interface)),notification_raw=data(notification,40).hex(),unicode_header=data(name_pointer,8).hex(),symbolic_link_text_captured=False,call_chain=['PiWalkDeviceList','IopNotifyDeviceClassChange','MmDispatchWin32Callout','IopPnPHydraCallback','PopNotifyPolicyDevice','PopConnectToPolicyDevice(type=0)','ZwOpenFile','KiSystemService','NtOpenFile','IoCreateFile','IopCreateFile','object parsing and class CREATE','HIDCLASS sharing denial']))
assert len(rows)==2
# Static type-zero continuation belongs to system-button policy. This path is
# NOT claimed executed: the failed open takes its earlier cleanup branch.
expect(0xddb83,'c7450c3ee14d00')
expect(0xdda18,'3bc70f8ca9010000')
result=dict(review_passed=True,power_policy_reopen_caller_proven=True,policy_type_zero_system_button_continuation_identified=True,static_success_continuation_executed=False,rows=rows,static_ranges=ranges,kernel_sha256=provider['sha256'],pdb_sha256=pub['pdb_sha256'],trace_sha256=sha(k/'veto001/trace.json'),script_sha256=sha(Path(__file__)),limits='Reconstructed from live saved stack/trap/arguments and the exact kernel image. Upper callback sites were not separately breakpoint-pinned. Lower sites and loaded kernel identity were verified live. Symbolic-link text, policy-registration history and power-button behavior remain unknown; no complete FPO unwind or ordinary timing qualification is claimed.')
dest=k/'caller-review002.json';assert not dest.exists();dest.write_text(json.dumps(result,indent=2)+'\n');print('Both failures bridge through ZwOpenFile to PopConnectToPolicyDevice(type0), PopNotifyPolicyDevice and interface-arrival dispatch')
