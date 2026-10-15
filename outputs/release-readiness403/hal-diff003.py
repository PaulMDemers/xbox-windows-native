from pathlib import Path
import struct
x=Path('/mnt/c/xwn403/installed-reference001/payload/E/Applications/XWNEBoot/loader/halxboxnt5.dll').read_bytes();y=Path('/home/paul/xbox-windows-native/release-readiness403-hal-path001/artifacts/halxboxnt5.dll').read_bytes()
for i,(a,b) in enumerate(zip(x,y)):
 if a!=b and 4096<=i<0x7a000:print(hex(i),hex(i-4096+0x11000),x[i-8:i+12].hex(),y[i-8:i+12].hex())
