"""Receiver preflight/readiness contract. No physical launch capability.

Validate before socket creation/readiness. The controller must recheck the
owned child at the final boundary before its one-shot SITE request. A live
process is still not a delivery guarantee or an atomic process/launch lock.
"""
import importlib.util,json,os,socket
from pathlib import Path
K=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('receiver655',K.parent/'udp655/receiver.py')
rx=importlib.util.module_from_spec(spec);spec.loader.exec_module(rx)

def preflight(config,attempt,build_id,candidate_sha256):
    # Preserve existing strict fixture vocabulary; never translate unknown input.
    rx.validate_manifest(config)
    if config['fixture']!='physical-candidate':raise ValueError('physical manifest required')
    if (config['attempt'],config['build_id'],config['candidate_sha256'])!=(attempt,build_id,candidate_sha256):
        raise ValueError('candidate identity mismatch')
    port=config['port']
    if type(port) is not int or not 1024<=port<=65535:raise ValueError('invalid diagnostic port')
    return port

def receive(config,attempt,build_id,candidate_sha256,ready,output,seconds=180,socket_factory=socket.socket):
    port=preflight(config,attempt,build_id,candidate_sha256)
    ready=Path(ready);output=Path(output)
    if ready.exists() or output.exists():raise FileExistsError('owned receiver paths already used')
    if not 0<seconds<=180:raise ValueError('invalid capture bound')
    with socket_factory(socket.AF_INET,socket.SOCK_DGRAM) as sock:
        if hasattr(socket,'SO_EXCLUSIVEADDRUSE'):
            sock.setsockopt(socket.SOL_SOCKET,socket.SO_EXCLUSIVEADDRUSE,1)
        sock.bind(('',port))
        with ready.open('x') as f:
            json.dump(dict(pid=os.getpid(),bound=True,manifest_validated=True,
                           port=port,attempt=attempt,build_id=build_id,
                           candidate_sha256=candidate_sha256),f)
        return rx.capture(sock,output,config,seconds=seconds)

def admit_live_receiver(process,ready,config):
    """Call after slow staging checks, immediately before persisting SITE intent.

    Still subject to child death after poll; preserve that race as a failed
    capture and NEVER retry an accepted/uncertain console request.
    """
    state=json.loads(Path(ready).read_text())
    if not state.get('bound') or not state.get('manifest_validated'):
        raise ValueError('receiver readiness incomplete')
    for name in ['attempt','build_id','candidate_sha256','port']:
        if state.get(name)!=config[name]:raise ValueError('readiness identity mismatch')
    if state.get('pid')!=process.pid:raise ValueError('receiver ownership mismatch')
    if process.poll() is not None:raise RuntimeError('receiver exited before launch')
    return True
