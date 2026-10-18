# Watched physical two-marker trial

User confirmed readiness to watch the front LED and screen. This trial uses
byte-identical466build001, already tested through both emulator checkpoints;
it does not rebuild or install a new ordinary launcher. Its unique physical
directory is E:\Applications\XWNBoot466a. The existing XWNEBoot path, normal
Windows startup, drivers and720p settings are pinned before staging and launch.
Dashboard C is not accessed. Root demo251 ownership must remain valid.

The first marker runs while the original wrapper's kernel stack is valid and
before paging changes. It requests patternff, then manual LED control. A failure
records reason12 through the existing bounded refusal path and returns to the
dashboard. The second marker executes after the original stack install and
requests patterna5. It makes no kernel/file calls. A second-marker failure halts
with interrupts disabled; a watched manual reset is the explicit recovery if it
stays stuck. Never interpret missing reports or unseen colors as checkpoint PASS.

Each marker permits only the two volatile SMC LED commands, one4096-read total
budget and64,000,000TSC ticks. The latter is not calibrated wall time. It waits
for idle, refuses unknown/error status, acknowledges only idle completion, does
not retry/reset the controller, and restores caller registers/flags on success.
The original single-CPU execution disables interrupts only inside the marker.
No EEPROM, disk, GPU ownership or driver operation is added by the marker.

Read back the new XBE and ownership receipt, retain before hives/events/trace,
and issue one SITE request. If Windows appears, retain the LED/screen observation
and collect after a normal Windows restart. If it fails, preserve the first
attempt before any later test. The physical run is not yet qualified by emulator
SMBus behavior. All proprietary captures stay privately on C:/xwn467.
