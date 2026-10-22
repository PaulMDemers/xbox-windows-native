#657 physical attempt closed: no UDP datagrams, dashboard returned

One SITE request was accepted at2026-10-22T20:24:30.401595Z. The owned receiver
ran20:24:17.070238Z through20:26:17.075747Z, covering106.67seconds after the
launch request, and received ZERO datagrams (not merely rejected/invalid packets).
No launch retry or second collection occurred. The user confirmed dashboard
state but did not observe the intervening screen sequence. Exporter execution,
native admission, NIC result and cleanup status are therefore unknown; absence
of packets does not identify which stage failed or prove a network fault.

The user ran the administrator script. firewall-open002 passed exact scoped
rule validation and started cleanup helper24512. run_v2 independently checked
active rule/interface and started receiver43208. The console became reachable;
collection001 completed20:25:16Z. All28 selected files are byte-identical, five
hives parse, event history is preserved, and no new Windows events/6006 exist.
This workload did not intend to run Windows; dashboard return is not a normal
Windows restart. SavedXBOX480 and ordinary720p/startup remain unchanged.

Receiver exited2 for silence. The cleanup helper removed its temporary rule at
20:26:19Z; independent cleanup-verification001 finds no rule or either owned
process. No hook was installed. Native cleanup itself remains unobserved.
reconciliation001 ties the receiver private manifest to the exact staged XBE,
identity and accepted launch. Receiver's launch_sent=false is its own lack of a
launch operation; the controller separately records one accepted request.

Physical657 is CLOSED. Never rerun/recollect it or reuse its token/capture/runtime.
Build and source artifacts remain reusable by pin. No GPU/mode/NIC qualification.
See NEXT.md for a fresh diagnostic that separates exporter entry, admission,
sender and cleanup outcomes before considering any functional change.

## Prepared qualification and preserved failures


The native caller now freezes the original651 display result, state, trace and
pre/post snapshots into652 data and encodes the unchanged655 packet before
calling656's nForce sender. It never continues into Windows. Successful sender
cleanup or rejection before NIC use permits one bounded SMC quick-reset request;
unsafe cleanup holds with its static DMA buffers retained. Reset timeout/error
also holds. No legacy wait_us is introduced into transport/reset.

The original pre-capture/apply/post-capture source prefix is unchanged. This
diagnostic replaces the subsequent LED classifier and Windows/fallback path;
it preserves original result0/error0 instead of substituting fallback error30.
It is an instrumented diagnostic, not a functional display fix or release.
The656 transport result is not part of the frozen655 display packet;
packet receipt alone cannot establish later cleanup/reset success.

Evidence:

- build001: source tree `9f1a69f0e4b22ae9f91db2317777beb120934945`, exact GCC12
  and existing480p flags. Encoder and bridge source bytes unchanged; only packet
  header includes adapted for native freestanding types. Ten original adapter,
  profile and656 module text/rodata comparisons match.
- compiled-wrapper001:78 actual linked i386 cases pass under Unicorn. Display
  apply, register I/O and NIC sender are modeled. Actual capture, bridge, encoder
  and reset instructions execute. Independent Python decode checks every raw
  group; success, noop, errors11/12/13/21/22/23/24, skipped indexed capture,
  sender rejection, safe/unsafe cleanup, frozen/backward/wrapped timer, busy SMC,
  completion timeout and status errors remain distinct. Packet bytes survive
  modeled producer RAM changes after freezing. Every case halts instead of
  returning into Windows if the modeled reset does not take effect.
- review001:23 source/object boundary checks pass. Native657 objects have no
  legacy delay, CR/MTRR/cache/interrupt writes;656's explicit post-capture WBINVD
  remains unchanged. This is not actual DMA/cache/timer/PHY qualification.
- lan001:Windows local limited-broadcast test from the resolved LAN address
  received three matching772-byte packets, including two duplicates. This
  qualifies local socket routing/decoder, not the external firewall/switch path.
- controller-review001: accepted and uncertain SITE outcomes each issue exactly
  one request, use20-second reply bound, preserve the outcome and reject reuse.
- preparation001: dashboard/ordinary720p/startup checked,28 selected files read
  twice and retained privately. stage001: unique owned E application staged and
  read back exactly. No startup hook, ordinary launcher edit or Windows run.

Staged `/E/Applications/XWNExport657/default.xbe`:312816 bytes,
SHA256 `b7c193959640e945355d1b5de7f57d65708e8ae59752065edeffe73e868164d3`.
Private build, configuration, assigned attempt/build tokens and before-files
are under C:/xwn657. They are not public release assets.

Firewall-open001 FAILED: Windows New-NetFirewallRule reported Access is denied;
subsequent rule readback failed. No rule exists from that attempt. The exact
failure receipt remains; it is not permission to bypass host policy. The user
has been asked to run Open-Firewall.ps1 in Administrator PowerShell. This fresh
open002 path scopes UDP50657 to the configured Xbox, Python314 and resolved LAN
interface. An elevated owned cleanup helper removes the single rule on request
or within10minutes; PID/readiness are checked. All three PowerShell scripts
parse, but elevated open/cleanup have NOT executed or been qualified yet.

At this checkpoint: no SITE launch, no active receiver/helper, no temporary hook,
no new Windows evidence. Physical attempt657 is prepared/staged, not closed or
executed. All host build/model instances are closed. Hardware lease retained;
build lease released; automation paused. Ordinary720p, savedXBOX480, releases,
private recovery and historical Ftdisk49/Popup26 limitations remain unchanged.

Orchestrator review: run.py is retained at its preparation pin after a Python314
invalid-escape SyntaxWarning was observed during AST validation; it never ran.
Use run_v2.py, with an explicit raw PowerShell string and a current interface
filter check. Its AST passes with warnings treated as errors. Native build,
controller, preparation and staged bytes are unchanged.
