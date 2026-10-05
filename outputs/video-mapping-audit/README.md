# Read-only framebuffer mapping audit

Candidate0094 extends the qualified0093 miniport only with observation records.
It leaves the desktop GPU aperture and VIDEO_MEMORY_SPACE_MEMORY flags unchanged.
At PASSIVE_LEVEL after a successful mapping, it records CR0/CR3/CR4, CPUID flags,
first/last mapping and known loader-alias PDE/PTEs, PAT and supported variable
MTRRs. PAE skips the fixed non-PAE page-table view; unsupported MSRs are skipped.
No CR/MSR/page-table/cache/GPU programming is introduced. This is not an exhaustive
alias scan. Compiled tests intercept privileged reads and reject privileged writes.

The source chain and tools are pinned in inputs.json/manifest.json. Source tree:
df828b3942de0d03e2cc3647f414e3bee4c359c2. Candidate SHA256:
ea18fa6c831b4cd9478cd85c65d2670b5ef0cb7892f804e9a1ed8572fc6a98ce.

Source observations from qualified0093 tree329a29d6:
- winldr.c XwnPreparePagingDisplay reserves the top RAM framebuffer and uses
  PTE bits0x1B (present/write/PCD/PWT) for identity/high aliases.
- bootvid's NT5 VidInitialize maps the reserved RAM address with MmNonCached,
  because the PCI aperture can disappear before shutdown rendering.
- Nt5VideoStartIO instead maps FramebufferAperture+Offset through VideoPortMapMemory
  with VIDEO_MEMORY_SPACE_MEMORY. Live page/PAT state must confirm its cache type.
- framebuf creates a bitmap directly over that mapping with no drawing hooks.

Hypothesis: direct reserved-RAM access may reduce costly screen readback compared
with the GPU aperture, without changing cache policy. It is not yet implemented
or measured here. Do not substitute WC/WB mappings while aliases are unresolved.

Physical protocol is one bounded GDI boot, collect/qualify, then restore0093.
Remote backup is xboxvnt5.trace012. The current0093 baseline overrides only the
miniport hash in the old release manifest; FATX/HAL/loader/startup hashes remain.
No second diagnostic run is permitted. Check reports for actual current status.

References: [Microsoft VideoPortMapMemory](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/video/nf-video-videoportmapmemory)
and [Intel system programming manual](https://www.intel.com/content/dam/support/us/en/documents/processors/pentium4/sb/25366821.pdf), memory cache control/PAT/MTRRs.

## Observed result (2026-10-05)

Emulator strict audit passed. Physical0094 captured the same mapping:
GPU physical0xF3C00000..0xF3FFFFFF, first/last PTE0xF3C0017B/0xF3FFF17B,
PAT index3=UC. Known loader alias endpoints0x83C00000/0x83FFF000 were absent.
This is not proof that all other aliases are absent. See physical-mapping.json
and findings.json for raw CPU/PTE/MSR state.

Hardware pixel/binary checks and normal restart passed, but strict qualification
is FALSE due to two new rundll32 DLL-initialization popups during shutdown.
Their text matches the previously observed shutdown issue; no cause is proven.
0093 was restored and verified without another launch. The trace and logs are
preserved. This diagnostic is not promoted as the baseline.
