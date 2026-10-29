# Native CR07 vertical-total overflow preservation — Test791

Fresh source-only derivative of closed native789 and kernel790. Adds the second
CR07 write after CR10, preserving all other bits: `(before & DE) | 20 | 0` from
pinned704 crtcvtotal524. Expected74 ->74 ->74. An unchanged readback cannot
distinguish a dropped same-value write or undo. Eight adjacent CRTC bytes are
checked; this CR07 operation restores before CR10 and the earlier CR07 operation.
Final success requires all23 recovery masks clear. Failed recovery inhibits output.
No CR06, CR16 or later mode operation is included.

The payload is18456bytes, padded to19456 within the same32768byte owned allocation.
Offsets(hex): payload1000..5C00, request5C00..5C3C, request guard5C3C..5C40,
result5C40..6460 (520words), result guard6460..6800 (928bytes), IDT6800..7000,
stack7000..8000 (4096bytes). Full native mode switching and Windows1.6 remain
unproved. The probe holds for a photo and manual power-cycle; native results are
optical and preparation files end before the handoff. No startup hook is installed.

Build inputs are main004.c/layout004.c, copied as main.c/layout.c by build007.py.
Do not build the kit directly with make. Qualified scripts must use fresh output
directories/receipts and the existing build/emulator resource leases. Sequence:
payload_build005.py; host_build005.py; cpu002.py build; model.py;
integration007.py; optical_review002.py; cpu002.py run; link_review008.py;
build007.py; page_review004.py; page_boundary005.py; plan_review003.py;
linked_review004.py; source_review.py; review_prepare.py.

physical004.py stages, launches and collects via private connection configuration,
unique E paths, exact readback, one SITE request with20second reply bound and no
launch retry. No dashboard C access or ordinary launcher/protected720p change.

Report: thirteen32bit rows, white1/black0, MSBleft on gray. Signature, final status,
eight masks, CR07total before/after/restored. Fifteen other masks are aggregate-only
through final status. Neighbor/CPU/selector raw values are not photographed.
Models establish instruction/bounds behavior under modeled devices, not physical
cache/timing/output semantics. See NEXT.md for actual admission/launch state.

Qualification passed:654 direct,644 complete-path,76 optical,12CPUfixtures closed;
131379hostownership,32+33compiledpage,372compiledownership cases. Maximum modeled
stack write100bytes of4096. Exact ELF/PE/XBE/source review passed; review001.json
is frozen. No791physical launch yet. restore_reports.py reconstructs exact
model001.json from public hashed text chunks; no runtime is reopened.

Physical result CLOSED PASS:photo791 final791, eight displayed masks clear,
CR07total74/74/74; fifteen masks aggregate-only and same-value limitation remains.
User power-cycled; nine fresh preparationreports collected/audited exact.
No normalWindows shutdown/native disk/fullmode proof. Never rerun/recollect/parent
this closedruntime. Read NEXT.md for the fresh source-only next operation.
