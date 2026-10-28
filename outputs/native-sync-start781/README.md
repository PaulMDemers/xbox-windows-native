# Test781: native vertical-sync-start recovery

Fresh source-only extension of closed Test779's frontend and closed Test780's
kernel-qualified probe. Tests NVVSYNCSTART at 0xfd68080c: own saved724, target489,
then saved724. The target comes from retained704 mode inputs. The preceding
qualified horizontal/vertical prefix remains; later NVVSYNCEND, encoder and clock
operations are not added. No Windows1.6 or complete mode-switch claim.

Native CPU admission requires cache-disabled paging-off context, CR3zero, IFclear,
PAEclear. All18 recovery masks must clear before output-enable. Eight masks and
the sync-start before/after/restored values are displayed in13rows. Ten older
masks and neighbor/CPU/selector details are aggregate-only. Same-value CR02 and
NVVVALIDSTART store effects remain indistinguishable.

The console test deliberately holds for a photo and manual power-cycle. It writes
only preparation records before handoff; native results are optical evidence.
No startup hook. Owned E path; ordinary launcher/protected720p unchanged.

## Preserved preparation failures

- payload002: raw16760 exceeded the14080-byte reserve. ELF.text was0x3210 bytes,
  followed by a4KiB-aligned rodata segment. No stage or launch occurred.
- payload003: fresh link uses max-page-size0x20, retaining32-byte data alignment
  and the same14080-byte reserve. No guest C change. link-review005 independently
  checks normalized instruction bytes, resolved internal relocations, data and
  unwind records against the failed002 build.
- link_review003 and004: reviewer range assumptions rejected a compiler-generated
  cs-minus22 indexed operand. Earlier003 failure note's one-past-end hypothesis
  was superseded by disassembly: mov displacement(esi,esi), esi11..14 accesses
  cs offsets0,2,4,6. Reviewer005 checks that exact instruction/operand/index range.
  Both failed reviewers are preserved; neither executed a runtime or hardware.

## Active qualification path

payload_build003 -> payload003; host_build005 -> host002; cpu002 build/run;
model -> model001; integration005 -> integration004; optical_review002;
build006 -> build002; page_review003/plan_review003/linked_review004;
source_review; review_prepare002 -> review001/sources001. Every result must pass
before physical003 stage/readback and a single20second-bounded SITE launch.
The source generators are historical, not commands to rerun after qualification.

Qualification complete:458 direct payload,448 full-path,76 optical,12 CPU(all closed),32 compiled page and372 ownership cases PASS. Linked executable checks and source review PASS. No physical evidence yet.
