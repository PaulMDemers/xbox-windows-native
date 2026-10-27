#719: CR1b observations around setup, without CR1b data writes

718 established saved85, target05/readback05 and restore85/readback05, but did
not sample between the first read and explicit target write. Blanking or unlock
could have changed the readback before that write. Their role is unmeasured.
719 isolates this gap. It preserves the validated kernel/bridge admission and
samples CR1b before setup, after SEQ1 blank, after80d3 blank, afterCR1f57,
after80d3 enable and afterSEQ1 restore. It never writes CR1b data, CR22, geometry,
encoder or clocks. The existing blank/output pair and unlock key remain writes;
"read-only" applies specifically to CR1b. No payload wait, retry or repair.

Green719 requires initial85 and all six samples85 plus sequencer/context checks.
Orange needs a photo:7197 is changed sample,7194 final sequencer/context failure,
7195 CR11 changed after unlock,7192 blank readback mismatch,7191/7196 baseline
refusal. Sample mask bits0..5 indicate completed reads; an unobserved post-start
sample isFFFFFFFF, while uncalled payload fields remainzero. Bridge phase4 and
checkpoint5 mean return, not refusal. No final pitch reread and no mode promotion.

Optical schema:7190000d, bridge phase/checkpoint/return, payload phase/error,
six CR1b samples and mask. Same13x32-bit gray panel; independent whole-image
oracle. Result212bytes stays inside owned256-byte slot. Payload5100 padded9916,
16 relocations/four absolute; bridge end558. Kernel forward namespace transform
exact. Dead legacy pixel bound changed718->719 with namespace, but legacy drawing
is unreachable and model checks forbid entering its helpers.

Fresh checks:190 instruction models,76 isolated optical cases,12 diskless CPU
cases (all closed),23 nxdk page and372 ownership cases,131379 host ownership cases.
These check control flow/ownership/report pixels, not physical bit7 semantics.
First payload build failed unused wait719 (-Werror); preserved under
failed-payload001 and private payload001. Removed unused include, built fresh
payload002. Review reverse-namespace comparison failed on legitimate719 height;
forward source transform passed. The subsequent stage preflight failed before
FTP because review was absent. Both failures retained; no hardware launch then.

Primary source review remains inconclusive on NV2A CR1b bit7. Linux v6.12
nouveau/dispnv04/hw.c saves/restores FIFO control; hw.h distinguishes base, shadow
and extended locks; envytools PCRTC documentation lists no CR1b bit7 meaning.
See source-review001.json for exact URLs and limits. No claim read-only/status,
no bit7 mask, no assignment of718 values to717, no708/709 root-cause claim.
