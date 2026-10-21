"""Independent host BGRA byte construction, without calling the guest helper."""
def oracle(w,h):
 assert (w,h) in [(720,480),(1280,720)]
 out=bytearray(w*h*4)
 for y in range(h):
  for x in range(w):
   i=(y*w+x)*4
   out[i:i+4]=bytes([255]*4) if x in (0,w-1) or y in (0,h-1) else bytes([(x^y)%256,y%256,x%256,255])
 return bytes(out)
