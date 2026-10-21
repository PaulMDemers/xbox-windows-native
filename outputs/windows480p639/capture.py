"""Read-only owned639 framebuffer observation; no input or guest writes."""
import datetime,hashlib,json,re,struct,sys,zlib
from pathlib import Path
K=Path(__file__).resolve().parent;P=Path('C:/xwn639/emu001')
sys.path.insert(0,str(K.parent/'native480p633'));from protocol import monitor
label=sys.argv[1];assert re.fullmatch(r'view[0-9]{3}',label)
out=K/(label+'.json');raw=P/(label+'.bin');png=P/(label+'.png')
assert not out.exists() and not raw.exists() and not png.exists() and not (K/'closure001.json').exists()
r=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Read-only owned emulator MMIO/RAM; expected BGRX interpretation',physical_access=False)
for name,addr in [('start',0xfd600800),('width_end',0xfd680838),('height_end',0xfd680818)]:
 reply=monitor(5698,'xp /1wx '+hex(addr));lines=[v for v in reply.splitlines() if re.match(r'^[0-9a-f]{8,16}:',v)];assert len(lines)==1;r[name]=int(lines[0].split(':')[1].strip(),16)
assert [r[n] for n in ['start','width_end','height_end']]==[0x3700000,719,479]
monitor(5698,'pmemsave 0x3700000 1382400 "'+raw.as_posix()+'"');data=raw.read_bytes();assert len(data)==1382400
rows=[]
for y in range(480):
 line=data[y*2880:(y+1)*2880];rgb=bytearray(2160);rgb[0::3]=line[2::4];rgb[1::3]=line[1::4];rgb[2::3]=line[0::4];rows.append(b'\0'+rgb)
def chunk(t,d):return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
png.write_bytes(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',720,480,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(rows)))+chunk(b'IEND',b''))
r.update(raw_sha256=hashlib.sha256(data).hexdigest(),png_sha256=hashlib.sha256(png.read_bytes()).hexdigest());out.write_text(json.dumps(r,indent=2)+'\n');print('Private capture '+label+' ready')
