# Kernel776 NVVCRTC recovery control

Fresh source-only773 cumulative-prefix successor, using775 measured baseline.
New word680808:719 ->479 ->719. Neighbors: display end479,total524,sync start724,
sync end729,valid start0,valid end719,CR13104,CR1948. Newest undo happens first;
all16 masks gate output restoration. No additional encoder/clock/scanout writes.
Readback is diagnostic evidence, not fullmode or Windows1.6 qualification.

Build under the existing build lease with build.py. Run model.py,layout_model.py
and clock_model.py under the exclusive emulator lease, then link_review.py,
layout_link_review.py,main_link_review.py and review_prepare.py. Qualification
receipts are exclusive; do not overwrite or rerun closed attempts. Source and
binary hashes are frozen by review001/sources001 before stage. physical.py uses
private C:/xwn776/connection.json and the existing physical ticket; uniqueE path,
one SITE with20second reply bound, no hook. Collect once with double readback
only after authenticated dashboard return, then audit_collection.py locally.
See NEXT.md for live state. Preserve earlier failed and closed evidence.
