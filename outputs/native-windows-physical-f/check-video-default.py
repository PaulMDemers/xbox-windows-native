"""Verify opt-in diagnostics leave the normal miniport code/imports intact."""
import pathlib, sys, json, hashlib
k = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(k.parents[1] / 'work/python-packages'))
import pefile
old = k / 'package/F/winnt/system32/drivers/xboxvnt5.sys'
new = k / 'artifacts/xboxvnt5-normal.sys'
a, b = pefile.PE(str(old)), pefile.PE(str(new))
def code(pe):
    return next(s.get_data() for s in pe.sections if s.Name.rstrip(b'\0') == b'.text')
def imports(pe):
    return [(lib.dll, [i.name for i in lib.imports]) for lib in pe.DIRECTORY_ENTRY_IMPORT]
assert code(a) == code(b)
assert imports(a) == imports(b)
r = {'scope': __doc__, 'baseline_sha256': hashlib.sha256(old.read_bytes()).hexdigest(),
     'rebuilt_sha256': hashlib.sha256(new.read_bytes()).hexdigest(),
     'text_section_identical': True, 'imports_identical': True}
(k / 'video-default-regression.json').write_text(json.dumps(r, indent=2) + '\n')
print(r)
