# Real GDI coverage with an established visible window

Same26 drawing cases, unchanged RAM0109 and strict pixel/reference/cold/event
requirements. Previous119 isolated failure to stage1: GetClipBox returned valid
COMPLEXREGION3 with bounds0,0,424,285, while the harness required SIMPLEREGION2.
No render operation had started. Recorded last error8 is not a failed GetClipBox
result and cannot establish out-of-memory.

Probe120 uses the already established older GDI workload's bounded SetWindowPos
HWND_TOPMOST/pump/wait procedure before each case. It still requires an actual
simple clip covering the entire384x256 area; never accepts a complex/occluded
region, closes a dialog, suppresses an event or changes a device policy.10-second
bound on uncover; failure is logged and requests normal restart while remaining
unqualified. Rendering algorithms, references, pixel gates and driver unchanged.
