# Kernel-context minimal interaction728

Fresh comparator to closed native727. The probe source and54-word structure
are identical after namespace normalization, except the CPU admission accepts
kernel paging and incoming IF. CR0/3/4 are read, never changed. The bounded
transaction saves flags, disables interrupts, then restores the original flags
before any file API. Different compiler/context means timing is not identical.

Sequence: baseline; blank/output gate;6302; unlock1f57; oneCR1b05 write;
direct data read then reselected read; saved6303; output restoration;32 late
pairs; full baseline and selector checks. No other prefix data writes or repair.
Final CR1b05 remains a failed85 baseline check, even if otherwise expected.

The kernel establishes720p before this sequence. A green top bar means728;
orange means cleanup7285 or immediate mismatch7288; red another guard/failure;
magenta means post-call reporting failed. Display lasts15seconds, then automatic
firmware return is requested. This is not a Windows test or shutdown proof.
Seven exclusive E-root reports include the raw result after flags restoration.

Build: run build.py under the existing build lease. Under the emulator lease,
run model.py and layout_model.py. Then link_review.py, layout_link_review.py,
main_link_review.py, review_prepare.py. Frozen source and staged bytes must match.
physical.py stage/launch/collect uses the private connection file, the hardware
ticket, unique owned E paths and a single20second SITE request. No C or hooks.

The actual COFF model tests34 cases including delayed/sticky/reasserted reads,
CPU/context guards, dropped writes, unexpected values and cleanup faults. It
does not prove physical register semantics, caches or timing. Layout2353 cases
and linked instruction-byte checks complement source reporting review.

Initial preparation command had a parse error before execution; retained in
preparation-failure001.json. No candidate build/model failure so far.
