"""Independent packet expectations and real localhost UDP; no console access."""
import argparse
import json
from pathlib import Path
import socket
import struct
import zlib
from receiver import capture, decode

ATTEMPT=bytes(range(1,17))
BUILD=bytes(range(128,160))


def expected(seed):
    groups={name:[(0x80000000^(seed*0x01010101)^(g*0x112233)^(i*0x9e3779b9))&0xffffffff
                  for i in range(n)]
            for g,(name,n) in enumerate((('request',8),('state',9),('trace',63),('pre',47),('post',47)))}
    if seed==0:
        groups['state'][0:2]=[255,22]; groups['pre'][0]=1; groups['post'][0]=0
    b=struct.pack('<8sII16s32siI',b'XWN655U1',1,772,ATTEMPT,BUILD,seed%3-1,1+seed%2)
    for values in groups.values(): b+=struct.pack('<'+'I'*len(values),*values)
    return b+struct.pack('<I',zlib.crc32(b)), groups


def main():
    p=argparse.ArgumentParser();p.add_argument('--packets',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    raw=a.packets.read_bytes();assert len(raw)==64*772
    checks=0
    for seed in range(64):
        packet, groups=expected(seed)
        assert packet==raw[seed*772:(seed+1)*772]
        decoded=decode(packet,ATTEMPT,BUILD)
        for name,values in groups.items(): assert decoded[name]==values
        assert decoded['result']==seed%3-1 and decoded['post_kind']==1+seed%2
        assert not decoded['hardware_execution_established'];checks+=1
    valid=raw[:772]
    def reject(packet,attempt=ATTEMPT,build=BUILD):
        nonlocal checks
        try: decode(packet,attempt,build)
        except ValueError: checks+=1
        else: raise AssertionError('bad packet accepted')
    for bit in range(len(valid)*8):
        damaged=bytearray(valid);damaged[bit//8]^=1<<(bit%8);reject(damaged)
    for length in range(772):reject(valid[:length])
    reject(valid+b'\x00');reject(valid,b'\x00'*16);reject(valid,ATTEMPT,b'\x00'*32)
    reject(valid,ATTEMPT[:-1]);reject(valid,ATTEMPT,BUILD[:-1])
    for offset,value in ((8,2),(12,771),(64,2),(64,0xfffffffe),(68,0),(68,3)):
        altered=bytearray(valid);struct.pack_into('<I',altered,offset,value)
        struct.pack_into('<I',altered,768,zlib.crc32(altered[:768]));reject(altered)
    manifest=dict(attempt=ATTEMPT.hex(),build_id=BUILD.hex(),expected_peer='127.0.0.1',fixture='host-loopback')
    def run(name,packets,maximum=64,peer='127.0.0.1'):
        with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as rx, socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as tx:
            rx.bind(('127.0.0.1',0))
            for packet in packets: tx.sendto(packet,rx.getsockname())
            return capture(rx,a.output/name,dict(manifest,expected_peer=peer),seconds=.08,maximum=maximum)
    r=run('duplicates',[valid]*3)
    assert r['status']=='one-distinct-valid-record' and r['duplicates']==2 and r['stop_reason']=='deadline';checks+=1
    r=run('conflict',[b'bad',valid,valid,raw[772:1544]],maximum=4)
    assert r['status']=='conflicting-valid-records' and r['duplicates']==1 and r['stop_reason']=='packet-limit';checks+=1
    assert [x['status'] for x in r['observations']]==['rejected','first-valid','duplicate','conflicting-valid'];checks+=1
    r=run('silent',[])
    assert r['status']=='no-valid-packet' and r['observations']==[];checks+=1
    r=run('unexpected-peer',[valid],maximum=1,peer='127.0.0.2')
    assert r['status']=='no-valid-packet' and r['observations'][0]['reason']=='unexpected source IP';checks+=1
    r=run('oversize',[b'x'*5000],maximum=1)
    assert r['observations'][0]['bytes']==5000 and r['observations'][0]['saved_bytes']==4096
    assert (a.output/'oversize/packet-000.bin').stat().st_size==4096;checks+=1
    r=run('wrong-identity',[valid[:16]+b'0'*16+valid[32:]],maximum=1)
    assert r['status']=='no-valid-packet' and r['observations'][0]['reason']=='unexpected attempt/build';checks+=1
    with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
        try: capture(sock,a.output/'duplicates',manifest,.01)
        except FileExistsError: checks+=1
        else: raise AssertionError('overwrote closed capture')
        for seconds,maximum in ((0,64),(181,64),(.01,0),(.01,129)):
            try: capture(sock,a.output/'inadmissible',manifest,seconds,maximum)
            except ValueError: checks+=1
            else: raise AssertionError('unbounded capture accepted')
        assert not (a.output/'inadmissible').exists()
    result=dict(status='pass',checks=checks,synthetic_records=64,loopback_captures=6,
                physical_access=False,broadcast_network_path_tested=False)
    (a.output/'tests.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
