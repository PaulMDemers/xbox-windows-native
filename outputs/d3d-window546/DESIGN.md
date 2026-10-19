# 546 combined windowed scene

Fresh rung 09c joins the unchanged five scene geometry/state cases with an
owned primary surface, child-window clipper and GDI readback. The 64x64 RGB32
render target is blitted without scaling to the panel origin. Only the child
rectangle [8,56)x[8,56) is visible; a magenta sibling covers [24,48)x[24,48)
in stages 1 and 2. The blue 80x80 panel provides an out-of-clip guard. Stages
2 through 4 move the panel from (64,64) to (144,112). Each stage captures its
black target/GDI baseline, rendered source, screen result and unchanged source
after presentation. Source textures are checked before and after all stages.

Require a 32-bit RGB desktop, normal cooperative mode, exact clip union,
unscaled presentation, zero API failures and complete teardown. The PC-only
runner may temporarily select 32-bit color, logging and restoring the original
mode before normal restart. No display-mode change is permitted on the Xbox.
If the PC driver refuses 32-bit mode, preserve the failure and reassess; do not
waive the format requirement. No physical launch before a qualified PC result.

The independent scene oracle keeps its original coverage bands. Presentation
checks require exact RGB equality to that already-qualified source, including
occluder and guard pixels. Native unused X bytes remain outside pixel claims.
Use metadata and capture mutations to prove malformed output is rejected.

This is software rendering and presentation coverage, not acceleration,
performance, varying-W interpolation or game compatibility. Boot diagnosis
stays tabled. Closed 545/496/492 runtimes are evidence only, never new parents.
Use the immutable original 404 NTFS seed for a fresh PC child.
