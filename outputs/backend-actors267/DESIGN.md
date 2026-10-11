# Shader acknowledgments and scoped context references

This is a read-only diagnostic child of the exact265 renderer, using the same
observation-only native265 probe and reboot-held258 driver. The fixture is the
never-executed265 standalone preparation. No completed or failed runtime disk is
used as a parent. Physical audio004/video118/shared158/FATX0101 is untouched.

The actual shader-save and loader thread creation sites invoke a wrapper around
their unchanged work functions. A bounded append-only pool retains 65,536 unique
records until process exit. Records publish created, started and original work
returned states with release/acquire ordering. Owner identity, function identity
and generation never change. The wrapper does not touch the owner after the
returned publication. That publication does not mean the OS thread has exited or
been joined. Pool exhaustion preserves ordinary work but fails the diagnostic;
no record is recycled. Existing ordinary joins and disposal paths are unchanged.

The immutable ledger captures those records while holding the existing shader
cache lock, without joining or waiting for shader work. Pending work remains an
explicit unknown. The loader and every retained save handle must have a record.
Host tests cover concurrent publication, unique generations, saturation and
pending states; actual runtime evidence is required separately.

The SDL backend reports the expected and actual native context/window identities
from each renderer context's owning thread. UI independently records its actual
context/window and the current VGA DisplaySurface identity, texture and size.
VGA metadata is read under its ordinary main-loop lock, without waiting on GL.

GL queries cover the uniform and transform-feedback indexed buffer interfaces
used by the pinned GL4.0 backend. This is not an exhaustive future-extension
inventory. Known render/display FBOs and VAOs are queried in their actual context;
their names can collide between contexts. Reserved but uninstantiated names are
recorded and never bound into existence. Live FBO attachment names, VAO buffer
references and attached program shaders are recorded. Current UI containers are
queried separately. Draw/read FBO and VAO selection are restored on every path,
with before/after values in the report. Existing active-texture restoration and
finite CPU/context acknowledgments remain intact. No object is disposed.

The observer has one immutable request, bounded storage, a ten-second worker
deadline and the inherited failure quarantine. The UI capture has a one-second
bound. The existing frontend close/reopen actors are never reset. A fresh runtime
must complete two actual native attestations, two unchanged exact CPU reads,
the224 workload, normal guest shutdown, orderly host exit and full cold audit.
Independent parsers require complete record coverage and reject state/identity,
attachment and restoration mutations. Ftdisk49 remains a strict failure.

This test does not release the four disabled texture-unit references, revoke UI
holders, stop actors, release guest scanout, alter PTE/cache aliases or grant the
native driver GPU ownership. Those are distinct subsequent decisions.
