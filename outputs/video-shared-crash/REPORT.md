# Shared UC crash rendering and high-LBA dump checks passed

The single controlled crash001 is CLOSED. It used the exact0106 miniport and
boot-video binaries already qualified by the ordinary shared-UC pair and the
subsequent alias diagnostic. No guest driver was rebuilt or changed this turn.
The one-shot trigger requested E058D103 with the exact existing cookie after
desktop startup; no host-injected bugcheck or forced successful completion.

Boot-video's VidResetDisplay, VidSolidColorFill and VidDisplayString executed at
IRQL31. The provider descriptor and globals were identical before and after the
crash: framebuffer FCED6000 -> physical03C00000, Ready1, References1, same desktop
owner and hidden backbuffer. All5672 resident bootvid text bytes matched the
relocated candidate PE. The captured screen is legible, shows the intended stop
and cookie, and reports dump completion. visual-review.json pins that inspection;
render-verification.json independently checks code, globals and translations.

The debugger recorded34events/56resident pins, paired the network shutdown and
dump callbacks, observed genuine final dump success, removed every breakpoint
and resumed. Three payload writes totaling65,536bytes exactly match independent
cold bytes at disk offset148440145920. Actual extended ATA command39 writes use
LBA289922160/8sectors,289922168/64 and289922232/56. All nine block writes after the
first dump command stay within the intended64KiB extent. The former28-bit alias
at11001192448 is unchanged and received no writes. See payload-verification.json.

Cold F allocation is consistent:325directories,6757files,326directory clusters,
zero errors/orphans. Five hives parse; protected binaries and staged payloads
match; inherited device configuration and96MiB/1536cluster pagefile are unchanged.
There are no new warning/error events. Normal shutdown count0 is expected for
this deliberate crash and is not treated as an ordinary clean-run result.
Metadata/hive/protected checks do not constitute an exhaustive all-file audit.

The original crash disk is preserved with SHA256
9f725a94949350264c854fcb24ff104f7373c6cc144c14fcd8e0e19f5313391c.
Never boot or relaunch it. This case establishes rendering and dump-write checks,
not recovery of this new crash image, arbitrary crash timing, PnP removal, WC,
physical hardware or speed. The earlier completed128GiB recovery remains separate.
Preparation46173,runner11007,tracer87163,supervisor30505 and audit23213 all CLOSED.
No owned emulator remains. No physical console access occurred.
