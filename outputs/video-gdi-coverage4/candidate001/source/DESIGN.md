# Full-desktop GDI test-window discriminator

Probe120 ran26 cases with zero RGB mismatches, but eight reference intervals saw
one global CopyBits callback each. Keep that as a strict failure; global counters
do not identify a caller. New121 changes only its own window from a small captioned
window to a1024x576 borderless topmost test window. Same384x256 tested rectangle,
source data, drawing calls, clip requirements, counter gates and unchanged RAM0109.

This is a controlled environment discriminator, not evidence yet that the calls
were background activity. No windows/dialogs are closed, no services/events/device
policy changed. Pending-install checks remain before/after. Counter deltas around
reference drawing must still be zero. Cursor remains1000,550 outside test bounds.
Normal restart and complete cold audit required. No hardware/performance claim.
