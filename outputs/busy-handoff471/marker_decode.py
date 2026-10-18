"""Independent strict successful-marker decoder; failures never imply LED output."""
import struct

def success(data, stage):
    if len(data)!=96 or stage not in (1,2):raise ValueError('record length/stage')
    r=struct.unpack('<24I',data)
    def need(ok,label):
        if not ok:raise ValueError(label)
    need(r[:5]==(0x354b524d,1,96,stage,0xff if stage==1 else 0xa5),'identity')
    need(r[5:9]==(1,2,3,0x10),'terminal result/completion')
    need(4<=r[9]<=4096,'poll bound')
    start=r[10]+(r[11]<<32);end=r[12]+(r[13]<<32)
    need(start<=end<start+64000000,'timestamp interval')
    need(all(x in (0,0x10) for x in r[14:16]),'idle status')
    need(r[16:19]==(0x10,0x10,1),'completion statuses/transaction')
    need(r[20]==sum(x==0x10 for x in r[14:16]),'ack count')
    need(r[19]==8+r[20] and r[21]==1+r[9],'write/time counts')
    need(r[22:24]==(1,0),'done/reserved')
    return dict(stage=stage,result=r[5],completed=r[6],started_mask=r[7],polls=r[9],
                tsc_start=start,tsc_end=end,io_writes=r[19],acks=r[20],done=True)
