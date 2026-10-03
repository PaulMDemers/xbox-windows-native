"""Summarize only packets in this task's isolated xemu capture."""
import argparse,pathlib,struct,json,collections,hashlib,ipaddress
p=argparse.ArgumentParser();p.add_argument('pcap',type=pathlib.Path);p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args();data=a.pcap.read_bytes();assert data[:4]==b'\xd4\xc3\xb2\xa1'
major,minor,zone,sig,snap,link=struct.unpack_from('<HHIIII',data,4);assert link==1
pos=24;frames=[];counts=collections.Counter();dhcp=[];echo=[];bad=[]
def checksum(b):
 if len(b)%2:b+=b'\0'
 n=sum(struct.unpack('>'+'H'*(len(b)//2),b));n=(n&65535)+(n>>16);n=(n&65535)+(n>>16);return (~n)&65535
while pos+16<=len(data):
 sec,usec,n,original=struct.unpack_from('<IIII',data,pos);pos+=16
 if pos+n>len(data):break
 f=data[pos:pos+n];pos+=n
 if len(f)<14:continue
 kind=struct.unpack_from('>H',f,12)[0];counts[hex(kind)]+=1;frames.append(n)
 if kind!=0x800:continue
 ip=f[14:];ihl=(ip[0]&15)*4;length=struct.unpack_from('>H',ip,2)[0];ip=ip[:length]
 if checksum(ip[:ihl]):bad.append({'frame':len(frames),'kind':'IPv4'})
 src=str(ipaddress.IPv4Address(ip[12:16]));dst=str(ipaddress.IPv4Address(ip[16:20]));payload=ip[ihl:]
 if ip[9]==1 and len(payload)>=8:
  if checksum(payload):bad.append({'frame':len(frames),'kind':'ICMP'})
  typ,code,cs,ident,seq=struct.unpack_from('>BBHHH',payload)
  if typ in [0,8]:echo.append({'type':typ,'source':src,'destination':dst,'id':ident,'sequence':seq,'payload':payload[8:].hex()})
 if ip[9]==17 and len(payload)>=8:
  sport,dport,size,cs=struct.unpack_from('>HHHH',payload);udp=payload[:size]
  if cs and checksum(ip[12:20]+bytes([0,17])+struct.pack('>H',size)+udp):bad.append({'frame':len(frames),'kind':'UDP'})
  if {sport,dport}=={67,68} and len(udp)>=248 and udp[244:248]==b'\x63\x82\x53\x63':
   opts={};q=248
   while q<len(udp):
    tag=udp[q];q+=1
    if tag==255:break
    if tag==0:continue
    size=udp[q];q+=1;opts[tag]=udp[q:q+size];q+=size
   dhcp.append({'type':opts.get(53,b'\0')[0],'offered_address':str(ipaddress.IPv4Address(udp[24:28]))})
requests=[e for e in echo if e['type']==8];replies=[e for e in echo if e['type']==0]
matched=sum(any(r['id']==q['id'] and r['sequence']==q['sequence'] and r['payload']==q['payload'] and r['source']==q['destination'] and r['destination']==q['source'] for r in replies) for q in requests)
report={'scope':'Isolated emulated Xbox Ethernet; reply capture alone does not establish guest receipt; correlate the guest ping log.','sha256':hashlib.sha256(data).hexdigest(),'pcap_version':[major,minor],'frame_count':len(frames),'ether_types':dict(counts),'dhcp':dhcp,'echo_requests':len(requests),'echo_replies':len(replies),'requests_with_matching_reply':matched,'checksum_errors':bad,'all_complete_records_parsed':pos==len(data)}
a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
