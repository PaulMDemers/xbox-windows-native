# Fixed arithmetic characterization, not a relaxed 484 oracle

484 remains FAILED for exact transparent/opaque endpoints. No old runtime or
oracle is changed. 485 hardware draft is held, not built/deployed/launched.

This fresh PC control changes source RGB to C97539 and background to 2468AC.
Eight captures: clear, ZERO/ONE, ONE/ZERO, alpha0/85/170/255, and blending disabled.
The factor controls use alpha85 and exact destination/source expectations.
Every factor and enable state is set and read back at every stage.

Before execution, three distinct hypotheses are fixed per 8-bit channel:

- nearest ideal: (S*a + D*(255-a) + 127) // 255
- combined floor: (S*a + D*(255-a)) // 256
- separate floor: (S*a // 256) + (D*(255-a) // 256)

All four alpha images must match ONE same model, with exact RGB and unchanged
background. The clear and factor-identity/disabled controls must be exact under
every model. Each image retains the independently defined 561 safe interior,
2199 exterior and 1336 bounded raster-edge pixels. No tolerance or model will be
added after observing results. A match characterizes these selected inputs only;
it does not trace runtime instructions, prove all alpha values, qualify exact
ideal blending or requalify 484. Unknown/multiple matches fail characterization.

Same owned NT5 D3D7 software device, private64x64 RGB32 surface, no mode change,
primary surface or hardware operation. Fresh reusable404 seed child, read-only
validated floppy, unique namespace, 90-second processes and 600-second outer
watchdog. Frozen sources/tools/runtime; independent cold readback/module join,
five-hive/event checks, normal restart and process closure. No Xbox launch.
