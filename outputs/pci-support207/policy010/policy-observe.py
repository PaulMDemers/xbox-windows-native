"""Read registration, interface announcements and actual system-button query outcomes."""
import uuid
r['policy_events']=[];r['policy_calls']=[]
policy_pending={}
def guid(p):return str(uuid.UUID(bytes_le=g.read(p,16)))
def policy_irp(p):
    stack=u32(p+0x60);raw=g.read(stack,36)
    return dict(address=p,status=u32(p+0x18),information=u32(p+0x1c),system_buffer=u32(p+0xc),current_stack=stack,stack_raw=raw.hex(),major=raw[0],ioctl=u32(stack+12))
def policy_observation(label,regs,identity):
    thread=identity['thread'];row=dict(site=label,utc=utc(),identity=identity,registers=regs)
    enter={'policy_register_enter':('register',7),'policy_state_enter':('state',2),'policy_connect_enter':('connect',2)}
    if label in enter:
        kind,n=enter[label];args=list(struct.unpack('<'+str(n+1)+'I',g.read(regs['esp'],4*(n+1))))
        call=dict(kind=kind,id=len(r['policy_calls'])+1,entry_esp=regs['esp'],identity=identity,args=args,entry_utc=utc(),caller=optional(code_reference,args[0]))
        if kind=='register':call.update(category=args[1],flags=args[2],guid=optional(guid,args[3]) if args[1]==2 else None,driver=optional(lambda p:uni(p+field('_DRIVER_OBJECT','DriverName')),args[4]),callback=locate(args[5]),context=args[6],output=args[7])
        if kind=='state':call.update(name=optional(uni,args[1]),enable=args[2]&255)
        if kind=='connect':call.update(policy_type=args[1],name=optional(uni,args[2]))
        r['policy_calls'].append(call);policy_pending.setdefault((thread,kind),[]).append(call);row['call_id']=call['id']
    elif label in ('policy_register_end','policy_state_end','policy_connect_after_open','policy_connect_end'):
        kind={'policy_register_end':'register','policy_state_end':'state','policy_connect_after_open':'connect','policy_connect_end':'connect'}[label]
        calls=policy_pending.get((thread,kind),[])
        assert calls,(label,identity)
        call=calls[-1];assert regs['ebp']+4==call['entry_esp'];row['call_id']=call['id']
        if label=='policy_connect_after_open':
            call['open_status']=regs['eax'];row.update(open_status=regs['eax'],handle_slot=u32(regs['ebp']-12),object_attributes=g.read(regs['ebp']-60,24).hex())
        else:
            call['end_utc']=utc();call['status']=regs['eax'] if kind=='register' else regs['edi'] if kind=='state' else None
            if kind=='register':call['registered_entry']=optional(u32,call['output'])
            calls.pop()
    elif label=='policy_internal_state_enter':
        args=list(struct.unpack('<4I',g.read(regs['esp'],16)));row.update(args=args,name=optional(uni,args[1]),enable=args[2]&255,third_argument=args[3],caller=optional(code_reference,args[0]))
    elif label=='policy_notify_enter':
        args=list(struct.unpack('<4I',g.read(regs['esp'],16)));row.update(args=args,event_guid=optional(guid,args[1]),interface_guid=optional(guid,args[2]),name=optional(uni,args[3]),caller=optional(code_reference,args[0]))
    elif label=='policy_callback_enter':
        args=list(struct.unpack('<3I',g.read(regs['esp'],12)));p=args[1];row.update(args=args,notification_raw=g.read(p,40).hex(),event_guid=guid(p+4),interface_guid=guid(p+20),name=optional(uni,u32(p+36)),context=args[2])
    elif label in ('policy_button_enter','policy_complete_enter'):
        args=list(struct.unpack('<4I',g.read(regs['esp'],16)));row.update(args=args,device=optional(device,args[1]),irp=optional(policy_irp,args[2]),context=args[3],context_raw=optional(lambda p:g.read(p,20).hex(),args[3]),caller=optional(code_reference,args[0]))
    elif label=='policy_button_submit':
        p=regs['edx'];stack=u32(p+0x60)-36;row.update(irp=optional(policy_irp,p),target=optional(device,regs['ecx']),next_stack=stack,next_stack_raw=g.read(stack,36).hex(),ioctl=u32(stack+12),output_length=u32(stack+4),input_length=u32(stack+8),system_buffer=u32(p+12),buffer_before=optional(lambda p:g.read(p,4).hex(),u32(p+12)))
    elif label=='policy_button_cleanup':row.update(context=regs['esi'],context_raw=g.read(regs['esi'],20).hex(),irp=optional(policy_irp,regs['edi']))
    r['policy_events'].append(row)
def policy_finished():
    failed=[c for c in r['policy_calls'] if c['kind']=='connect' and c.get('open_status')==0xc0000043 and 'end_utc' in c]
    return len(failed)>=2 and not any(policy_pending.values())
