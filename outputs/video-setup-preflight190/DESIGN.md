# Wait for actual setup idle before display measurements

Physical188 and189 independently measured pending258 and identified audio01B0;
their later SetupAPI logs identify PCI01B4/01C1 and USBFFFF:FFFF. Real manual
no-driver searches/cancellation cleared the visible queue for that session but
did not complete a durable device binding. The same prompts returned on189.
Neither a synthetic physical null INF nor an unsupported-device disablement is
needed to validate the display operation after actual setup has become idle.
Do not repeat baseline observer boots or claim that190 fixes unsupported hardware.

The runner now waits at most300000ms before starting any probe. It polls the
actual CMP_WaitNoPendingInstallEvents(0) status every250ms, retaining transitions;
requires continuously observed idle0 for5000ms. Any pending sample resets that
interval. Any unknown/error status blocks measurement. A deadline blocks rather
than launching probes or requesting restart. Unsigned monotonic differences
support tick wrap; bounded budgets remain less than2^31. Host tests exercise
pending/late idle/transient idle/error/slow query/wrap and exact deadline cases.

Only after the observed idle gate passes can any sample directory/process be
created. Query actual status before and after each of the five unchanged v8
probe invocations. Nonzero at either boundary stops the trial, preserves partial
results and requests no restart. Retain the exact existing restart_gate.h and its
two observations immediately before the normal restart. No installer control,
window cancellation, registry edits, service/event/dump suppression or driver
changes. Human cancellation is explicit user interaction, separate from telemetry.

Polling is not atomic exclusion of future installer work; it cannot prove that
installation never becomes pending between observations. Stable-idle and sample
boundary evidence must be retained, with actual command/UI/device observations
when useful. An event/error gate is not changed or waived by this timing helper.
Existing Ftdisk49/Srv2013 remain strict failures in physical diagnostics.

New emulator cases must use unique fixtures/namespace, frozen source/binary inputs,
owned leases, bounded lifetimes and complete cold audits. A pending baseline child
must show no sample launch or restart; a settled child must show real gate0,
five exact probes and guarded normal restart. Settled emulator-only null policy
is explicitly inherited, never copied to physical hardware. Current physical
0101/video0093,0088rollback and immutable0.1.0 remain unchanged. No190physical
deployment is authorized by a host build or isolated tests alone.

Microsoft documents an explicit null-driver binding for unused devices, with no
function service. That is a configuration intervention, not support for audio,
SMBus or unidentifiedUSB, and the existing179 emulator results remain separate:
https://learn.microsoft.com/en-us/windows-hardware/drivers/install/installing-a-null-driver
The Windows installation-parameter documentation describes DI_FLAGSEX_SETFAILEDINSTALL,
but we will not fabricate ConfigFlags or use that flag to manufacture idle:
https://learn.microsoft.com/en-us/windows/win32/api/setupapi/ns-setupapi-sp_devinstall_params_w
