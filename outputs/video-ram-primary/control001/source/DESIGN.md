# RAM-primary0108 correctness prototype

The qualified0107 direct display is the control. Candidate0108 uses an opaque
device primary and a separate, locked engine bitmap in allocated RAM. Fourteen
rendering hooks substitute that bitmap for primary inputs, delegate to the real
Eng implementation, then synchronously upload destination changes to the existing
permanentUC0106 framebuffer mapping. No GPU, cache attribute, PTE, mode, storage,
network, PnP policy or physical-console change is made.

Source-dependent and mask-dependent ROP4 operands are inspected only when the
truth table uses them. All65,536 truth tables have an independent host dependency
check. Uploads intersect visible dimensions and clip bounds, use bounded positive
stride copies and also preserve partial engine drawing when Eng returns failure.
Complex clip/path/text operations conservatively upload the visible clip bounds;
this is a correctness prototype and may be slower than the direct driver.

Allocation/association/lock/device publication failures unwind in reverse order.
The bitmap is unlocked/deleted before freeing its backing memory, then the shared
view is released. AssertMode disables uploads, restores the miniport mode and
uploads RAM on successful enable. No drawing lock is held across reentrant engine
calls. The current one-display GDI serialization assumption needs runtime review
before extending this to concurrent or multiple-device drawing.

DirectDraw is declined so an external writer cannot bypass the private primary.
Software pointer callbacks retain the0107 Eng path; actual callback coverage,
exclusion and cursor correctness are NOT established by host shims. Old Pinball
and OpenGL observations do not qualify this new display path.

Read-only escapes report revision108, geometry,14 saturating callback counts,
upload count/bytes and an RGB comparison of the RAM image and mapped scanout.
No pointers or write commands are exposed. A zero driver self-comparison is useful
but is NOT an independent physical-framebuffer oracle. Primary-source GDI reads
also see RAM and alone cannot establish visible coherence.

The new ordinary pair uses fresh children of the unused immutable shared-UC
fixture. Both authored DLLs and the same new probe are present in both. Only two
bound InstalledDisplayDrivers selectors and the expected-driver marker differ.
The same54 cases/162 pixel stages test copies, overlap, reads and fills at three
sizes. Candidate adds54 self-coherence checks and actual callback counters. Strict
event/allocation/hive/protected-file/pagefile gates remain unchanged. Only callbacks
actually observed are counted as guest coverage.

Before hardware promotion: independent framebuffer oracle, wider rendering and
cursor/mode lifecycle coverage, new sacrificial crash-render test, then meaningful
matched performance measurement. No physical speed or complete DDI-support claim.

Draft001 is preserved: SAL generation left opt_ tokens and declarations outside
the header guard; review corrected both before compilation, plus unused ROP input
handling. Host001 failed because its generator mistakenly changed an earlier
StretchBlt mask assertion when generating StretchBltROP; host002 fixed the shim
and passed46 cases/all65,536 truth tables under ASan/UBSan/leak detection. This was
a harness failure, not guest evidence. Exact host001 source remains in the owned
Linux build directory and host-failure001. Build001 compiled successfully.
