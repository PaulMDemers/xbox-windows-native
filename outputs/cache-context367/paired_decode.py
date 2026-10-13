"""Cold refusal is evidence of incomplete residency, never a full cold PASS."""
import hashlib,struct
from decode import BYTES,cpu,decode,need

def paired(cold,warm):
    result=decode(warm,True)
    need(len(cold)==BYTES,'cold packet length')
    c=struct.unpack('<16640I',cold);w=struct.unpack('<16640I',warm)
    need(c[:3]==(0x4d57584e,354,BYTES),'cold identity')
    need(c[4:14]==w[4:14],'cold/warm owner or geometry changed')
    # Intel253668-021 section2.5: only MP(bit1)/TS(bit3) govern FP task context.
    # Keep all raw bits; all paging/cache/CR3/CR4/PAT/MTRR/CPUID fields equal.
    need(c[17:96]==w[17:96] and not ((c[16]^w[16])&~0xA),'cold/warm memory-policy context changed')
    need(c[15]==4096 and 0<c[14]<=w[14],'cold capacity')
    cpu(c[16:96])
    if c[3]==0:
        complete=decode(cold)
        record=dict(complete=True,collector_status=0,counts=complete['counts'])
    else:
        need(c[3]==16,'unsupported cold refusal')
        need(not any(c[96:176]) and not any(c[177:256]),'partial cold unexpected trailing header')
        need(c[176]&1 and not c[176]&0x80 and (c[176]^c[17])&0xfffff000==0,'partial cold self map')
        need(not any(c[256+c[14]*4:]),'partial cold unused output')
        for i in range(c[14]):
            at=256+i*4;role,va,pde,pte=c[at:at+4]
            need((role,va)==w[at:at+2],'partial cold row order')
            need(pde&3==3 and not pde&0x84,'partial cold invalid PDE')
            if i+1==c[14]:
                need(not pte&1,'cold refusal is not absent PTE')
            else:
                need(pte&7==3,'earlier cold row invalid')
        record=dict(complete=False,collector_status=16,rows=c[14],absent_virtual=va,
                    pde=pde,pte=pte,scope='Prefix only; no PFN/cache interpretation of nonpresent PTE or proof of fault cause')
    record['sha256']=hashlib.sha256(cold).hexdigest()
    result['cold_residency']=record
    result['cross_capture_cr0']={'cold':c[16],'warm':w[16],'xor':c[16]^w[16],'allowed_nonmemory_mask':0xA}
    result['scope']='Complete post-full-buffer-read sampled page policy; cold residency separately preserved. CR0 MP/TS task-state differences retained separately; not CPU-context identity. No atomicity/TLB/alias or performance proof.'
    return result
