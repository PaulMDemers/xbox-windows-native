"""Independent pixel-coordinate oracle for695; no probe code executed here."""
import struct
COLORS={1:0x00ff00,2:0xff0000,3:0x00ffff,4:0xffff00,5:0xff8000,6:0xff00ff}
def expected_framebuffer(values,result):
 b=bytearray(b'\x20'*3686400)
 def rect(x,y,w,h,color):
  row=struct.pack('<L',color)*w
  for yy in range(y,y+h):b[(yy*1280+x)*4:(yy*1280+x+w)*4]=row
 rect(8,8,1264,72,0x00ff00)
 rect(8,96,1264,64,COLORS[result])
 for r,value in enumerate(values):
  for col in range(32):rect(128+32*col,200+64*r,24,32,0xffffff if value&(1<<(31-col)) else 0)
 return b
