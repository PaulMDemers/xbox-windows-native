# Test760 staged: kernel CR01 display-end and own recovery

Fresh source-only758 extension after native759 closure. The next original
operation writes CR01=(720/8)-1=59. Capture its actual byte immediately before
writing; check CR01 plus CR00/02/03/04/05/17, then undo CR01 before CR17 and
all older recoveries. A new recovery mask inhibits output on failure. No later
CR02/display-enable/pitch/vertical/encoder change is included.

Fresh actual-COFF189 cases,2353 layout cases,10 actual-clock cases and independent
source/schema mutations/link checks pass. Model001's decimal17 versus0x17 harness
error is preserved; model002 fixes the injection target without guest changes.
Two alternate CR01 own-value cases prove the model does not assume a fixed
physical baseline. Model behavior is not physical hardware proof.

176words704bytes are serialized. A future native counterpart would end at53c0
if placed at5100, requiring fresh bounds and explicit optical mapping review.
Clock3375000/high0 guard is unchanged, actual compiled stack offsets verified.
Exact staged source/index/private build and unique E readback pass. XBE SHA256:
d12836761e9a116e6b6b465da3369b45833985dcd335b8dba6d7945f1ef7250c.

No launch yet. Console authenticated dashboard during staging. No startup hook,
native handoff or Windows intended. No owned process/VM remains. All759/prior
runtimes CLOSED. Standing user authorization covers bounded automatic-return
kernel tests; no visual observation will be inferred from an exit or FTP alone.
