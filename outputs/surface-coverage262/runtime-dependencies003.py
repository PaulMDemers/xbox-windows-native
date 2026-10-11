"""Explicit invoked path inventory: fail before any owned emulator is started."""
import hashlib,json,re
from pathlib import Path
k=Path(__file__).resolve().parent;ws=k.parents[1]
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def inventory():
    local=['Run003.ps1','Invoke003.ps1','run003.py','trace003.py','audit003.py','typed-state003.py','close-host.py','atomic_json.py','attest.py','kernel-discovery.py','common.py','runtime-dependencies003.py']
    prebuild=['monitor_capture.py','launch_unleashx.py']
    kernel=['capture-runtime.py','capture-state.py','launch-network-install.py','exercise-input.py','trace-entry.py']
    paths=[k/n for n in local]+[k.parent/'native-windows-prebuild'/n for n in prebuild]+[k.parent/'native-windows-nt5-kernel'/n for n in kernel]
    integration=Path('C:/Users/Paul/Desktop/ogxbox-linux/scripts')
    paths+=list(integration.glob('*.ps1'))+list((integration/'lib').glob('*.ps1'))
    assert paths and all(p.is_file() for p in paths)
    # Includes conditionally invoked modes as well as the actual ManualCapture path.
    required=set(re.findall(r'[A-Za-z_][A-Za-z0-9_-]+\.(?:ps1|py)',(k/'Invoke003.ps1').read_text()+(k/'Run003.ps1').read_text()))
    assert required<={p.name for p in paths},required-{p.name for p in paths}
    return {str(p.resolve()):sha(p) for p in paths}
if __name__=='__main__':
    manifest=json.loads((k/'host-dependencies003.json').read_text())
    assert inventory()==manifest['files'],'Runtime dependency missing, new or changed'
    print('262 complete invoked host dependency inventory verified')
