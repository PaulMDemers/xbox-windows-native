# Physical 1080 phase attribution completed

Both single hardware runs completed the full diagnostic workload at1920x1080x32/pitch7680: five drawing samples,75 large-area intervals per run, six audio API phases, installer-idle boundaries, joined children and one normal shutdown. Mode0 clocks were disabled; mode1 returned coherent positive timings with stable calibration and no timer errors/overflow. The original physical201 wizard helper was used. No new user audibility or visual observation was collected.

Control launched16:06:32UTC and dashboard return was observed16:14:31UTC on October13. Candidate launched16:19:41UTC and returned16:27:44UTC. Each used a fresh rollback capture and unique namespace. Normal startup was restored first on return, the actual tested DLL was preserved, then the original display DLL was restored and read back. Post-scan readback verified the normal E baseline and five hives plus original F protected files/loader/five hives. The console is back at UnleashX with the original display DLL `b23b94ac12c9f507e3d905d9de905dcff9a8fd53c2fba4336fb830e97666101d`. Xbox C was never accessed by tools.

The post-control E scan had622 directories,7581 files and639 directory clusters; post-candidate had628/7597/645. Both had zero errors/orphans and consistent allocation. The increase is the second owned workload namespace and its outputs. All four unique scan launches are closed. Scan output resides in owned F/Applications directories; the F Windows rollback was not modified. final-review.json rehashes1320 declared captured files per case plus scan artifacts, actual test DLLs and169 frozen inputs. No owned subprocess or hardware test remains active.

Diagnostic completion is TRUE, but combined and strict qualification remain FALSE in BOTH cases. Each has inherited Ftdisk49 on HarddiskVolume1 and Srv2013 for Windows F (mapped to dashboard C); Srv2013 occurred inside the combined interval. The original event gates were not changed. The new diagnostic_workload_completed field does not waive those failures or qualify performance. It records workload/restoration/integrity completion separately so the second diagnostic can be collected safely.

## Measured attribution, largest960x540 operations

Values below are medians in milliseconds per operation across five samples within each boot. Engine columns show the relevant measured engine callback. The upload wrapper contains the copy body, so those two must not be added together.

| Operation | OFF wall | ON wall | ON engine | ON copy body | ON wrapper |
|---|---:|---:|---:|---:|---:|
| Fill |31.875|31.875|7.562 BitBlt|24.310|24.326|
| RAM upload |41.053|41.053|16.945 CopyBits|24.254|24.269|
| Overlap down/right |40.263|40.263|15.712 CopyBits|24.241|24.256|
| Overlap up/left |40.263|41.053|16.130 CopyBits|24.267|24.282|
| WM_PAINT |41.667|41.053|16.954 CopyBits|24.253|24.268|

This diagnostic evidence points to framebuffer copying as the largest measured component for these large operations, with software-engine work also material. Wrapper overhead is small relative to the copy body in these observations. The similar OFF/ON values do not establish zero profiling cost: wall timers are quantized, counters are global, and these are sequential boots with five samples each. Background/preemption is included; event failures remain present. This is not desktop FPS, a causal speedup, GPU acceleration or release qualification.

The source review confirms that copy-body timing encloses row copies while engine timing ends before XwnUpload; complete-wrapper timing contains those bodies. Earlier209 scalar-store unrolling showed no benefit and remains OFF. Historical211 upload accounting found explicitly bounded copies with no fallback in its measured scene; do not invent a new bounds defect from these timing totals.

Original source and host failures are preserved. Host001 tests18 actual path allowlist cases plus restore/one-send ordering, not a simulated full console. An ad-hoc hive import probe initially omitted the library path; the actual auditor preamble, which includes that path, passed unchanged. Copied342 audit changes are explicit in the patches, with combined/strict expressions retained byte-exact. All raw binaries/hives/INF payloads remain private. Neither immutable release tag was moved.
