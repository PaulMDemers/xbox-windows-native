# Observer failure retained; workload and cold gates passed

candidate001 is CLOSED and audited. Never relaunch or recollect it. The observer
failed its module-list assertion at the first checkpoint while using the older
fixed kernel base823df000. It captured zero frames/pins and removed every
breakpoint, then resumed the guest. This is failed diagnostic qualification,
despite the subsequent workload and cold gates passing. See verification.json.

The guest completed54cases162pixel stages/54self-comparisons, normal shutdown and
dashboard return. Full allocation325directories6759files326directoryclusters had
zero errors/orphans; five hives/protected payloads and96MiB pagefile remained
valid. No new warning/error/application events. No physical-console access.

The next NEW video-ram-scanout2 kit retains the same binaries but discovers the
live kernel base from two IDT gates and validates headers before walking modules.
Its separate replay test agreed with an older independently decoded snapshot's
823e0000 base. That replay does not establish this failed attempt's actual base.
All failed observer, compiler and preparation records remain preserved.
