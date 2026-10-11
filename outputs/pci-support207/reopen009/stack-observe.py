"""Read bounded live kernel frames; raw stack candidates are not an unwind."""
def code_reference(address):
    row=locate(address)
    if row.get('module') in pes:
        start=address-16
        pin(start)
        row.update(window_start=start,window=g.read(start,32).hex())
    return row

def stack_observation(regs,at_entry):
    thread=u32(0xffdff124)
    low=u32(thread+field('_KTHREAD','StackLimit'))
    high=u32(thread+field('_KTHREAD','StackBase'))
    assert 0x80000000<=low<=regs['esp']<high and high-low<=0x10000
    row=dict(thread=thread,stack_limit=low,stack_base=high,esp=regs['esp'],ebp=regs['ebp'],frames=[],at_helper_entry=at_entry)
    size=min(4096,high-regs['esp'])
    row['raw_stack']=g.read(regs['esp'],size).hex()
    if at_entry:row['immediate_return']=code_reference(u32(regs['esp']))
    frame=regs['ebp'];seen=set()
    for index in range(48):
        if not (regs['esp']<=frame and low<=frame and frame+8<=high and frame%4==0):
            row['termination']='frame_outside_stack_or_unaligned';break
        if frame in seen:row['termination']='cycle';break
        seen.add(frame)
        previous,ret=struct.unpack('<II',g.read(frame,8))
        row['frames'].append(dict(frame=frame,previous=previous,return_address=code_reference(ret),words=g.read(frame,min(48,high-frame)).hex()))
        if previous<=frame:row['termination']='nonascending_frame';break
        frame=previous
    else:row['termination']='frame_bound'
    row['limits']='EBP links plus pinned return neighborhoods; FPO gaps and raw stack words require separate instruction review.'
    return row
