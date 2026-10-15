import hashlib, json
from pathlib import Path
K = Path(__file__).resolve().parent
s = (K / 'hive_audit002.py').read_text()
s = s.replace('import hivex', 'import hivex\nfrom raw_value004 import stored_value')
s = s.replace('            raw = v.raw_data()', "            stored_type, raw = stored_value(data, v._vkrecord.offset())\n            assert stored_type == v.value_type()")
with (K / 'hive_audit004.py').open('x') as f:
    f.write(s)
s = (K / 'cold-audit002.py').read_text().replace('from hive_audit002 import audit', 'from hive_audit004 import audit')
with (K / 'cold-audit004.py').open('x') as f:
    f.write(s)
with (K / 'cold-audit002-failure.json').open('x') as f:
    json.dump(dict(failed_source_sha256=hashlib.sha256((K / 'hive_audit002.py').read_bytes()).hexdigest(),
        failure='Python Registry raw_data interprets inline strings as four bytes and inline MULTI_SZ as empty; hivex returns declared lengths',
        phase3_extraction_reused=True, no_reextraction=True,
        correction='Read declared VK lengths with cell bounds; compare every raw value/type against independent hivex; retain unknown typed DRM value'), f, indent=2)
with (K / 'hive-comparison003-failure.json').open('x') as f:
    json.dump(dict(failure='Diagnostic printed SYSTEM/SOFTWARE differences, then requested lower-case sam on case-sensitive extracted filesystem; no output summary created',
                   no_guest_operation=True, original_source_preserved=True), f, indent=2)
