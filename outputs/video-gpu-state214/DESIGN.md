# Observational GPU state214

214 adds two emulator-only snapshots through the miniport's existing681000-byte
Control mapping. Both hooks are in the same freshly compiled common object:
phase0 follows retained-mode validation, before Ready; phase1 follows the first
successful shared framebuffer map. OFF and ON differ only in the helper's
XWN_GPU_SNAPSHOT flag. No extension layout, map, interrupt, device policy,
scanout format, cache attributes or GPU write/submission is added.

A CPU interlocked once gate bounds each phase to one emission. It is not a GPU
lock or completion fence. Phase, passive IRQL, non-null/aligned mapping and exact
length guards precede reads. ON records22 explicitly approved32-bit words and a
checksum/end record per phase. Invalid guards emit21403 and do not read MMIO.
The original video path continues; cold qualification fails on any21403.
Control emits only the two mode0 markers. No unbounded polls or RAMIN reads occur.

model-inventory.json pins full source copies against the actual685f24e3 xemu build
manifest. PMC interrupt/chip words, PFIFO configured RAM tables/cache1 words,
PGRAPH interrupt/context/FIFO words and PCRTC interrupt/start words are approved
from their actual read handlers. Raster increment and RDI indexed-data reads are
excluded because the model mutates state on read. An absent PGRAPH_STATUS symbol
is not invented; an unimplemented PMC_ENABLE read returning0 is not reported as
an enable-state capability. The default PGRAPH helper reads regs_ directly.

The actual NT5 READ_REGISTER_ULONG provider is pinned as mov pointer/mov load/ret4.
Its ABI matches one pointer argument; the helper imports only that new routine.
Do not impute modern barrier implementation details to the old binary. Primary
[API documentation](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/wdm/nf-wdm-read_register_ulong)
requires resident mapped device memory and identifies Windows2000 support. This
probe runs only at passive IRQL and never treats these reads as GPU ordering.
The CPU atomic once gate compiles inline; it adds no interlocked kernel import.

Host002 exercises the exact helper with an independent address/value/order oracle:
105 OFF/352 ON checks, five invalid-context faults, duplicate phases and32 concurrent
same-phase callers with successful join. Host001 reported sanitizer success, but later source review found a plain check
counter increment shared by main and the winning worker. Preserve that result
and host001-concurrency-review.json; use002 with an atomic counter for current
coverage. Production helper and native binaries did not change.002 provenance
also pins the actual executed script beside the inherited generator-label pin.
Mock provider success does not prove
physical read semantics or NT5 runtime. parser002 has254 fail-closed record/order/
value/checksum/header checks. The failed first harness expected count48->49 to
fail even when the extra record is outside214's scoped family; it stays preserved.
The parser did not change. The corrected test checks count255 and explicit valid
legacy-family coexistence, retaining exact214 lifecycle gates.

Fresh children use the immutable211 prelaunch parent, retained accounting119 ON,
HAL/FATX/shared0106 bootvid and captured physical-core policy. No synthetic null
device or service/device suppression is added. The known targeted wizard Cancel
helper remains explicit; unknown dialogs hold the run. Require five retained GDI
samples, exact pixels/upload/readback/phase coverage, actual snapshot records,
one normal shutdown/dashboard return, full cold allocation and five hive/protected
file/typed-state checks. Any inherited Ftdisk49 remains a strict whole-boot failure.

The two snapshots are sequential register observations, not atomic GPU state.
Identical pointer values, empty interrupts or equal DMA_GET/PUT cannot prove
exclusive ownership or safe channel/context reuse. xemu's separate RAMIN backing
cannot establish physical instance-memory non-overlap. No acceleration, new mode,
hardware read safety, physical qualification or release promotion follows from
this diagnostic. Preserve physical0101/video0093,0088 rollback and immutable0.1.0.

Actual matched ordinary cases closed with exact OFF/ON trace scope, retained GDI
and full cold integrity passes. Candidate44 reads were identical across phases:
push/pull access disabled, PFIFO channel1; PGRAPH FIFO access enabled, context0;
retained scanout03c00000. These fields do not prove idle or exclusive ownership.
Whole-boot strict qualification remainsFALSE solely inherited Ftdisk49. See
REPORT.md, state-observations.json and NEXT.md. No physical access or GPU write.
