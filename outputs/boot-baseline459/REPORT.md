# Normal cold-start attempt returned to dashboard

The user reports: “It just rebooted straight to the dash.” This followed a request
for full power-off/on and one direct launch of the unchanged normal launcher,
without a graphics test hook. The exact power-off duration and early execution
stage were not independently observed.

Capture002 retrieved ten files twice, read-only. All five registry hives and both
event logs are byte-identical to the closed458 collection; all five hives pass
clean-header and independent raw-value checks. The launcher, normal startup and
existing video trace are unchanged from capture001. There is no new Windows boot,
shutdown or D3D sample receipt. This does not identify the failing instruction.

Capture001 matched seven boot-chain/configuration/startup pins to the known415
working baseline and checked the launcher section digest. Only normal startup
remains. No remote writes, host launch, driver change or Xbox C access occurred
in459. These selected-file checks are not a full FATX allocation audit.

All459 processes are closed. The next investigation is the separate460 logged
wrapper, preserving the installed launcher. Earlier409/410 successful prefix
checks and414 emulator stops do not establish the cause of this current return.

Evidence: [capture001](capture001.json), [review001](review001.json),
[capture002](capture002.json), [review002](review002.json).
