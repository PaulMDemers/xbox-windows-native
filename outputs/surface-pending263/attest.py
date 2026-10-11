"""Read-only checkpoint attestation. No dirty-arena read, mutation or execution."""
import hashlib,struct

def u32(data):
    assert len(data)==4
    return struct.unpack('<I',data)[0]

def translate32(physical_read,cr3,cr4,virtual,forbidden):
    assert not cr4&0x20,'PAE is outside this pinned NT5 diagnostic'
    assert 0<=virtual<=0xffffffff and cr3&~0xffffffff==0
    def word(address):
        assert 0<=address<=0x4000000-4
        assert address+4<=forbidden[0] or address>=forbidden[1],'Page table aliases protected arena'
        return u32(physical_read(address,4))
    pde_address=(cr3&0xfffff000)+(virtual>>22)*4;pde=word(pde_address)
    assert pde&1,'Nonresident PDE'
    if pde&128:
        assert cr4&0x10,'Large page without PSE'
        return (pde&0xffc00000)+(virtual&0x3fffff),dict(pde_address=pde_address,pde=pde,large=True)
    pte_address=(pde&0xfffff000)+((virtual>>12)&1023)*4;pte=word(pte_address)
    assert pte&1,'Nonresident PTE'
    return (pte&0xfffff000)+(virtual&4095),dict(pde_address=pde_address,pde=pde,pte_address=pte_address,pte=pte,large=False)

def handle_entry(read,table,handle,off):
    assert 0<handle<0x4000000 and not handle&3,'Only aligned user NT5 handles'
    def ptr(address):
        value=u32(read(address,4));assert 0x80000000<=value<=0xfffffffc and not value&3
        return value
    top=ptr(table+off('_HANDLE_TABLE','Table'))
    middle=ptr(top+((handle>>18)&255)*4)
    leaf=ptr(middle+((handle>>10)&255)*4)
    entry=leaf+((handle>>2)&255)*8
    raw=read(entry,8);obj,access=struct.unpack('<II',raw);assert obj
    header=(obj|0x80000000)&0xfffffff8;body=header+off('_OBJECT_HEADER','Body')
    return body,dict(top=top,middle=middle,leaf=leaf,entry=entry,raw=raw.hex(),header=header,access=access)

class Attestor:
    def __init__(self,plan,pes,read,physical_read):
        self.plan,self.pes,self.read,self.physical_read=plan,pes,read,physical_read
        self.L=plan['structures'];self.pins=[]
    def off(self,t,n):return self.L[t]['fields'][n]['offset']
    def word(self,a):return u32(self.read(a,4))
    def kp(self,a):
        p=self.word(a);assert 0x80000000<=p<=0xfffffffc and not p&3
        return p
    def header(self,name,base):
        assert self.read(base,2)==b'MZ';peoff=self.word(base+60);assert 0x40<=peoff<4096
        raw=self.read(base+peoff,0x60);assert raw[:4]==b'PE\0\0'
        m=self.plan['modules'][name]
        assert struct.unpack_from('<H',raw,4)[0]==0x14c
        assert u32(raw[8:12])==m['timestamp'] and u32(raw[0x50:0x54])==m['image_size']
    def pin(self,name,base,rva,size):
        assert 0<size<=16384
        pe=self.pes[name];expected=bytearray(pe.get_data(rva,size));assert len(expected)==size
        reloc=[]
        for block in getattr(pe,'DIRECTORY_ENTRY_BASERELOC',[]):
            for e in block.entries:
                if e.type==3 and rva<=e.rva<rva+size:
                    pos=e.rva-rva;assert pos+4<=size
                    val=u32(expected[pos:pos+4]);struct.pack_into('<I',expected,pos,(val+base-pe.OPTIONAL_HEADER.ImageBase)&0xffffffff);reloc.append(pos)
        observed=self.read(base+rva,size);assert observed==expected,(name,hex(rva),'Resident instruction mismatch')
        self.pins.append(dict(module=name,base=base,rva=rva,size=size,relocations=reloc,sha256=hashlib.sha256(observed).hexdigest()))
    def modules(self,kernel):
        head=kernel+self.plan['module_list_rva'];q=self.kp(head);seen=set();rows=[];last=head
        while q!=head:
            assert q not in seen and len(seen)<128;seen.add(q)
            assert self.word(q+4)==last,'Loaded module backward-link mismatch'
            node=q-self.off('_LDR_DATA_TABLE_ENTRY','InLoadOrderLinks')
            base=self.kp(node+self.off('_LDR_DATA_TABLE_ENTRY','DllBase'))
            size=self.word(node+self.off('_LDR_DATA_TABLE_ENTRY','SizeOfImage'));assert 0<size<=0x1000000
            n,maximum,p=struct.unpack('<HHI',self.read(node+self.off('_LDR_DATA_TABLE_ENTRY','BaseDllName'),8))
            assert n and n%2==0 and n<=maximum<=2048 and p>=0x80000000
            rows.append(dict(base=base,size=size,name=self.read(p,n).decode('utf-16le').lower()))
            last=q;q=self.kp(q)
        assert self.word(head+4)==last
        return rows
    def checkpoint(self,stage,registers,cr3,cr4):
        assert 1<=stage<=5
        self.pins=[];p=self.plan;k=p['kernel_base_lead'];self.header('ntoskrnl.exe',k)
        for site in p['handle_semantics']:self.pin('ntoskrnl.exe',k,site['rva'],site['size'])
        thread=self.kp(p['current_thread_address']);process=self.kp(thread+p['thread_owner_offset'])
        pid=self.word(process+self.off('_EPROCESS','UniqueProcessId'));assert 0<pid<0x100000
        image_name=self.read(process+self.off('_EPROCESS','ImageFileName'),16).split(b'\0')[0];assert image_name==b'probe.exe'
        base=self.word(process+self.off('_EPROCESS','SectionBaseAddress'));self.header('probe.exe',base)
        assert base==p['modules']['probe.exe']['preferred_base'] and registers['eip']==base+p['checkpoint_rva']
        dtb=self.word(process+self.off('_KPROCESS','DirectoryTableBase'));assert dtb&0xfffff000==cr3&0xfffff000
        caller,actual_stage,reply,handle=struct.unpack('<4I',self.read(registers['esp'],16))
        assert actual_stage==stage and reply==base+p['reply_rva']
        call=next(c for c in p['callsites'] if c['stage']==stage);assert caller==base+call['rva']+5
        for name,at in [('probe.exe',base)]:
            mod=p['modules'][name];self.pin(name,at,mod['text_rva'],mod['text_size'])
        rows=self.modules(k)
        assert sum(m['name']=='ntoskrnl.exe' and m['base']==k for m in rows)==1
        driver=[m for m in rows if m['name']=='pattern.sys'];assert len(driver)==1;driver=driver[0]
        db=driver['base'];self.header('pattern.sys',db)
        dm=p['modules']['pattern.sys'];assert driver['size']==(dm['image_size']+4095)&~4095
        self.pin('pattern.sys',db,dm['text_rva'],dm['text_size'])
        ar=self.read(db+p['arena_rva'],32);owner,virtual,generation,physical,closed,reads,writes,attempted=struct.unpack('<8I',ar)
        expected=[(0,0),(1,0),(2,0),(3,1),(4,1)][stage-1]
        assert (generation,closed,reads,writes,attempted)==(1,0,*expected,1)
        assert 0x100000<=physical<=0x03bfc000 and not physical&4095
        assert 0x80000000<=virtual<=0xffffc000 and not virtual&4095
        assert 0x80000000<=owner<=0xffffff00 and not owner&3
        # Header only. Reading Reply.data is unnecessary; never read arena bytes.
        rh=struct.unpack('<8I',self.read(reply,32));assert rh==(258,0,1,physical,16384,0,*expected)
        table=self.kp(process+self.off('_EPROCESS','ObjectTable'))
        assert self.word(table+self.off('_HANDLE_TABLE','UniqueProcessId'))==pid
        assert self.word(table+self.off('_HANDLE_TABLE','QuotaProcess'))==process
        # The pinned probe requests GENERIC_WRITE; DeviceIoControl does not
        # require FILE_READ_DATA even when the buffered IOCTL returns data.
        body,entry=handle_entry(self.read,table,handle,self.off);assert body==owner and entry['access']&2==2
        typ,size=struct.unpack('<HH',self.read(owner,4));assert typ==5 and size==self.L['_FILE_OBJECT']['size']
        counts={n:self.word(entry['header']+self.off('_OBJECT_HEADER',n)) for n in ['PointerCount','HandleCount']}
        assert 0<counts['HandleCount']<=counts['PointerCount']<0x100000
        dev=self.kp(owner+self.off('_FILE_OBJECT','DeviceObject'))
        dr=self.kp(dev+self.off('_DEVICE_OBJECT','DriverObject'))
        assert self.word(dr+self.off('_DRIVER_OBJECT','DriverStart'))==db
        assert self.word(dr+self.off('_DRIVER_OBJECT','DriverSize'))==driver['size']
        pages=[];walks=[]
        for i in range(4):
            pa,walk=translate32(self.physical_read,cr3,cr4,virtual+4096*i,(physical,physical+16384))
            assert pa==physical+4096*i;pages.append(pa);walks.append(walk)
        return dict(stage=stage,thread=thread,process=process,pid=pid,image=image_name.decode(),probe_base=base,
            checkpoint=registers['eip'],caller=caller,reply=reply,handle=handle,handle_entry=entry,
            file_object=owner,object_counts=counts,device_object=dev,driver_object=dr,driver_module=driver,
            arena_address=db+p['arena_rva'],arena_raw=ar.hex(),virtual=virtual,physical=physical,
            generation=generation,reads=reads,writes=writes,cr3=cr3,cr4=cr4,pages=pages,walks=walks,
            modules=rows,pins=self.pins.copy(),dirty_arena_read=False,passed=True)
