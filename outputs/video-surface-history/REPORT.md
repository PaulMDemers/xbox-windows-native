# A prelaunch depth-buffer watch persists into Windows

The lifecycle trace identifies the callback-producing surface as a 640Ã—480 linear
**depth (ZETA) surface**, created before the Windows launch request. Its pitch is
1,280 bytes and its recorded transfer format is two bytes per pixel. The pinned
size calculation gives 614,400 bytes, covering `[0x03c64000, 0x03cfa000)`.

That extent exactly predicts the observed addresses in all three selected uploads:
zero callbacks for the two top rectangles, and 17,280 callbacks for the lower
rectangleâ€”192 four-byte writes on each framebuffer row from 160 through 249.
The remaining six rows of that rectangle fall outside the surface. There are no
source-read callbacks or unrelated callback addresses in the selected windows.

The surface is uploaded before the launch request, downloaded once during the
handoff interval, and never invalidated or recreated before the last captured
callback. No GPU upload/download event occurs during any of the three selected
Windows uploads. This establishes a retained watch around already-downloaded data,
rather than evidence of a GPU download per store. It does not measure lock/wait
duration or prove the precise point at which a safe watch-removal handshake can run.

## Evidence and boundaries

The owned xemu instance starts with seven sparse surface lifecycle events enabled.
Actual HMP state checks verify them before launch. Both CPU-access events remain
off except during the same fifteen upload windows used by the preceding diagnostic.
They are disabled before debugger memory reads. All lifecycle and CPU tracing ends
at the final marker; breakpoint teardown and guest resume are verified.

The single launch request was accepted at 07:02:12.045133 UTC on October 8, 2026.
The before-request and after-reply log positions are both byte 49,692. The target
surface's creation ends at byte 48,625, and its initial upload ends at 48,723. Its
download occupies bytes 49,692â€“49,792. The first Windows marker is at 50,192, and
the last marker at 914,192. Thus creation is unambiguously prelaunch, and the
download precedes the measured Windows copies. Exact guest ownership of the
handoff download is not established by these surface events alone.

The trace contains 489 lifecycle events and 17,280 selected CPU-write events in
914,192 total captured log bytes. The lifecycle verifier reparses the raw private
log, checks its prefix against the closed original log, reconstructs creation and
invalidation history, and independently predicts callback addresses from captured
guest page mappings. The raw `ln`/`lin` layout spelling difference is normalized
explicitly from pinned source; raw event text remains preserved.

Three surfaces have recorded creations with no later invalidation by the final
marker: the target depth surface and color surfaces at 0x03d04000 and 0x03e30000.
The selected rectangles exercise only the depth surface. This run makes no claim
about callback density elsewhere in the framebuffer.

## Identity and validation

Exact probe141, RAM0112 display and xemu-resource-model binaries are reused. No
guest driver, cache setting, service, device policy or emulator binary changed.
Actual copy operands, code and row mappings are captured through 24 guest events
and 15 resident pins. The display header's prior E14 limitation remains explicit;
loader identity, relocated resident code and cold payload hash corroborate it.

Final diagnostic and strict cold qualification **PASS**. All 45 cases,
13,271,040 compared pixels, 45 exact reference files and 45 observed RGB files pass.
The workload issued 82,688 measured BitBlt calls. Full allocation is consistent:
327 directories, 6,851 files and 328 directory clusters, with no errors or orphans.
Five registry hives parse; protected binaries, startup, configuration and the
96 MiB/1,536-cluster pagefile remain correct. There is one normal shutdown and no
new warning/error or application events. All three independent trace verifiers pass.

Ordinary, timing and physical qualification remain FALSE for this debugger run.
The guest returned at 07:06:54.341653 UTC; owned cleanup completed at
07:06:54.7622841 UTC. Capture/teardown ended at 07:03:04.590322 UTC. Preparation
25086, backend check 99123, runner 95963, tracer 36355, supervisor 7188, cold audit
72149 and verifier 94513 are CLOSED. No next fixture or running session exists.
Physical 0101/video0093, 0088 rollback and immutable 0.1.0 remain untouched.

Host tests cover seven lifecycle event formats, a known extent/lifetime case and
six rejected corruptions, plus the inherited graphics oracle/protocol checks,
surface parser tests and mapping/window teardown corruption gates.

An initial host-kit name collided with an older ignored historical directory.
The no-overwrite assertion stopped at its existing audit.py before any fixture or
guest action. Only files newly created in that attempt were moved/removed with
explicit paths and hash verification; historical contents were preserved. The
actual new kit and single guest attempt are `video-surface-history/candidate001`.

## Next change

`OPTIMIZATION-DESIGN.md` describes the missing synchronization proof: repeated CPU
writes should avoid full callback work once CPU data is authoritative, while GPU
reuse must re-establish correct watching and data transfer. Existing asynchronous
watch removal, page-translation invalidation, renderer context and PGRAPH locking
must be respected. The existing non-TCG dirty-bitmap path is a source reference,
not permission to disable TCG callbacks or select a different policy blindly.

No optimization is implemented or qualified here. A small GPU/CPU synchronization
workload is the next useful discriminator before a candidate patch and matched
ordinary performance regression. This emulator issue remains distinct from the
physical console's window-drawing performance.
