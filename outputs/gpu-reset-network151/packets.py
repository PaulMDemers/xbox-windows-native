"""Bounded Ethernet/IPv4/DHCP decoder; retain offsets and transaction identity."""
import collections,hashlib,ipaddress,struct
MAX_BYTES=16*1024*1024
def address(b):return str(ipaddress.IPv4Address(b))
def decode(data):
    assert 24<=len(data)<=MAX_BYTES
    assert data[:4]==b'\xd4\xc3\xb2\xa1'
    major,minor,zone,sig,snap,link=struct.unpack_from('<HHIIII',data,4)
    assert (major,minor,link)==(2,4,1) and 0<snap<=65536
    pos=24;frames=[];dhcp=[];counts=collections.Counter()
    while pos<len(data):
        at=pos;assert pos+16<=len(data),'Partial packet header'
        sec,usec,n,original=struct.unpack_from('<IIII',data,pos);pos+=16
        assert usec<1000000 and 14<=n<=snap and n==original and pos+n<=len(data),'Truncated packet'
        f=data[pos:pos+n];pos+=n;kind=struct.unpack_from('>H',f,12)[0]
        row=dict(offset=at,end_offset=pos,seconds=sec,microseconds=usec,bytes=n,ether_type=kind,
                 source_mac=f[6:12].hex(':'),destination_mac=f[:6].hex(':'))
        counts[str(kind)]+=1
        if kind==0x800:
            ip=f[14:];assert len(ip)>=20 and ip[0]>>4==4
            ihl=(ip[0]&15)*4;length=struct.unpack_from('>H',ip,2)[0]
            assert 20<=ihl<=length<=len(ip)
            row.update(protocol=ip[9],source=address(ip[12:16]),destination=address(ip[16:20]))
            flags=struct.unpack_from('>H',ip,6)[0]
            if ip[9]==6 and flags&0x3fff==0:
                tcp=ip[ihl:length];assert len(tcp)>=20
                head=(tcp[12]>>4)*4;assert 20<=head<=len(tcp)
                sport,dport,seq,ack=struct.unpack_from('>HHII',tcp)
                row.update(source_port=sport,destination_port=dport,sequence=seq,acknowledgement=ack,
                           tcp_flags=tcp[13],tcp_payload_bytes=len(tcp)-head)
                if sport==21:
                    row.update(ftp_greeting_part=tcp[head:].startswith(b'220-'),
                               ftp_greeting_ready=tcp[head:].startswith(b'220 '))
            if ip[9]==17 and flags&0x3fff==0:
                udp=ip[ihl:length];assert len(udp)>=8
                sport,dport,size,cs=struct.unpack_from('>HHHH',udp);assert 8<=size<=len(udp)
                row.update(source_port=sport,destination_port=dport)
                bootp=udp[8:size]
                if {sport,dport}=={67,68}:
                    assert len(bootp)>=240 and bootp[236:240]==b'\x63\x82\x53\x63'
                    assert bootp[1:3]==b'\x01\x06'
                    opts={};q=240;ended=False
                    while q<len(bootp):
                        tag=bootp[q];q+=1
                        if tag==255:ended=True;break
                        if tag==0:continue
                        assert q<len(bootp);size=bootp[q];q+=1;assert q+size<=len(bootp)
                        assert tag not in opts,'Duplicate option outside decoder contract'
                        opts[tag]=bootp[q:q+size];q+=size
                    assert ended and len(opts.get(53,b''))==1
                    d=dict(offset=at,end_offset=pos,type=opts[53][0],xid=struct.unpack_from('>I',bootp,4)[0],
                           client_mac=bootp[28:34].hex(':'),op=bootp[0],client_address=address(bootp[12:16]),
                           offered_address=address(bootp[16:20]),source=row['source'],destination=row['destination'])
                    if 50 in opts:assert len(opts[50])==4;d['requested_address']=address(opts[50])
                    if 54 in opts:assert len(opts[54])==4;d['server']=address(opts[54])
                    dhcp.append(d)
        frames.append(row);assert len(frames)<=65536
    return dict(sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),frames=frames,dhcp=dhcp,
                ether_types=dict(counts),complete=True)
