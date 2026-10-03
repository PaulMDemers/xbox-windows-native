"""Capture only the explicitly selected task monitor; no process/window discovery."""
import argparse,pathlib,sys,socket,json,hashlib,time,re,msvcrt
kit=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(kit.parents[1]/'work/python-packages'))
from PIL import Image

def command(port,text):
    def receive(sock):
        data=bytearray()
        while not data.endswith(b'(qemu) '):
            block=sock.recv(65536)
            if not block: raise RuntimeError('Monitor disconnected')
            data.extend(block)
        return data.decode('utf-8','replace')
    with socket.create_connection(('127.0.0.1',port),timeout=10) as sock:
        # Full 64 MiB guest dumps can exceed ten seconds under host I/O load.
        sock.settimeout(30 if text.startswith('pmemsave ') else 10)
        receive(sock);sock.sendall((text+'\n').encode());return receive(sock)

def acquire_monitor_lock(port):
    lock_path=kit.parents[1]/'work'/f'monitor-{port}.lock'
    lock=open(lock_path,'a+b');lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0)
    deadline=time.monotonic()+45
    while True:
        try:msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1);break
        except OSError:
            if time.monotonic()>=deadline:raise RuntimeError('Task monitor lock is busy')
            time.sleep(.1)
    return lock

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--port',required=True,type=int)
    parser.add_argument('--output',type=pathlib.Path);parser.add_argument('--command')
    parser.add_argument('--address',type=lambda value:int(value,0),default=0x03c00000)
    parser.add_argument('--auto-framebuffer',action='store_true')
    args=parser.parse_args()
    # HMP accepts one connection at a time; serialize entire pause/capture/resume
    # transactions, including manual commands, across our task's processes.
    lock=acquire_monitor_lock(args.port)
    if args.command: print(command(args.port,args.command).split('\n',1)[-1])
    elif args.output:
        output=args.output.resolve();output.parent.mkdir(parents=True,exist_ok=True)
        raw=output.with_suffix('.raw')
        was_running = 'VM status: running' in command(args.port,'info status')
        command(args.port,'stop')
        try:
            registers=command(args.port,'info registers')
            if args.auto_framebuffer:
                reply=command(args.port,'xp /1wx 0xfd600800')
                matches=re.findall(r'fd600800:\s+0x([0-9a-fA-F]+)',reply)
                if not matches:raise RuntimeError('Could not read NV2A framebuffer address')
                args.address=int(matches[-1],16)&0x0fffffff
            if not 0 <= args.address <= 64*1024*1024-1228800:raise ValueError('Framebuffer outside 64 MiB RAM')
            command(args.port,f'pmemsave {hex(args.address)} 1228800 {json.dumps(raw.as_posix())}')
            data=raw.read_bytes()
            if len(data)!=1228800:raise RuntimeError('Incomplete framebuffer dump')
            Image.frombytes('RGB',(640,480),data,'raw','BGRX').save(output)
            output.with_suffix('.json').write_text(json.dumps({'method':'guest-memory','address':hex(args.address),'width':640,'height':480,'raw_sha256':hashlib.sha256(data).hexdigest(),'registers':registers},indent=2)+'\n')
        finally:
            if was_running: command(args.port,'cont')
        raw.unlink()
        print(output)
    else:parser.error('Specify --output or --command')
