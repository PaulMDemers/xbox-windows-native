"""Verify opt-in diagnostics leave the normal HAL code/imports intact."""
import pathlib, sys, json, hashlib
k = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(k.parents[1] / 'work/python-packages'))
import pefile
old = k / 'package/E/Applications/XWNFBoot/loader/halxboxnt5.dll'
new = k / 'artifacts/halxboxnt5-framebuffer-off.dll'
a, b = pefile.PE(str(old)), pefile.PE(str(new))
def code(pe):
    return next(s.get_data() for s in pe.sections if s.Name.rstrip(b'\0') == b'.text')
def imports(pe):
    return [(lib.dll, [i.name for i in lib.imports]) for lib in pe.DIRECTORY_ENTRY_IMPORT]
original, rebuilt = code(a), bytearray(code(b))
# UNIMPLEMENTED_DBGBREAK embeds __LINE__. The opt-in block moves three existing
# debug messages by 43 source lines even when compiled out. No opcodes change.
line_changes = [(24378, 685, 728), (24442, 696, 739), (24825, 778, 821)]
for offset, before, after in line_changes:
    assert original[offset-4:offset] == rebuilt[offset-4:offset] == b'\xc7\x44\x24\x0c'
    assert int.from_bytes(original[offset:offset+4], 'little') == before
    assert int.from_bytes(rebuilt[offset:offset+4], 'little') == after
    rebuilt[offset:offset+4] = original[offset:offset+4]
assert original == rebuilt
assert imports(a) == imports(b)
r = {'scope': __doc__, 'baseline_sha256': hashlib.sha256(old.read_bytes()).hexdigest(),
     'rebuilt_sha256': hashlib.sha256(new.read_bytes()).hexdigest(),
     'text_identical_except_debug_source_line_numbers': True,
     'debug_line_changes': line_changes, 'imports_identical': True}
(k / 'framebuffer-default-regression.json').write_text(json.dumps(r, indent=2) + '\n')
print(r)

