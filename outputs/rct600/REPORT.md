# PC600: paired API returns and recursive invocations passed

A fresh Windows 2000 PC fixture ran the original subject once uninstrumented
and once under the new debugger recorder. Both subjects passed their own result
assertions. The recorder captured exactly45 matched call/return pairs:

- 25 LoadLibraryA/GetProcAddress pairs across two threads.
- 20 invocations of the dynamically resolved original probe, including recursive
  depth4 and overlapping active calls from the two threads.
- Five expected zero results from missing DLL/name/ordinal lookups.
- Every probe return matched the independent arithmetic formula. Named and
  ordinal lookups returned the same single probe address.

The independent [trace review](trace-review001.json) checks frame IDs, thread,
return address, stack cleanup, returned EAX, exact request counts, recursive
results and closure. Thirteen constructed corrupt traces were rejected by the
[parser tests](oracle-tests001.json). The [shared-code host tests](host-tests001.json)
also passed recursion/thread-sharing/stale-site cases and nine rejection controls.
Those host checks are separate from the observed NT5 debugger run.

Both subject and recorder exited0 without forced termination. Windows requested
a normal restart; the VM exited0 before its bound. The single cold audit found
one new EventLog6006, five clean/header-valid system hives with independent raw
reader agreement, exact four copied tools and unchanged protected OS binaries.
The seed and helper ISO hashes were unchanged. No capture/transport/build failure
was recorded in this attempt. [Final closure](final001.json) pins the evidence.

## Scope and limitations

This is an original synthetic recorder control, not an RCT drawing or performance
result. The game has not yet run with this return recorder. The DLL is deliberately
retained for the whole process. Arbitrary module unload/reload, exceptions,
unwinding, tail calls, output-pointer capture and COM method observation are not
qualified. Address collisions and unresolved frames reject a run; success must
not be inferred from an entry record or from an unpaired return. No FPS, CPU-cost,
GPU or Xbox capability claim follows from this control.

The inherited preparation script's stdout says “planned second boot”; that label
is stale. PC600 was one fresh boot containing two fresh subject processes, followed
by one normal restart and closure. It must never be reopened or used as a parent.

## Reproduction and provenance

The pinned RosBE compiler builds `fixture.c`, `subject.c`, `trace.c` with shared
`calls.h`, and `runner002.c` through `build001.py`. `binary_review001.py` checks
the PE/NT5 contracts and actual seed DLL exports. `host_test001.py` runs the shared
pairing code under the host compiler; `oracle_tests001.py` independently checks
the trace parser. `media001.py` packages only those four original tools and verifies
every ISO member. The existing build/xemu/UI resource leases cover their respective
operations. See the exact build, media, preparation and VM command receipts.

The fixture derives only from immutable404. After the initial cold audit, the
native Windows logon and owned QMP transport copied the tool CD, ejected it, and
launched `C:\xwn600-kit\run600.exe` once. The final cold audit and `close001.py`
validated the persisted results. Credentials are resolved privately and are not
part of this source or the public receipts.

## Space and physical state

A fresh dependency inventory excluded backing references before losslessly
archiving the closed570,571,598 leaf disks to `E:\xwn600\archives`. Each archive
was decompressed and SHA/length checked; originals were rehashed immediately
before exact-path removal. About1.65GiB of C: capacity was recovered. These are
evidence archives, not resumable runtimes. [Archive journal](archive001.json).

All owned host processes are closed. The Xbox was untouched, last known at the
dashboard with no owned startup hook. The596 offline SOFTWARE cleanup still
awaits a subsequent Windows boot. Protected720p, saves, ordinary launcher and
both transfer ZIPs remain unchanged. The ZIPs still exclude RCT. Other consoles,
sound, fullscreen, boot intermittency and1080i remain deferred.

Final staging initially rejected documentation CRLF normalization, and the
repository guard caught generated Python bytecode included by force-add. The
documentation bytes were normalized and the cache unstaged before commit.
Those failures remain in staged-review001 and repository-check001; staged-review002
preceded the cache exclusion. Two metadata-writing commands also failed (shell
quoting, then default Windows text decoding); neither affected guest execution
or frozen source bytes. The final review uses exact index bytes and UTF-8 text.
