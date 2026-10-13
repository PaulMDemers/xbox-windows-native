"""Narrow, reversible edit of the exact303 stretch wrappers only."""
from pathlib import Path

def transform(original):
    s = original
    assert '#include "stretch_bounds.h"' not in s
    s = s.replace('#include "row_store.h"', '#include "row_store.h"\n#include "stretch_bounds.h"', 1)
    for name, following in [('XwnStretchBlt', 'XwnStretchBltROP'), ('XwnStretchBltROP', 'XwnPlgBlt')]:
        start = s.index('BOOL APIENTRY ' + name + '(')
        end = s.index('BOOL APIENTRY ' + following + '(', start)
        old = s[start:end]
        new = old.replace(' PPDEV p=NULL; BOOL ok;',
            ' PPDEV p=NULL; BOOL ok; RECTL saved,damage;\n'
            ' BOOL have = prclDest != NULL;\n'
            ' if (have) saved = *prclDest;', 1)
        before = 'if (XwnOwner(psoDest)) XwnUpload(p, NULL, pco);'
        after = ('if (XwnOwner(psoDest)) XwnUpload(p, XWN_STRETCH_BOUNDS ?\n'
                 '     XwnStretchDamage(ok, have ? &saved : NULL, &damage) : NULL, pco);')
        assert new.count(before) == 1
        new = new.replace(before, after)
        assert new != old
        s = s[:start] + new + s[end:]
    return s

def integrate(src, kit):
    target = Path(src) / 'win32ss/drivers/displays/framebuf'
    p = target / 'shadow.c'
    original = p.read_bytes()
    assert b'\r' not in original
    p.write_text(transform(original.decode()))
    (target / 'stretch_bounds.h').write_bytes((Path(kit) / 'stretch_bounds.h').read_bytes())
    p = target / 'CMakeLists.txt'
    s = p.read_text()
    assert 'XWN_STRETCH_BOUNDS' not in s
    p.write_text(s + '\noption(XWN_STRETCH_BOUNDS "Bound successful stretch uploads to destination" OFF)\n'
        'if(XWN_STRETCH_BOUNDS)\n target_compile_definitions(xwnown PRIVATE XWN_STRETCH_BOUNDS=1)\n'
        'else()\n target_compile_definitions(xwnown PRIVATE XWN_STRETCH_BOUNDS=0)\nendif()\n')
