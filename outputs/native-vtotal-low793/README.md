# Native CR06 vertical-total low byte — Test793

Fresh source-only derivative of closed native791 and kernel792. Adds the next
operation from pinned704: CR06 receives crtcvtotal524 & FF = 0C, after the second
CR07 write. The saved byte is expected to be EC. Eight adjacent CRTC bytes are
checked. CR06 restores before the second CR07, CR10 and earlier CR07 operations.
Final success requires all24 recovery masks clear; failed recovery inhibits output.
No CR16 or later mode operation is included.

Payload19704bytes is padded to20480 within an owned32768byte allocation. Offsets
(hex): payload1000..6000, request6000..603C, request guard603C..6040,
result6040..68D8 (550words), result guard68D8..7000 (1832bytes), IDT7000..7800,
stack7800..8000 (2048bytes). These enlarged boundaries require independent native
execution, page, allocation, relocation and complete-handoff checks before launch.

Build inputs main004.c/layout004.c are copied as main.c/layout.c by build008.py.
Do not build this kit directly with make. Qualified scripts use fresh output
directories/receipts and the existing build/emulator resource leases. Sequence:
payload_build005.py; host_build005.py; cpu002.py build; model.py;
integration008.py; optical_review002.py; cpu002.py run; link_review008.py;
build008.py; page_review005.py; page_boundary006.py; plan_review003.py;
linked_review004.py; source_review002.py; review_prepare003.py.

physical006.py stages, launches and collects using private connection configuration,
unique E paths, exact readback, one SITE request with a20second reply bound and no
launch retry. No startup hook, dashboard C access, ordinary launcher or protected
720p change. Native execution deliberately holds for a photograph and power-cycle.
Native results are optical; files persisted before handoff are preparation evidence.

Report: thirteen32bit rows, white1/black0, MSBleft on gray. Signature, final status,
eight recovery masks, then CR06 before/after/restored. Sixteen other recovery masks
are aggregate-only through final status. Neighbor/CPU/selector values are not shown
raw. Models establish instruction/bounds behavior under modeled devices, not
physical cache/timing/output semantics, full mode switching or Windows1.6 support.

User workflow: after a legible photo, the user power-cycles without a separate Ready
reply. Authenticate dashboard before one-time collection. Ask for recovery only
if it remains offline. This is manual power-cycle evidence, not Windows shutdown.
See NEXT.md for current qualification and physical state.

Qualification failure retained: integration005 completed680 cases but its internal
600second limit expired before four remaining cases. integration008 changes only
receipt/deadline (900seconds), with a fresh complete run and unchanged payload.
Generator-failure001 also preserves an incorrect replacement assertion, corrected
before any build or launch. Neither failure is relabeled as a pass.

Qualification completed:694 direct native cases,684 complete bridge cases,
76 optical cases,12 closed CPU fixtures,131379 host allocation cases,32+33
compiled page cases and372 compiled allocation cases. Exact ELF/PE/XBE/source
review passed. review003/sources003 freeze the active inputs. restore_model.py
verifies/reconstructs exact model001 from hashed public text chunks.

page-review001 is FAILED and retained: the enlarged payload overlapped the old
host harness stack. Fresh page_review005/page-review002 and boundary006 put the
harness stack at20F000, check payload immutability and a lower stack guard, and
pass exact page comparison. Production inputs did not change. Also preserve
qualification-failure001/002, generator-failure001, documentation-failure001 and
link-reference-correction001. No failed receipt is relabeled or overwritten.

Readiness-failure001 occurred beforeFTP: controller005 named a nonexistent plan
receipt. controller006 corrects that exact reference and names a new freeze;
controller-review001 verifies no production or launch-logic change. Prior helper,
review002/sources002 and all earlier qualification evidence remain immutable.
