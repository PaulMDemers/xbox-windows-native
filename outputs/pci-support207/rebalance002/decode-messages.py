"""Resolve observed event IDs through pinned installed NT5 PE message resources."""
import hashlib, json, struct, sys
from pathlib import Path
k = Path(__file__).resolve().parent
sys.path.insert(0, 'C:/Users/Paul/Documents/Codex/2026-10-02/xbox-windows-feasibility/work/python-packages')
import pefile
manifest = json.loads((k / 'providers001.json').read_text())
result = []
for row in manifest['providers']:
    wanted = 1005 if row['source'] == 'Dhcp' else 0xc0050009
    for provider in row['providers']:
        p = k / 'artifacts/providers001' / provider['file']
        assert hashlib.sha256(p.read_bytes()).hexdigest() == provider['sha256']
        pe = pefile.PE(str(p))
        for kind in pe.DIRECTORY_ENTRY_RESOURCE.entries:
            if kind.id != 11: continue
            for name in kind.directory.entries:
                for lang in name.directory.entries:
                    d = lang.data.struct
                    data = pe.get_data(d.OffsetToData, d.Size)
                    for i in range(struct.unpack_from('<I', data)[0]):
                        low, high, off = struct.unpack_from('<III', data, 4 + 12*i)
                        for ident in range(low, high + 1):
                            size, flags = struct.unpack_from('<HH', data, off)
                            assert size >= 4 and off + size <= len(data)
                            if ident == wanted:
                                text = data[off+4:off+size].decode('utf-16le' if flags & 1 else 'cp1252').rstrip('\0\r\n')
                                result.append(dict(source=row['source'], event_id=hex(wanted), provider=provider, language=lang.id, message=text))
                            off += size
assert {r['source'] for r in result} == {'Kbdclass', 'Mouclass', 'Dhcp'}
dest = k / 'messages001.json'
assert not dest.exists()
dest.write_text(json.dumps(dict(scope=__doc__, physical_access=False, messages=result), indent=2) + '\n')
print(json.dumps(result, indent=2))
