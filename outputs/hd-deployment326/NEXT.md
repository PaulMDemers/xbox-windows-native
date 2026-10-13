# Next: measure large-window drawing on the preserved HD release

326 is closed. Do not rerun physical001 or host001/sharing001. The hardware is on the restored pre-HD baseline and there is no pending launch. The0.2.0 tag and archives remain immutable. This tool's six-file hardware restoration is not a full-system recovery test.

Implement a new probe, not a new display driver, starting from the source and exact imports of the qualified206 replay. Use one bounded, visible owned window with test rectangles such as256×128,640×360 and960×540 where the actual client bounds permit them. Record the real rectangle, pitch, operation count, copied-byte counters and clipping/occlusion state. Reject unsupported sizes rather than silently scaling. Keep allocations bounded for the64MiB console.

Time fill, RAM-to-screen upload and overlap copies in both directions separately. Flush completion belongs inside operation timing; expensive statistics snapshots and independent pixel/guard checks belong outside it. Keep correctness mandatory: validate the actual final image and overlap direction with an independent oracle, and expose first mismatching coordinates/colors. Measure a realistic large-window repaint sequence separately from these microbenchmarks. Do not call correctness-oracle wall time FPS.

Use unchanged0.2.0 payloads and preserve the baseline through a new unique deployment attempt. Validate probe behavior and NT5 imports in a new owned emulator child first, keeping emulator timings separate. Then a new bounded physical control run can establish large-area copy cost; no hardware launch is currently queued. Before any performance patch, choose a specific mechanism supported by that measurement and compare against a matched control with identical graphics/audio/event/integrity gates.

Do not change framebuffer cache attributes or enable native GPU work as a shortcut. The9MiB reservation and aliases must remain valid; prior GPU ownership/cache lifetime requirements are not solved by the standalone texture-release experiments. Do not repeat the already answered small-rectangle or pixel-only tests without a new discriminator.

Remaining independent work: repeated HD boots without resetting diagnostic files, a separately planned full restore on suitable disposable media, device-wizard integration and stereo routing, reproducible compiler pipelines, and a sanitized public export/upstream review. No historical strict failure is waived.
