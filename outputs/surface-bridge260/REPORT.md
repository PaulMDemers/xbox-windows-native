#260: bridge compiled; first live attempt stopped before renderer admission

The opt-in QOM/PFIFO bridge compiled successfully, with all borrowed sources
restored. Renderer001 SHA256 is
`6bf95a6330a07261c206c00b051fc0b0ca17be2f1a3483374cff362712f33d14`
(191,574,604 bytes), at
`E:/Codex-archive/xbox-windows-native/bridge260-build001/xemu-bridge260.exe`.
Only five source files differ from259: NV2A state/QOM, PFIFO, GL renderer and
the callback-owner classifier appended to surface.c. There is now an actual
bounded worker caller for259's stage routine. This is compilation evidence.

The exact callback-comparison code used in the bridge passed4,622 ASan/UBSan
checks, including256 callbacks, permutations and unrelated-tuple changes.
The corrected attestor passed26 complete synthetic process/module/handle/page
layouts and negative cases. Earlier24 decoder checks and the overly restrictive
FILE_READ_DATA requirement remain preserved under prior-attestation001. The
actual probe requests GENERIC_WRITE. Host tests are not live callback coverage.

## Attempts

- emu001: projected C reserve refused at20:31:05UTC, before runner-start, xemu
  instance or Windows launch. Closed; no collection required and never reused.
- emu002: new immutable-input/run identity. Windows launch accepted at
  20:33:54.204885UTC. At20:34:54.227221 the CPU was at CPL3, EIP160012e5,
  the expected checkpoint lead, with CR3=039c1000 and IDTR828cb400/07ff.
  Actual kernel-header read at the historical lead823df000 returned GDB E14.
  This does not establish the actual kernel base or why that mapping was absent.
  The complete native/process attestation did not finish. **No frontend close,
  bridge stage request, GL test operation or pixel-preservation proof occurred.**
  Breakpoint removed, physical mode0 verified, guest not resumed, owned emulator
  quit and closed. Cold audit completed20:35:32.572329UTC; never replay/recollect.

The deliberately interrupted second disk fails integrity:322 directories,
6,726 files,323 directory clusters,13 orphans and four allocation errors in WBEM
repository chains. There is no normal shutdown and the new result.log was not
present in the cold filesystem. Preserve this failure; do not label the disk
healthy, repair it or use it as a parent. It is not evidence of a renderer change
corrupting storage: no new renderer operation was requested. The interruption
also prevents ordinary qualification. The inherited Ft49 strict event gate is
unchanged; a known baseline event never waives this attempt's failures.

The002 review completed its checks but its manifest-writer used an incorrect
parent filename; source/result retained. complete-freeze002.py created only the
missing manifest using the actual immutable258 parent. All1,778 frozen inputs
must remain unchanged.

## Capacity and baseline

Closed258 and228–230 portable executable/shader copies were hash-verified on E:
with original paths retained through junctions. No disk/backing-chain relocation.
The attempted246–250 offload refused immediately because246 was already a
junction; no source was removed. Manifests are in task-storage-offload. The
20GiB projected build/run reserve was preserved throughout.

Physical audio004/softwarevideo118/shared158/FATX0101, recovery256,0088 and
immutable0.1.0 are unchanged. No physical access or new test was queued. Historical
250/258 emulator policies are explicitly inherited, including synthetic null/
unsupported-device handling; this fixture is not the audio-integrated physical
demo. All owned260 sessions are closed.

Next: derive kernel identity from actual stopped IDTR and two independently
matched trap vectors, pin the PE and resident instructions, and log failed read
addresses. kernel-discovery.py has10 synthetic checks but was not used live.
Only a NEW fresh attempt with completed attestation may request the renderer.

No GL/callback/pixel-preservation, native GPU ownership, speedup or new physical
qualification is claimed by260.
