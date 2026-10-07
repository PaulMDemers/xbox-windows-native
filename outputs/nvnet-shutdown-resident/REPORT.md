# Resident NVNet shutdown helper, implementation0104

The preserved crash002 diagnostic reached the NDIS miniport bugcheck callback
and faulted in NVNetIdleTransmitter at IRQL31. The exact code page was absent.
This is a directly observed residency defect. It is separate from the original
physical111-byte corruption and does not establish that corruption's cause.

0104 removes CODE_SEG("PAGE") from both the function definition and declaration,
and removes PAGED_CODE from that function. The MMIO accesses, finite polling
loops, stall durations and shutdown registration are unchanged. The other
reviewed shutdown helpers already reside in nonpaged text. At HIGH_LEVEL the
existing handler skips its ordinary lock-taking pause helper.

The first fresh candidate build was rejected before any guest launch: removing
the definition annotation alone left the header declaration in PAGE. The source,
inputs, patch and build report are retained in preliminary-build001, with the
private rejected binary and original Linux build directory. Corrected build002
uses tree4ab4b8ab56ee8373d60b3fade3ea192c041266c9. Matched control001 uses0103.

Reviewed NVNet hashes:

- Control:3ac304984d66a4e289c9ca63d8e57b5af09219ced7f43d87018b09d1c96ef3d9.
- Candidate:aee9c501c5ec2e5f8c874ee23926cdeab4d10afec63f3735b8024a84bbc32fe8.

The corrected idle helper is nonpaged .text at RVA1f30; MiniportShutdown is at
RVA22a0. All reviewed shutdown callees are nonpaged/nondiscardable. Actual imports
match pinned owned NT5 kernel, HAL and NDIS exports; stall calls use the HAL
KeStallExecutionProcessor import. See nvnet-review.json for full disassembly.

The first normal test harness in this directory failed before storage workload:
FAIL_CONNECT_WAIT because its outbound TCP test was incompatible with the
runner's existing restrict=on network. The host recorded zero connections.
The run was stopped through owned cleanup, preserving its desktop capture and
cold evidence: clean allocation323directories6754files324directoryclusters,
five parsed hives, protected hashes, no new warning/error events, but zero normal
shutdowns and strictFALSE. Never relaunch control001. Candidate001 here was
prepared but NEVER launched; preserve it without using its identity again.

The probe's preliminary link failed for CRT stack-check/memset references; static
buffers and a statically initialized address removed those dependencies before
the pinned build. These are host build/harness failures, not guest driver results.

New ordinary validation is in ../nvnet-shutdown-network. It retains restrict=on
and uses an explicit127.0.0.1:4597 guest port forward. The same guest verifies
two32x4096-byte request/response streams, before/after the storage workload.
Driver binaries and settings are the same matched pair. Crash validation is
separate in ../nvnet-controlled-dump, gated on both ordinary results.

No physical Xbox access, driver deployment, dump/service suppression, policy
change or qualification waiver occurred. Physical0101/video0093, original0088
and immutable0.1.0 remain unchanged.
