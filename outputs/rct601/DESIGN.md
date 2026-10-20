# Original NT5 graphics and interface recorder control

Fresh immutable404 child; no Xbox or retail game. Repeat600's two-thread recursive
original probe and independent checks, then exercise actual Windows GDI and
DirectDraw APIs in both pristine and traced processes. Each run checks33 exact
8x8x32 BitBlt copies and one StretchDIBits copy after GdiFlush, invalid BitBlt and
CreateDIBSection results, failed DirectDrawCreate for an owned invalid GUID,
successful default creation, an owned hidden window with normal cooperative
level, an8x8 offscreen system-memory surface, its returned descriptor and a fill.
Objects and GDI resources are released; loaded DLL references stay until exit.

The new recorder captures complete stdcall arguments (up to13), paired EAX,
output-pointer values, returned vtables and selected actual methods. Header-based
compile assertions validate descriptor size and vtable offsets. It reads remote
PE image bounds/timestamps, requires executable committed image memory before
setting code breakpoints, and rejects unload of any tracked code range, including
historical return sites. Untracked module unloads are recorded. It never borrows
addresses from the debugger process or writes object data/vtables.

Every graphics/probe entry has a32-call sampling bound. On the next call the entry
is disabled and CAP records the limit; later calls are deliberately unobserved.
Return breakpoints use outstanding-frame reference counts and retire once the
last matching return is observed, so completed sampling does not trap indefinitely
at stale return addresses.600 recursion/thread cases remain in this subject to
exercise this changed lifecycle. Global bounds remain60seconds/4096calls/10000
events,256breakpoint sites/256modules/64threads/32frames per thread.

The first invalid BitBlt is inside the sample;33 subsequent valid calls exceed
the limit. Independent subject pixels verify all33 even though only31 successful
BitBlt entries plus the failed one should be retained. CAP is a lower-bound
observation, never a count of all drawing. This does not measure FPS or overhead.
The fixture's DirectDraw behavior is a PC result, not Xbox acceleration.

Known limits: reject unsupported signature/address aliasing and tracked unloads;
no transparent exception-unwind/tail-call support, no detaching with patched code,
no arbitrary interface version discovery. A failed output read is a failed trace,
not a successful object. A HRESULT failure permits observing its pointer slot but
does not permit following the object. Existing bounds and ordinary shutdown/cold
audit are mandatory. No changes to functional drivers or delivered packages.
