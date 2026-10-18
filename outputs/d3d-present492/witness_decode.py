"""Independent bounded receipt decoder; no receipt can prove its own close."""
import struct
from primary_decode import decode
from legacy_refusal_decode import decode_refusal as legacy_refusal

def need(value,message):
    if not value:raise ValueError(message)

def marker_success(data):
    need(len(data)==96,'marker length')
    m=struct.unpack('<24I',data)
    need(m[:8]==(0x354b524d,1,96,1,255,1,2,3),'completed marker identity')
    need(m[8]==16 and 4<=m[9]<=4096,'status/poll bounds')
    need(m[14] in (0,16) and m[15] in (0,16) and m[16:19]==(16,16,1),'two completed transactions')
    need(m[20]==sum(v==16 for v in m[14:16]) and m[19]==8+m[20],'writes and acknowledgments')
    need(m[21]==m[9]+1 and m[22:]==(1,0),'terminal clock count')
    start=m[10]+(m[11]<<32);end=m[12]+(m[13]<<32)
    need(start<=end<start+64000000,'bounded clock')
    return dict(completed_transactions=2,polls=m[9],tsc_start=start,tsc_end=end)

def decode_witness(data,primary):
    p=decode(primary)
    need(p['preparation_verified'],'ineligible primary')
    need(len(data)==256,'witness length')
    w=struct.unpack('<64I',data);r=struct.unpack('<44I',primary)
    need(w[:4]==(0x30393448,1,256,0x49000101),'witness identity')
    need(w[4:10]==(2,6,1,1,r[12],1024),'preceding close/check state')
    need(w[10:16]==(r[6],r[8],r[9],r[7],r[37],0),'allocation/target identity')
    m=marker_success(data[64:160])
    need(w[40:49]==r[32:40]+(r[28],),'original saved frame')
    need(not any(w[49:60]),'reserved')
    need(w[60:]==(0x454e4f44,1,0x49000101,256),'witness trailer')
    return dict(record_complete=True,preceding_primary_close_and_comparisons_proved=True,
                preceding_marker=m,witness_flush_close_proved=False,
                post_witness_comparisons_proved=False,paging_transition_executed=None,
                windows_started=None,hardware_origin='requires external evidence')

def decode_refusal(data):
    need(len(data)==192,'refusal length')
    q=struct.unpack('<48I',data);reason=q[4]
    if reason<=12:return legacy_refusal(data)
    need(q[:4]==(0x30393452,2,192,0x49000101) and q[44:]==(0x454e4f44,2,0x49000101,192),'refusal identity')
    need(13<=reason<=19 and q[19]==0,'witness refusal reason')
    need(q[10:16]==(6,1,1,1,1,1) and not q[16]&1024 and q[17]==0,'preparation state')
    need(q[9]==(0 if reason<16 else 1 if reason==16 else 2),'witness close state')
    need(not (q[9] or not q[8]) or q[18]==0xeeeeeeee,'cleanup close order')
    need(reason==13 or q[8]!=0,'missing witness handle')
    if reason==13:need(q[5]!=0 or q[6]!=0 or q[7]!=2 or not q[8],'create did not refuse')
    if reason==14:need(q[5]!=0 or q[6]!=0 or q[7]!=256,'write did not refuse')
    if reason==15:need(q[5]!=0 or q[6]!=0,'flush did not refuse')
    if reason==16:need(q[5]!=0 and q[6]==0,'close did not refuse')
    if reason>=17:need(q[6]==0 and (reason==17 or q[5]==0),'post-witness mismatch state')
    marker_success(data[80:176])
    return dict(record_complete=True,deliberate_wrapper_refusal=True,reason=reason,
                handle_role='witness',return_status=q[5],iosb_status=q[6],iosb_information=q[7],
                close_state=q[9],cleanup_status=q[18],paging_transition_proved=False,
                fallback_flush_close_proved=False)

def classify(primary,witness=None,refusal=None):
    p=decode(primary)
    w=None if witness is None else decode_witness(witness,primary)
    f=None if refusal is None else decode_refusal(refusal)
    if f and f['reason']<=12:need(w is None,'witness preceded refused boundary')
    return dict(preparation=p,witness=w,refusal=f,
                boundary_observed=w is not None,wrapper_refused=f is not None,
                windows_started=None,boot_qualified=False)
