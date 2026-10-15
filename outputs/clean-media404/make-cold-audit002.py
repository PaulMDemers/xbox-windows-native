"""Preserve failed typed auditor; resume its completed extraction without rerun."""
import hashlib, json
from pathlib import Path
K = Path(__file__).resolve().parent
p = K / 'cold-audit001.py'; text = p.read_text()
start = text.index('    assert not target.exists()')
end = text.index('    paths = ', start)
old = text[start:end]
fresh = old.replace('    assert not target.exists()\n', '')
# A resumed phase3 extraction exists; phase4 uses the ordinary new extraction path.
replacement = '''    resume = args.phase == 3
    disk = P / 'disk.qcow2'
    before = sha(disk)
    assert before == state['disk_sha256']
    raw = target / 'disk.raw'
    extracted = target / 'files'
    if resume:
        assert target.exists() and raw.is_file() and extracted.is_dir()
        space = {'scope': 'Reused completed001 read-only conversion/extraction; no duplicate conversion'}
        check_data = json.loads((target / 'qcow-check.json').read_text())
        with raw.open('rb') as f:
            mbr = f.read(512)
        partitions = []
        for i in range(4):
            e = mbr[446 + 16*i:462 + 16*i]
            partitions.append(dict(index=i+1, boot=e[0], type=e[4], start_lba=struct.unpack_from('<I', e, 8)[0], sectors=struct.unpack_from('<I', e, 12)[0]))
    else:
'''
replacement += ''.join('    '+line+'\n' for line in fresh.splitlines())
replacement += '        check_data = json.loads(check.stdout)\n'
text = text[:start] + replacement + text[end:]
start = text.index('    hives = []')
end = text.index('    system = ', start)
text = text[:start] + '''    from hive_audit002 import audit
    hives = [audit(path('winnt/system32/config/' + name)) for name in ['system', 'software', 'sam', 'security', 'default']]
''' + text[end:]
text = text.replace('qcow_check=json.loads(check.stdout)', 'qcow_check=check_data')
text = text.replace("scope='Selected-file", "typed_decode_complete=all(h['typed_decode_complete'] for h in hives),\n                  scope='Independent raw hive readers agree; original typed-decoder failure retained. Selected-file")
with (K / 'cold-audit002.py').open('x') as f:
    f.write(text)
record = dict(failed_auditor_sha256=hashlib.sha256(p.read_bytes()).hexdigest(), phase=3,
              failure='Python Registry UnknownTypeException for SOFTWARE/Microsoft/DRM DataPath type0x404',
              extraction_completed=True, raw_copy_preserved_for_resume=True, guest_relaunch=False,
              correction='Compare every key and raw value/type with independent hivex; keep typed decode failure explicit')
with (K / 'cold-audit001-failure.json').open('x') as f:
    json.dump(record, f, indent=2)
