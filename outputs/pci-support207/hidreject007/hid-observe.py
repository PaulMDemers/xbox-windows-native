"""Read HID share predicates and retained owners through the pinned observer."""
def csrss_handles(targets):
    head=K+plan['active_process_head_rva'];q=u32(head);seen=set();rows=[]
    while q!=head:
        assert q not in seen and len(seen)<128;seen.add(q)
        process=q-field('_EPROCESS','ActiveProcessLinks');name=g.read(process+field('_EPROCESS','ImageFileName'),16).split(b'\0')[0]
        if name==b'csrss.exe':
            pid=u32(process+field('_EPROCESS','UniqueProcessId'));table=u32(process+field('_EPROCESS','ObjectTable'))
            assert u32(table+field('_HANDLE_TABLE','UniqueProcessId'))==pid
            assert u32(table+field('_HANDLE_TABLE','QuotaProcess'))==process
            count=u32(table+field('_HANDLE_TABLE','HandleCount'));entries=0;leaves=0;matches=[]
            top=struct.unpack('<256I',g.read(u32(table+field('_HANDLE_TABLE','Table')),1024))
            for high,middle in enumerate(top):
                if not middle:continue
                for mid,leaf in enumerate(struct.unpack('<256I',g.read(middle,1024))):
                    if not leaf:continue
                    leaves+=1;assert leaves<=1024
                    for low,(obj,access) in enumerate(struct.iter_unpack('<II',g.read(leaf,2048))):
                        if not obj:continue
                        entries+=1;header=(obj|0x80000000)&0xfffffff8;body=header+field('_OBJECT_HEADER','Body')
                        if body in targets:
                            matches.append(dict(handle=(high<<18)|(mid<<10)|(low<<2),entry=leaf+low*8,entry_words=[obj,access],file=body,header=header,header_raw=g.read(header,24).hex(),pointer_count=u32(header),handle_count=u32(header+4),granted_access=access))
            rows.append(dict(process=process,pid=pid,image='csrss.exe',table=table,reported_count=count,observed_count=entries,count_matches=count==entries,matches=matches))
        q=u32(q)
    return rows

def hid_observation(regs,label):
    frame=regs['ebp'];ext=u32(frame+8);irp=u32(frame+12);stack=u32(irp+0x60)
    raw=g.read(stack,L['_IO_STACK_LOCATION']['size']);assert raw[0]==0
    access=u32(u32(stack+4)+8);sharing=struct.unpack('<H',g.read(stack+14,2))[0]
    counters=dict(zip(('opens','readers','writers','deny_read','deny_write','deny_all'),struct.unpack('<6I',g.read(ext+0x2c,24))))
    tests=[('existing_deny_all',counters['deny_all']!=0),('new_deny_all',counters['opens']!=0 and sharing==0),('read_denied',bool(access&1) and counters['deny_read']!=0),('write_denied',bool(access&2) and counters['deny_write']!=0),('existing_readers_not_shared',counters['readers']>0 and not sharing&1),('existing_writers_not_shared',counters['writers']>0 and not sharing&2)]
    collection=u32(frame-12);head=collection+0x14;q=u32(head);seen=set();contexts=[]
    while q!=head:
        assert q not in seen and len(seen)<64;seen.add(q);context=q-0x18;file=u32(context+0x38)
        contexts.append(dict(address=context,list_entry=q,file=file,file_info=optional(file_info,file),desired_access=u32(context+0x40),share_access=struct.unpack('<H',g.read(context+0x44,2))[0],raw=g.read(context,0x68).hex()))
        q=u32(q)
    row=dict(extension=ext,irp=irp,stack=stack,stack_raw=raw.hex(),file=optional(file_info,u32(stack+24)),desired_access=access,share_access=sharing,counters=counters,collection=collection,list_head=head,contexts=contexts,predicted_first_rejection=next((name for name,test in tests if test),None),local_status=u32(frame-8),eflags=regs['eflags'])
    if label=='hid_read_denied_branch':row['jne_taken_by_flags']=not bool(regs['eflags']&0x40)
    if label=='hid_sharing_status':row['csrss_owners']=optional(csrss_handles,{x['file'] for x in contexts})
    return row
