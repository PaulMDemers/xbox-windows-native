#350: the6036-byte difference is outside the same-primary fast path

One fresh read-only debugger run resolves349's aggregate coverage question.
Both captured960x540 BitBlt operations generated thirteen CopyBits calls. Eight
were same-primary calls and all executed the fast path. The other five involved
two31x27 system-memory bitmaps with negative124-byte stride; actual XwnOwner
returns rejected their nonprimary source or destination. No driver/probe code
was changed, no fallback admission was broadened and no physical access occurred.

| Actual call scope, per operation | Calls | Bytes |
|---|---:|---:|
| Primary to primary, fast | 8 | 2067564 |
| Bitmap to primary, engine | 3 | 6036 |
| Primary to bitmap, engine | 2 | 2688 |

The eight fast rectangles and three engine output rectangles tile the requested
960x540 destination exactly, without gaps or overlap. The latter6036 bytes
exactly equal349's unexplained difference. The two bitmap destinations are
separate copies and are not double-counted in destination coverage. All thirteen
actual CopyBits calls returned success in each direction. The bitmaps' cursor
purpose was not established; their actual type/ownership proves they are outside
the same-primary optimization regardless of purpose.

This supports a **new eligible-plan-byte contract**, described in NEXT.md. It
does not turn349 or350's original full-requested-fast-byte gate into PASS. That
gate incorrectly used top-level requested bytes as a proxy for only primary
work. No percentage threshold is substituted, no arbitrary bitmap fast path is
proposed and no historical audit is rewritten.

## Runtime evidence and limits

Single launch17:44:49UTC October13, dashboard return17:50:30UTC. Exact348
candidate f5329b0f0d400ce394064ff9626524f25ba64f26e7696ae447d8e1e4f4eac200
and probe60aa2545febe74da772b984e17615b306b6c63db8ecb0d562fd95c4167dafeb5
ran from a fresh child of the never-executed339 seed. Inherited emulator-only
device policy is unchanged and is not physical-console policy.

Two actual kernel IDT gates, loader name/base/size, process identity and171
relocated resident code pins support the trace. Display header GDB E14 is
recorded explicitly; scoped identity instead uses loader identity, actual code
and full cold binary hashes. Calls/returns pair actual thread, process and stack
frame. Destination/source descriptors, rectangles/origins, translation/clip
state and owner returns were captured before dereference lifetimes ended.
171 pins were independently compared with the exact five prepared module files.
549 mutations of actual call/return/geometry evidence were rejected. The host
protocol had563 separate decoder/pairing/bounds/source checks.

Both operations completed under the existing trace bounds, with no unpaired
calls, no breakpoint remaining and explicit virtual-memory mode restoration.
The guest resumed without data/register modification. The full workload then
completed: five drawing samples,150 large pixel checks/75 original intervals,
copy/DIB/text/window checks, six captured audio phases, joined helpers and one
normal shutdown. Orderly host exit0, no fallback kill. Cold341 directories,
6809 files,358 directory clusters,zero errors/orphans; five hives, protected
hashes, startup/policy and SetupAPI/event history passed.189 frozen inputs and
30 private captures were rehashed in final-review.json.

Original combined/strict qualification remains FALSE for primary-byte coverage
and the sole Ftdisk49 HarddiskVolume1 event. No event suppression or gate waiver.
functional-scope001.json separately applies the unchanged344 decoder to the
observed phase projection; it does not replace the original qualification.
Debugger timing cannot qualify ordinary performance. No physical speedup,
release promotion, GPU/cache/mapping change or general bitmap lifetime claim.

## Preserved host failures

- sites001 lacked the engine/API providers needed for return-site pins. sites002
  includes them before launch. The first inline extension failed PowerShell
  parsing without creating a file; extend-sites.py generated the replacement.
- freeze.py assumed gdi32.dll was in the old protected subset and failed with
  KeyError before freeze/launch. provider-preflight.py independently read all
  five actual prepared module files, and freeze002 pinned that evidence.
- Initial trace_analysis.py incorrectly assumed positive bitmap stride and one
  bitmap identity. Actual immutable descriptors show negative stride and two
  identities. The original failed analyzer/receipt remains; analysis002 checks
  those raw fields and bottom-up address relationships. No guest oracle,
  captured bytes or coverage gate changed.

The frozen new preparation script retains the inherited trailing blank line.
Two file-specific whitespace exceptions preserve that executed script and its
patch byte-for-byte; no test gate changes.

All sessions are closed: prepare54049, runner63397, tracer40098,
supervisor24911 and cold audit43641. No hardware queued. Physical E baseline,
normal startup, F rollback, immutable tags and the prohibition on console C
access remain unchanged. No cleanup or backing-chain move was needed.
