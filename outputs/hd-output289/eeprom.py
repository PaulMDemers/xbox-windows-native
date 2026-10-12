"""Offline HD flags on a NEW emulator-private EEPROM only."""
import hashlib,json,struct,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent
sha=lambda b:hashlib.sha256(b).hexdigest()
def crc(data):
 high=low=0
 for v, in struct.iter_unpack('<I',data):
  high=(((high<<32)|low)+v)>>32
  low=(low+v)&0xffffffff
 return (~(high+low))&0xffffffff
def enable(data):
 assert len(data)==256
 b=bytearray(data)
 assert struct.unpack_from('<I',b,0x60)[0]==crc(b[0x64:0xc0]),'Original checksum invalid'
 old=struct.unpack_from('<I',b,0x94)[0]
 struct.pack_into('<I',b,0x94,old|0xe0000)
 struct.pack_into('<I',b,0x60,crc(b[0x64:0xc0]))
 assert all(a==z or 0x60<=i<0x64 or 0x94<=i<0x98 for i,(a,z) in enumerate(zip(data,b)))
 return bytes(b)
if __name__=='__main__':
 out=Path('E:/xwn289/fixture001');assert not out.exists()
 source=Path('C:/Emulators/xemu/eeprom.bin');a=source.read_bytes();b=enable(a)
 assert a!=b and enable(b)==b
 source_code=subprocess.check_output(['wsl','-d','Ubuntu','--','cat','/home/paul/ogxbox-linux/sources/xemu/hw/xbox/eeprom_generation.c'])
 # Cross-check against an independent end-around-carry total.
 for words in [list(range(23)),[0xffffffff]*23,[0x12345678]*23]:
  data=struct.pack('<23I',*words);total=sum(words)
  assert crc(data)==(~((total>>32)+(total&0xffffffff)))&0xffffffff
 for i in [0x64,0x90,0xbf]:
  bad=bytearray(a);bad[i]^=1
  try:enable(bad)
  except AssertionError:pass
  else:raise AssertionError('Changed checksum accepted')
 out.mkdir();(out/'original.bin').write_bytes(a);(out/'hd.bin').write_bytes(b);(out/'checksum-source.c').write_bytes(source_code)
 r=dict(physical_access=False,source=str(source),source_sha256=sha(a),private_hd_sha256=sha(b),checksum_source_sha256=sha(source_code),changed_offsets=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y],before_flags=struct.unpack_from('<I',a,0x94)[0],after_flags=struct.unpack_from('<I',b,0x94)[0],only_video_flags_and_user_checksum=True,original_source_unchanged=source.read_bytes()==a,synthetic_checksum_cases=3,changed_checksum_refusals=3)
 (k/'eeprom001.json').write_text(json.dumps(r,indent=2)+'\n');print('Private HD EEPROM created and verified; shared source unchanged')
