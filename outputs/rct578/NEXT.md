# Next: planned two-boot save/reload control

578 is CLOSED. Physical576 remains independently active; follow engineering
continuation and576/NEXT002.md before console work. No competing console launch.

Prepare a fresh immutable404-based PC experiment with two planned boots, whose
overall lifecycle stays open through the second boot. First boot saves a uniquely
named park in its owned game Saved Games directory, then requests normal restart.
Cold audit must pin the exact save and establish clean shutdown before the second
boot loads that same save and independently verifies the park/camera/pause state.
Do not use any CLOSED runtime as the new parent or silently create another save.

Use observed Save Game #32770 and filename Edit ID1148 with owned-PID/visibility/
enabled/control-class checks. Use bounded text message readback to verify the
full unique path before submitting Save; GetWindowText enumeration was empty.
Refuse an existing target. Preserve a mismatch, modal warning or timeout; cancel
and restore configuration when possible. Qualify the Load dialog separately.
Do not assert reload from file existence or button submission alone.

Project disk/ISO/log growth against20GiB free, includingWSL backingC. A new fixture
has not been admitted. Verified private retail media may be reused as a read-only
asset; its closed guest disk may not. Keep game assets/screenshots/hives private.
Actual runtime API tracing and fixed-scene cost measurements follow persistence.
