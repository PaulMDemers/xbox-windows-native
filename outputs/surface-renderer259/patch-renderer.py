"""Compile259 internal stage routine; deliberately add no command or caller."""
from pathlib import Path
def apply(s):
    k=Path(__file__).resolve().parent
    h=s/'hw/xbox/nv2a/pgraph/gl/renderer.h';text=h.read_text()
    assert text.endswith('#endif\n') and 'pattern259' not in text
    text=text[:-len('#endif\n')]+(k/'admission.h').read_text()+'\n'+(k/'renderer-api.h').read_text()+'\n#endif\n'
    h.write_text(text)
    p=s/'hw/xbox/nv2a/pgraph/gl/surface.c';text=p.read_text();assert 'pattern259' not in text
    core=(k/'admission.c').read_text();assert core.startswith('#include "admission.h"\n')
    p.write_text(text+'\n'+core.split('\n',1)[1]+'\n'+(k/'renderer-stage.c').read_text())
