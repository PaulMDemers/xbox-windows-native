# Correct dump writes beyond128GiB

Controlled diagnostic crash006 is closed. Candidate0105 took the genuine existing
extended ATA path. All65,536 cold bytes at disk offset148440145920 match the three
captured write buffers, including the intended E058D103 bugcheck and exact cookie.
The prior wrapped address11001192448 is unchanged. Actual ATA command39 writes
were LBA289922160/8 sectors,289922168/64,289922232/56. All nine recorded block writes
after the first dump command stayed within the intended contiguous64KiB extent.
All three lower returns succeeded, followed by genuine final dump success.

The bounded debugger captured31 events/53 resident pins including the entire
105-byte selector, paired each call by frame/thread, removed every breakpoint,
and resumed before cleanup. Complete cold allocation has324 directories,
6756 files,325 directory clusters and zero errors/orphans. Five hives and
protected hashes remain valid; this is not an exhaustive all-file content audit.
Configuration and the96MiB/1536-cluster pagefile map are unchanged.

See payload-verification.json, verification.json and crash006/closure.json.
Original crash disk SHA980611b0bdd1b442db457872e06fed19ac5f1dc1b0e68b47d692256e61314843
is preserved and must never be booted. Separate recovery validation is in
atapi-lba48-recovery. This deliberate debugger-observed crash is not an ordinary
strict run or physical qualification. No physical access occurred.
