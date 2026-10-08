# Next discriminator: actual NT5 same-mode reset

Cursor work does not exercise surface/PDEV replacement or the boot-video handoff.
The unchanged RAM0109 DrvAssertMode disables ShadowActive before the miniport
reset; enabling requests the mode, restores ShadowActive and uploads the RAM
surface. DrvDisableSurface unregisters the primary before deleting its surface
and releasing the shadow allocation. Those source paths need actual NT5 runtime
evidence before claiming transition safety.

Use a NEW ordinary probe and a separate bounded observer. First record actual
EnumDisplaySettings current/enumerated modes and CDS_TEST responses against the
pinned miniport. Keep the known visible 1024x576x32 mode. A same-mode CDS_RESET
request is a candidate trigger, not proof that disable/re-enable occurred.
Use actual pinned Win32 APIs, not direct calls into driver callbacks.

Observe DrvAssertMode and actual surface/PDEV enable/disable entry/return pairs,
tracking module reloads and ownership changes rather than assuming stable bases.
Record which transitions really occur; if the reset is a no-op, retain that
coverage failure and choose the next discriminator from actual NT5 behavior.
Do not invent success counters or patch the driver solely to force a transition.

Require a deterministic pattern and cursor before/after, fresh screen DC state
where appropriate, independent raw framebuffer checks, no stale primary access,
unchanged shared framebuffer cache/mapping contract, full teardown, normal
shutdown, cold allocation/hive/protected hashes and strict event gates. Preserve
any failing frame or inaccessible runtime state. Separate real mode reset,
boot-video/crash ownership and hardware/new-resolution qualification.

Source inspection is a plan, not an executed transition test. No mode/reset
experiment was launched by the color-cursor kits.
