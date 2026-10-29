# Native CR10 vertical-sync-start low-byte diagnostic - Test789

Fresh source-only extension of native787 and kernel788. Closed runtimes are not
inputs. The added register operation is CR10 D4 -> E9 -> D4 after CR07 becomes74;
CR10 restores before CR07. Eight adjacent CRTC bytes are checked. Final success
requires all22 recovery masks clear; any mismatch inhibits output restoration.

The payload grew to17240bytes. Its reserve is18432bytes within the same32768byte
owned allocation. Layout: payload1000..5800, request5800..583C, result5840..5FE8,
24byte result guard, IDT6000..6800, stack6800..8000. Addresses are offsets in hex.
No complete mode switch, Windows1.6 or acceleration capability is established.

Active build sources include main004.c and layout004.c. build007.py copies them
as main.c/layout.c into the fresh build directory. The earlier same-named kit
files are retained rejected frontend sources: global size substitution altered
unrelated64MiB eligibility and firmware reservation constants. See
frontend-review-correction001.json. Do not build the kit directly with make.

Active qualification order (fresh unique outputs and leases required):
payload_build005.py, model.py, host_build005.py (host003), cpu002.py build/run
(cpu-build002/cpu-run002), integration007.py (integration005), optical_review002.py,
link_review008.py, build007.py, page_review004.py, page_boundary005.py,
plan_review003.py, linked_review004.py, source_review002.py, review_prepare002.py.
physical004.py is the active stage/launch/collect controller. It uses private
configuration, unique E paths, exact readback, one20secondSITE reply bound and
no launch retry. Qualification completed: review001.json is PASS. Physical staging and launch are pending.

Preserve preparation-failure001/002/003 and failed integration004. failed-layout001
contains exact initial host002 source snapshots only; none is an admitted build
or runtime parent. Initial cpu-build001 fixtures were never run. The refreshed
bridge fixes a stale request+4 offset. relocate004 extends the checking helper
with the new18KiB bound; the real page builder is checked independently. Fresh
page harnesses keep their relocation recipe outside the enlarged payload.

The thirteen-row report uses white1/black0, MSBleft, on gray. Eight masks are
shown; fourteen are aggregate-only. Same-value CR02/NVVVALIDSTART write drops
remain indistinguishable. Host instruction/device models and diskless CPU tests
cannot establish physical register or output behavior. The physical probe holds
for a photo and manual reset. Native results are optical; persisted files stop
before the handoff. No startuphook or ordinary Windows launcher modification.

Validation:614direct cases,604full-path cases,76optical cases,12CPUfixtures closed;
131379hostownership,32+33compiledpage cases,372compiledownership cases.
Maximum modeled stack writes100bytes of6144; hardware behavior remains untested.
restore_reports.py verifies/reconstructs exact public text chunks for model001.
