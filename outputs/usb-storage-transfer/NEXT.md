# Resume normal-restart qualification with reliable host closure

The current byte capture distinguishes correct guest submissions from lost
QCOW mappings in the forced-stop harness. Preserve both closed siblings and
the older failures; do not repair or relaunch those images.

1. Carry the verified host-close procedure into future owned emulator harnesses:
   acknowledge HMP stop, request quit, wait for the exact owned process and record
   its exit code. Treat a timeout requiring Kill as a separate forced-stop result.
   Retain the original error/closure evidence, including monitor resets after quit.
2. Diagnose the remaining setup guard using a fresh sibling and the existing
   typed device/SetupAPI evidence. Identify the exact pending installer and UI
   before any intervention. Do not infer installer success from a working service
   or silently dismiss an unidentified dialog. emu002 shows hub description and
   ConfigFlags changes, but does not by itself locate the pending install.
3. Require workload completion, an explicit guest normal restart, expected
   shutdown evidence and independent cold verification. Record Ftdisk 49 and
   all new event errors; a clean allocation scan alone is not a strict pass.
4. Separately trace the guest flush path to the ATA/backend boundary if durability
   is the question. Neither current capture observed IDE 0xe7/0xea. Host exit
   flushing cannot substitute for a demonstrated guest flush contract.
5. If a producer defect remains under normal closure, investigate the changing
   outstanding buffers with ownership/lifetime evidence. Current changed ranges
   are outside the eight selected targets and do not justify a driver patch.

No additional emulator run, physical deployment or device integration is included
in this completed capture experiment. The physical baseline remains unchanged.
