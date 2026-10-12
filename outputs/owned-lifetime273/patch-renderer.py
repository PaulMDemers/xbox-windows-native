"""Observation adapter only, exact269 source parent, no release helper."""
from pathlib import Path
k=Path(__file__).resolve().parent
def apply(root):
    target=root/'hw/xbox/nv2a/pgraph/gl/texture.c'
    old=(k.parent/'unit-reuse269/watch.c').read_text()
    new=(k/'watch.c').read_text()
    wire=(k/'wire.h').read_text().replace('#include "lifetime.h"',(k/'lifetime.h').read_text())
    new=new.replace('#include "wire.h"',wire)
    text=target.read_text();assert text.count(old)==1
    changed=text.replace(old,new);assert changed.replace(new,old)==text
    target.write_text(changed)
