"""Read the actual qualified display binary's upload/copy instructions; no patch."""
import hashlib,json,subprocess
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1];dest=k/'upload-instructions.json';assert not dest.exists()
binary=ws/'outputs/video-clip-upload/candidate001/artifacts/xwnown.dll'
assert hashlib.sha256(binary.read_bytes()).hexdigest()=='ba6e37ddb2bdaad05cc12585fe9c986bdb5203c94101443500ebf1c547c81da8'
path='/mnt/c/'+str(binary)[3:].replace('\\','/')
tool='/home/paul/xbox-windows-native/toolchains/RosBE-2.2.1/i386/bin/i686-w64-mingw32-objdump'
results=[]
for label,args in [('upload',['--start-address=0x127b0','--stop-address=0x12830']),('copy-alias',['--start-address=0x13f10','--stop-address=0x13fe0'])]:
    command=['wsl','-d','Ubuntu','--',tool,'-d',*args,path]
    p=subprocess.run(command,check=True,capture_output=True)
    (k/(label+'-disassembly.txt')).write_bytes(p.stdout)
    results.append(dict(label=label,command=command,stdout_sha256=hashlib.sha256(p.stdout).hexdigest(),stderr=p.stderr.decode('utf-8')))
dest.write_bytes((json.dumps(dict(binary_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),read_only=True,driver_changed=False,results=results,
    observations=['XwnUploadBox calls address13f10 per row; memcpy/memmove symbols alias that address'],
    limits='Static instruction evidence only; no measured per-stage cost or speed qualification'),indent=2)+'\n').encode('utf-8'))
print((k/'copy-alias-disassembly.txt').read_text())
