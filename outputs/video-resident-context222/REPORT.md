# Native CPU ownership checkpoint222

Ordinary runtime001 passed the CPU ownership scope and returned normally to the
dashboard. This prepares accelerated video; it does not establish GPU ownership
or acceleration. Strict whole-boot qualification remains FALSE for inherited
Ftdisk49, retained without suppression or a waived gate.

The demand-loaded NT5 driver allocates and checks an actual16KiB contiguous UC
buffer below the framebuffer reservation, retains the owning FileObject, uses a
bounded kernel mutex, and rejects foreign owners/stale generations. EXPOSE always
returns HOLD. There are no GPU register accesses, descriptors, channel grants or
device-policy changes. Failed cleanup entry defers a pending IRP through a
reserved work item; eight bounded retries end in success or retained CPU ownership
until reboot. That fallback is host-tested, not native fault-qualified.

## Evidence

- Production CPU core O0/O2 ASan/UBSan:512 concurrent leases,532 balanced
  allocations/frees and references; translation/OOM/IRQL/wait/corruption/counter/
  generation boundaries passed.
- Unchanged driver.c with host kernel substitutes O0/O2 ASan/UBSan passed pending
  cleanup retry, exhaustion, elevated-IRQL deferral, completion and reference/
  work-item checks. These do not establish NT5 scheduling or ABI behavior.
- Build005 compiled with pinned compiler/import archives. Actual fixture
  providers cover its imports, including SetupAPI idle; driver sections are
  nondiscardable. Static review is not runtime PTE/cache-alias residency evidence.
- ONE ordinary runtime001 launch accepted2026-10-10T16:46:37.779885UTC;
  dashboard returned16:48:16.058507UTC; cold audit closed16:48:34.077982UTC.
  Four joined workers completed64 leases plus one handle-cleanup lease:
  65 allocations/releases/exposure refusals,1 cleanup release,3194880 verified
  bytes. Actual wait-all return3 validates the corrected success-range check.
- Existing targeted wizard helper closed3 known dialogs and reached stable
  SetupAPI idle without disabling devices. Both probe idle gates passed.
  One normal shutdown; no application event or Application Popup.
- Cold allocation320 directories/6723 files/321 directory clusters,0 errors/
  orphans;5 structural hives/28 protected hashes passed. Startup, event/SetupAPI
  history and selected typed policy passed. This is not all-file content auditing
  or complete hive byte equality.
- Sole warning/error: Ftdisk49 HarddiskVolume6,record204,error3. CPU scope TRUE;
  strict/ordinary overall FALSE. Native cleanup faults/physical/GPU unqualified.

## Reproducibility and preserved failures

Build001 missing HAL import and build002 compiler warnings are preserved, with
exact prior001/002/003 source snapshots. Build003 linked after owner-reference,
cleanup and probe fixes. Build004 failed before compilation: generated output
replacement also changed the pinned HAL archive path. Build005 fixes only intended
output selectors and adds actual SetupAPI gates. No old attempt was relaunched,
rebuilt or recollected.

resident.sys SHA256:
`0c272f680b3d6a9574db79629cecb8fe0852260a20ca9de2ed6350dc93c65f06`.
probe.exe SHA256:
`2d94065fc3166027f17cd17931f27486ab49a7a481e85941c05da65bb99d383e`.
Seed: `E:/Codex-archive/xbox-windows-native/resident222/runtime001-source.qcow2`.
Closed artifacts:
`E:/Codex-private-artifacts/xbox-windows-feasibility/resident222-runs/nt5-resident222-runtime001`.
Frozen input pins, audit/closure records and checkpoint-review.json identify the
actual closed result. Preparation69643/controller66959/runner/observer are CLOSED0;
no owned guest remains. No debugger, physical access or GPU exposure occurred.

Physical0101/video0093,0088 rollback,immutable0.1.0 and failed evidence are preserved.
Audio/USB/PCI hardware220 tickets separately closed/restored; no branch merge or
root physical change. Next: actual loader-to-NT5 instance/channel ownership and
SetMode TRUE boot guards, then native bounded service/completion/drain/quarantine
before16x8 copy. CPU cleanup is not a GPU drain witness.
