# Physical368: paired copy measurement closed

The single physical Windows run was accepted at 20:51:48 UTC on October 13, 2026; dashboard FTP returned at 21:00:07. The diagnostic workload completed and Windows recorded one normal shutdown. Normal E startup was restored first, the tested driver preserved, and the original303 display driver restored before evidence collection. Final readback at 21:02:56 verified the E baseline and original F rollback. All owned sessions are closed. No Xbox dashboard C access occurred.

Four actual 640x360 upload calls each copied 921600 bytes. Five packet reads contained those same four completed records, not twenty independent measurements. The private RAM copy and original display upload alternated order. Both used the same source rows; the private destination pitch was2560 and the display pitch7680.

| Call | First copy | RAM milliseconds | Display milliseconds |
| --- | --- | ---: | ---: |
| 0 | RAM | 6.386667 | 10.914667 |
| 1 | Display | 6.357333 | 10.864889 |
| 2 | RAM | 6.441778 | 10.840000 |
| 3 | Display | 6.338667 | 10.864000 |

Median RAM time was6.372ms, median display time10.864444ms; the median paired ratio was1.709005. Effective throughput was136.44–138.66MiB/s to private RAM and80.53–81.08MiB/s to the display buffer. Each call's32 timer calibration pairs measured3.556–4.444 microseconds. No calibration subtraction was applied.

All four source/output comparisons,64-byte guards and unused scratch tail checks passed. Both memory-policy captures per call reported507 private WB pages and507 display UC pages, with matching captured mappings/register state. The additional join to the full shadow/display capture passed, including16 rejected mutations of actual owner/source/destination identities. All ten full cold/post-read memory pairs passed the prospectively declared367 policy comparison. Original365 failed evidence remains unchanged.

These observations locate a substantial cost in the current display-copy path, while the RAM copy also remains material. They do not prove that cache policy alone accounts for the difference: destination strides differ, and instrumentation/allocation/verification affect cache history outside the timed intervals. This is not an optimized-driver comparison, desktop FPS result or demonstrated speedup. No cache settings, aliases, SIMD or GPU ownership changed.

Graphics pixels/copies/DIB/text/window workloads, actual1920x1080/32bpp/pitch7680, audio API/device checks and joined child completion passed. Five hives, protected binaries/INFs, selected policies/device bindings, event/SetupAPI history and persisted E drive bindings passed. Audio audibility and stereo routing were not newly observed.

Both full E allocation scans were clean: before646 directories/7665 files/663 directory clusters; after652/7706/669. Both had zero errors and orphan clusters. Closeout rehashed1345 captured files and438 frozen inputs, plus the two read-only scanner captures. This is selected binary/hive and complete allocation verification, not a full file-content audit.

The original strict and combined verdicts remain FALSE: Ftdisk49 names HarddiskVolume1, and Srv2013 names Windows F: inside the measurement interval. No event gate is waived. The Windows letter does not authorize access to dashboard C. Release/performance qualification remains false; immutable releases and rollbacks are unchanged.

Authoritative records: candidate001/audit.json, timing-review.json, collection.json, both scan trial records, final-state.json and final-review.json. The inherited closeout console label says356; its output path, hashes and structured record are368. The frozen helper was not changed to cosmetically relabel that historical message.
