# PC604: bounded bitmap-header reader qualified

A fresh original Windows 2000 control passed with and without the recorder.
Their result logs are byte-identical. The observer recorded 123 matched calls
and returns, including 19 independently decoded bitmap-header observations.
This qualifies the scoped reader for further graphics observations, not RCT's
bitmap layout, game performance or Xbox acceleration.

## What was exercised

The shared reader requests at most four bytes followed by forty bytes. Every
ReadProcessMemory call must report complete success. A failed second read retains
only the previously verified size field, discarding any partially copied body.
Null and wrapping addresses are rejected before an unsafe read. No palette,
bitfield mask or pixel payload is read. Derived row stride and extent are policy
checks, not proof that a pixel allocation is present or accessible.

The supported policy is a 40-byte BITMAPINFOHEADER with BI_RGB, one plane,
1/4/8/16/24/32 bits per pixel, positive width and nonzero signed height. Dimensions
are bounded to 16384 and the derived pixel extent to 64 MiB. Zero biSizeImage is
accepted for this RGB layout. Other header sizes, compression and excessive
dimensions, image sizes or palette counts are explicitly rejected rather than
interpreted as supported formats.

| Actual NT5 observation | Result |
| --- | --- |
| Original probe, top-down and bottom-up 8x8x32 headers | Signed heights preserved; stride32, extent256 |
| Null and wrapping pointers | Explicit rejection |
| PAGE_NOACCESS page and a header four bytes before it | Read failure; no invented header body |
| Unsupported size, zero width, minimum signed height, planes, bpp, compression, extent, sizeimage and palette cases | Expected rejection statuses |
| Real invalid CreateDIBSection | Header size0 recorded and API returned failure |
| Two real valid CreateDIBSection calls and one StretchDIBits | Exact 8x8 top-down32-bit RGB header recorded |

Invalid-memory tests call a dedicated original no-dereference probe; those
addresses are never passed to GDI. The original601 graphics core is unchanged:
33 exact BitBlt pixel copies, the StretchDIBits copy, DirectDraw failure/success,
system-memory surface checks and the two-thread recursive arithmetic all passed.
The existing 32-entry BitBlt cap remains explicit; a sampled call is not a frame.

## Independent checks and closure

The exact shared C reader passed nineteen host rejection controls, including
partial-copy corruption, changed header size and address/extent boundaries.
The separate Python decoder passed fifteen expected cases and six malformed
record rejections. The preserved call-pairing host controls passed. Twenty-three
mutations of the actual cached trace were rejected, covering missing/duplicate
headers, wrong pointer, status, length, stride, extent, signed height and bpp,
alongside the existing call/return/interface checks.

The RosBE compiler pin, NT5 imports, frozen sources, unchanged601 core and ISO
member hashes passed. This604 build succeeded on its first build invocation;
the inherited build002 filename does not imply a new604 build001 failure.
The trace executable SHA256 is
`d59f59c51f465e7277d2eda3c017696edb115f1b0e9e5bfc5dba895a5dfe0198`.

One helper launch ran one pristine and one traced subject, both exit0, then
requested restart. The owned VM exited normally at 2026-10-20 04:07:28 UTC.
The subsequent cold audit enumerated6492 files and310 directories, verified
exact copied tools and protected OS binaries, five clean hives with raw-value
agreement, and unchanged seed/audited disk bytes. EventLog6006 increased by one.
Its record number precedes the new startup records, but the independently checked
raw timestamps place shutdown after startup; record order is not time order.
The inherited DRM typed-value decoding limitation remains; raw agreement does
not claim every typed value decoded. This is not a full NTFS allocation audit.

All owned build/VM/cold processes exited. The runtime is CLOSED; do not reopen,
recollect or use it as a parent. No game or Xbox access occurred. Last console
state remains dashboard/no owned hook;596 offline SOFTWARE cleanup remains
cold-only. Launcher, protected720p, saves and transfer ZIPs are unchanged; RCT is
excluded from the ZIPs. Physical Ftdisk49 and shutdown limitations remain.

See review001.json, oracle-tests001.json, event-timestamps001.json and final001.json.
The actual RCT bitmap layout, park-phase coverage, clock checks, observer overhead
and presentation costs remain next work.
