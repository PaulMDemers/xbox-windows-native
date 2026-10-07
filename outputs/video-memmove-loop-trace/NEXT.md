# Next: framebuffer cache and alias contract

This trace001 is CLOSED and diagnostic PASS; never relaunch/recollect. All owned
sessions closed. Actual first-row loops:23 forward REP MOVSD,1 seven-DWORD scalar.
No driver/hardware change. Old automation PAUSED. Read REPORT.md and verified
raw evidence; ordinary QPC timing remains separate.

Do not repeat another branch trace without a new discriminator. The CPU path
is identified. Before an access-policy or rendering experiment, review the
complete framebuffer reservation, aliases and lifetime across loader/HAL/video.
Reuse evidence: engineering-notes/VIDEO-DIAGNOSTIC-LIFECYCLE.md already records
0094 physical PAT/MTRR and UC endpoint observations, with a strict popup FAILURE
and0093 restoration. video-map-profile/candidate001/mapping.json records0096
emulator UC endpoints and raw MSRs. These do not cover every alias or the current
0093 address space, and must not be relabeled current-run/full qualification.

Next concrete work is a source/manifest inventory of framebuffer aliases and
reservations, followed only where needed by a NEW bounded read-only observation
of current mappings and supported CPU MSRs. Reuse the reviewed0094/0096 MSR
reader rather than inventing a new mechanism. Include large pages, direct RAM
versus GPU aperture aliases, actual PAT/MTRR/CR0 and ownership/teardown; define
what is unobserved. Never write cache-control registers or map a conflicting
cache alias just to compare speed. Runtime mapping coverage must match the claim.

Then choose one justified experiment with unchanged control, exact pixels,
independent scanout checks, ordinary timing and cold/event gates. The earlier
UC aperture/direct-RAM comparison gave no convincing emulator gain; preserve
that negative result. Emulator instruction/MMIO costs may differ from physical
reads and writes. A cached shadow still needs complete drawing/cursor/readback
and upload contracts (see video-copy-profile-visible/SHADOW-DESIGN.md).

Keep128GiB emulator dump-write/recovery closure, original physical111-byte damage
unresolved, all failures, physical0101/video0093,0088rollback and0.1.0. No physical
test is queued.1080i remains a separate display handoff project.
