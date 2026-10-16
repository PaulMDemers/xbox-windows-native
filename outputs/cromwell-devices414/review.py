"""Pin original ELF sections/call boundaries to the deployed embedded payload."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

K = Path(__file__).resolve().parent
P = Path('E:/xwn414')
sha = lambda b: hashlib.sha256(b).hexdigest()


def verify_sections(elf, payload):
    assert elf[:7] == b'\x7fELF\x01\x01\x01'
    h = struct.unpack_from('<16sHHIIIIIHHHHHH', elf)
    assert h[2] == 3 and h[4] == 0x2600000 and h[11] == 40
    sections = [struct.unpack_from('<IIIIIIIIII', elf, h[6]+i*h[11]) for i in range(h[12])]
    s = sections[h[13]]
    names = elf[s[4]:s[4]+s[5]]
    result = []
    cursor = 0
    for s in sections:
        if not s[2] & 2 or s[1] == 8:
            continue
        name = names[s[0]:].split(b'\0')[0].decode('ascii')
        start = s[3]-0x2600000
        assert start == cursor and s[5] > 0
        data = elf[s[4]:s[4]+s[5]]
        assert len(data) == s[5] and data == payload[start:start+s[5]]
        result.append(dict(name=name, address=s[3], bytes=s[5], sha256=sha(data)))
        cursor += s[5]
    assert cursor == len(payload)
    return result


def call_target(payload, address):
    offset = address-0x2600000
    assert 0 <= offset <= len(payload)-5 and payload[offset] == 0xe8
    return address+5+struct.unpack_from('<i', payload, offset+1)[0]


if __name__ == '__main__':
    assert not P.exists() and not (K/'source-review.json').exists()
    P.mkdir()
    elf = Path('E:/xwn374/build001/image-crom.elf').read_bytes()
    payload = Path('E:/xwn374/build001/image-crom.bin').read_bytes()
    xbe = Path('E:/xwn374/build001/default.xbe').read_bytes()
    assert sha(elf) == 'f64c05c1c07797945244b4a8db7fe79256db3a8f0fefac48cc8508b966cc2f0d'
    assert sha(xbe) == '6240a801d97c4894e56d516a934059da056446fb77cf895b5364bdd6cd24be9a'
    assert payload == xbe[0x3000:0x3000+len(payload)]
    sections = verify_sections(elf, payload)
    # Actual direct CALL instructions in BootResetAction, checked against ELF symbols.
    calls = [(0x260071b, 'BootStartUSB'), (0x2600778,'BootIdeInit'), (0x2600801,'BootFromDevice')]
    nm = subprocess.check_output(['wsl','-d','Ubuntu','--','nm','-n','/mnt/e/xwn374/build001/image-crom.elf']).decode()
    symbols = {v[2]:int(v[0],16) for line in nm.splitlines() if len(v:=line.split()) == 3}
    for address, name in calls:
        assert call_target(payload, address) == symbols[name]
    stops = [(0x260071b,'before_usb'), (0x2600720,'after_usb'),
             (0x2600778,'before_ide'), (0x260077d,'after_ide'),
             (0x2600801,'before_boot_device')]
    sources = {}
    root = '/home/paul/xbox-windows-native/build/resolution-e374-build001/source/'
    for name in ['boot/BootStartup.S','boot/BootResetAction.c','drivers/video/BootVgaInitialization.c',
                 'drivers/video/BootVgaInitialization.h','drivers/video/BootVideoHelpers.c','include/memory_layout.h','drivers/video/BootVideo.h','drivers/video/xwn_hd_native.c','drivers/video/xwn_hd_adapter.c','drivers/usb/sys/BootUSB.c','drivers/ide/BootIde.c']:
        data = subprocess.check_output(['wsl','-d','Ubuntu','--','cat',root+name])
        dest = P/'source'/name
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(data)
        sources[name] = sha(data)
    result = dict(passed=True, source_files=sources, elf_sha256=sha(elf),payload_sha256=sha(payload),
                  original_xbe_sha256=sha(xbe), sections=sections, calls=[dict(address=a,target=symbols[n],name=n) for a,n in calls],
                  stops=[dict(address=a,label=n,expected_code=payload[a-0x2600000:a-0x2600000+32].hex()) for a,n in stops],
                  video_mode_address=symbols['vmode'], physical_access=False, runtime_evidence=False)
    (P/'symbols.txt').write_text(nm,encoding='utf-8')
    (K/'source-review.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(passed=True,sections=len(sections),stops=len(stops),sources=len(sources))))
