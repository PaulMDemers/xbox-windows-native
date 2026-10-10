# Resource-only installation and power transitions pass — closed

The narrow live-resource compatibility correction removes Code10. Installation
succeeds without a reboot requirement; the live devnode reports problem0 and
started, profile2 at C000. Telemetry remains disabled and returns error50.
All5,751 host ASan/UBSan regression cases pass, including the actual52-byte START
capture, truncations, all256 port-flag encodings and invalid ranges/counts/forms.
Only version/revision0/0 and flags0x31 were added to the prior accepted encodings;
exact C000/C200 profile ranges, lengths, types and count checks remain enforced.

SetupAPI accepted DICS_PROPCHANGE with no reboot/restart flags, followed by a
successful interface query. A second FILTER/START sequence is captured. Three
rounds of real D3/D0 requests completed successfully (six transitions), with the
powered gate0 in D3 and1 in D0 and the final power counter6.

Removal stopped at CONFIGRET52 (CR_CALL_NOT_IMPLEMENTED), yielding probe exit29.
The exact installed setupapi.dll ANSI CM_Query_And_Remove_SubTree_ExA export is a
six-byte constant-return stub. Its Unicode counterpart has an implementation;
lifecycle004 tests that entry point with preserved UTF-8 veto reporting and adds
actual PnP minor dispatch tracing. This is our helper compatibility failure,
not a device-removal veto. Removal and normal restart are not qualified here.

The guest ran20:13:17–20:16:18UTC on2026-10-10 and closed at its180-second host
bound. No event6006/dashboard return. Do not relaunch. Cold protected files,
five hives, old log history and allocation pass (319directories,6726files,
320directory clusters, no errors/orphans). Target SYS SHA256:
f6225780619a35ce338d99acf162d41bcf742644d9d4cd2de3694637debd26ce.
Installed OEM-INF SHA256:
12d2f7d71077da69181e978629b9679c1a1ae70a481546c56d229e30251fe937.

The optional read-only HMP screenshot failed because this xemu monitor does not
implement screendump. screen002.json retains that response; no screen observation
is claimed and no UI input/reset was sent. The baseline HAL was retained; no bus
transactions or physical access occurred. Full binding changes remain reviewable
in audit.json, and inherited Ftdisk49 remains a whole-boot failure.
