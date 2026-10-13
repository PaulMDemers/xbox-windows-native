#364 revised diagnostic compiled

Closed362 completed all base tests but capturedzero records because960x540 logical operations fragmented. New version364 selects640x360, where362 actual phase counters recorded one upload per operation. Copied payload921600bytes; same2073600-byte private allocation/policy capture, now with explicit zero-tail check as well as bothguards. Same original upload and memory-policy/copy/calibration implementation, new geometry/version only. No new scanout writes or cache changes.

Build002 tree c613a7bb106d7e5e39283d2f639c02876a085820, DLL ed23ec8ba9cc78805bcb09f50b6abdac3122748c291d28ae11c8f8f23d7567e0, probe725afeac826a737c737395e90d90d2cc033cd89ebfdcd4ce77b0028a528865d9. Host ASan/UBSan 2428 checks/138 balanced allocations,111 independent transport negatives. Native imports/residency/no privileged writes/inherited warnings reviewed. Original361 functions reconstruct after explicit changes. No runtime or physical performance claim from this build.

Build001 failed before compilation: Git shared-alternate nesting exceeded its lookup depth. Preserved completeattempt/source.log. Build002 flattened only the NEW checkout's alternate list, deepest-first; all seven original object stores remain unchanged. This is Git metadata, not a QCOW backing-chain move. Source/SDK shared files unchanged.

Fresh365 and eventual366 are separate from closed362 and never-launched363. All prior failures and strict gates retained.
