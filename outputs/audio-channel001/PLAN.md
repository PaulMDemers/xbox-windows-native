# Separate channel listening qualification

The user authorized proceeding with dedicated tone and channel verification.
Change only the helper: six three-second phases, each containing two seconds of
low-level tone and one second of silence, plus the retained 350 ms inter-cycle
pause. Masks are left, right, both, left, right, both. Left is 400 Hz and right
600 Hz. Each phase must complete all 144,000 frames before normal reset/close.

Keep the build004 driver and reviewed runner/state/wizard binaries unchanged.
First build with pinned RosBE and test the exact waveform under ASan/UBSan, with
independent capture rejection cases. Then use a new emulator fixture derived
from the closed, genuinely installed audio parent, preserving its bytes/history.
Capture actual emulator PCM and require the correct sequence and silence, driver
state, normal restart and all prior cold integrity gates. Preserve any failure;
never launch a physical case based only on successful helper compilation.

If emulator qualification passes, use a new physical ticket and unique paths,
capture the actual then-current baseline and revalidate it, run the reviewed
installation and new listening helper, collect the user's observation, and
restore/read back the incoming baseline before releasing ownership. Never reuse
closed audio220 or audio-listen001 tickets. Ftdisk49 remains a strict failure;
analog login sound observation does not prove dedicated channel correctness.
