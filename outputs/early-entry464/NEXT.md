# Next implementation

Implement and host-test a new bounded observation adapter and its exact insertion
site under DESIGN.md. Do not call the existing unbounded LED helper at entry or
add a PUSH/CALL before the stack is established. Preserve all original source
pins; use a new source/build attempt and independently verify relocated branches,
copy spans and restored registers/flags. The current review authorizes no marker
as safe by itself and does not attribute the intermittent boot cause.

After actual code tests, run one fresh owned emulator qualification before a
physical marker attempt. Keep the original launcher and720p setup intact. No
physical attempt is currently queued; no additional human action is needed yet.
