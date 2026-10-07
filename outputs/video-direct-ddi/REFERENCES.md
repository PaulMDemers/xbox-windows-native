# DDI reference notes (2026-10-07)

The pinned source headers and actual NT5 binaries are authoritative for this
experiment's ABI. The current Microsoft SURFOBJ page includes additional private
members absent from this pinned ReactOS header. Do not copy its modern layout
into the NT5 module or infer a field offset from the web declaration.

- [DrvEscape](https://learn.microsoft.com/en-us/windows/win32/api/winddi/nf-winddi-drvescape):
  validates the escape number and input/output sizes; read-only identity belongs
  here, drawing does not. Our private code is above Microsoft's reserved range.
- [EngAssociateSurface](https://learn.microsoft.com/en-us/windows/win32/api/winddi/nf-winddi-engassociatesurface):
  associate before returning the primary surface; unhooked standard-bitmap
  drawing uses GDI. Do not reassociate an already returned primary surface.
- [EngSetPointerShape](https://learn.microsoft.com/en-us/windows/win32/api/winddi/nf-winddi-engsetpointershape):
  GDI can manage the software cursor. Actual exclusion/coherence with a future
  RAM primary still needs measured callback coverage.
- [SURFOBJ](https://learn.microsoft.com/en-us/windows/win32/api/winddi/ns-winddi-surfobj):
  useful conceptual surface description; current layout is not NT5 ABI proof.

An exploratory static read found EngAssociateSurface RVA0x1b5ca in the owned
win32k.sys and stores of the HDEV/PDEV into its internal surface. This is only a
lead, not runtime proof that this candidate escape executed. A subsequent lookup
for EngGetDHpdev found no export (StopIteration); no driver or guest changed.
The Linux environment has no rg binary, so header inspection used grep after the
failed rg invocation. These inspection failures do not affect guest results.
