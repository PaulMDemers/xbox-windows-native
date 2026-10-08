# Explicit fixed-Z swizzled draw probe

This fresh probe corrects153's state mismatch before either fixture launch.
After target binding it explicitly writes NV097_SET_CONTROL0=0x00100001, disabling
W-buffering, and logs DEPTH_MODE. The first rectangle uses Z=0; the overlapping
second rectangle uses Z=16384. W remains1. Colors, shapes, sparse CPU stores,
readback stages and full32768-byte arena/tail checks otherwise follow153.

An independent rectangular Morton oracle predicts all twelve files. The pinned
build003 control/candidate xemu pair remains unchanged. Require both exact cold
pixel sets, observed swizzled lifecycles with matching pitches/formats, actual
candidate CPU-write evictions, normal dashboard return, complete clean E allocation,
unchanged existing E contents/chains and entire F.67 host oracle checks pass.
Reuse bounded DeadlineFTP from152 within the original native probe deadline.
No debugger, physical deployment, Windows boot or performance qualification.
