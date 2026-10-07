"""Pin the next display prototype's source lead and owned NT5 engine exports."""
import hashlib
import json
import re
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
WS = KIT.parents[1]
sys.path.insert(0, str(WS/'work/python-packages'))
import pefile


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    dest = KIT/'shadow-contract.json'
    assert not dest.exists(), 'Do not overwrite evidence'
    binary = Path('E:/Codex-archive/xbox-windows-native/0.1.0/physical-files/F/winnt/system32/win32k.sys')
    assert sha(binary) == '414cc2568ba7f11fa58490060c947477f44d6218e6c52e01deea1bbe8a364a92'
    pe = pefile.PE(str(binary))
    exports = {s.name.decode(): s.address for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name}
    required = [
        'EngCreateDeviceSurface','EngCreateBitmap','EngAssociateSurface',
        'EngLockSurface','EngUnlockSurface','EngDeleteSurface',
        'EngBitBlt','EngCopyBits','EngTextOut','EngLineTo','EngStrokePath',
        'EngFillPath','EngStrokeAndFillPath','EngPaint','EngStretchBlt',
        'EngStretchBltROP','EngPlgBlt','EngAlphaBlend','EngGradientFill','EngTransparentBlt',
        'EngCreateSemaphore','EngAcquireSemaphore','EngReleaseSemaphore','EngDeleteSemaphore',
        'EngSetPointerShape','EngMovePointer','EngAllocMem','EngFreeMem',
        'EngDeviceIoControl','EngCreatePalette','EngDeletePalette','EngSetLastError',
    ]
    assert all(n in exports for n in required)
    source = Path(r'\\wsl.localhost\Ubuntu\home\paul\xbox-windows-native\build\video-shared-framebuffer-001\source\win32ss\drivers\displays\framebuf')
    files = {p.name: sha(p) for p in sorted(source.iterdir()) if p.is_file()}
    text = '\n'.join(p.read_text() for p in sorted(source.glob('*.c')))
    referenced_eng = sorted(set(re.findall(r'\b(Eng[A-Za-z0-9_]+)\s*\(', text)))
    funcs = re.findall(r'\{INDEX_(Drv\w+),', (source/'enable.c').read_text())
    result = dict(passed=True, scope=__doc__, source_sha256=sha(Path(__file__)),
        source_root=str(source), source_files=files,
        source_tree='53e9aedc58152d03116c00579185000483379837',
        tree_note='Existing reconstruction index tree checked separately; its HEAD is upstream afc0127, not this staged reconstruction. No source edit or new build performed.',
        binary_path=str(binary), binary_sha256=sha(binary),
        needed_engine_exports={n: exports[n] for n in required},
        source_engine_references={n: exports.get(n) for n in referenced_eng},
        existing_drv_table=funcs,
        limits='Static export/source availability only; does not prove calling ABI, semantic behavior, full fallback coverage or an NT5-compatible compiled display driver. Microsoft framebuf is still the tested installed display driver; ReactOS framebuf is only a source lead.')
    dest.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True, needed_exports=len(required), source_files=len(files),
        missing_source_exports=[n for n in referenced_eng if n not in exports])))


if __name__ == '__main__':
    main()
