# 216 actual handoff and context discriminator

This kit adds four approved read-only registers to the closed214 diagnostic:
PFB_CFG0 (100200), PFB_CSTATUS (10020c), PGRAPH_DEBUG_3 (40008c), and
PGRAPH_CTX_CONTROL (400144). It retains the existing681000-byte mapping, two
passive-level hooks, exact actual NT5 read-provider import, CPU-only once gate,
OFF/ON common main object, original modes and211 GDI/cold/event gates. No GPU
write, IRQ acknowledgement, reset, context setup, RAMIN/USER mapping, indexed
read, cache change, device-policy change or physical access is introduced.

The concrete question is whether current PFIFO channel1 can submit into the
observed PGRAPH channel0 without a context-switch handler. Pinned compiled-model
pgraph_context_switch reads CTX_CONTROL bit16 as validity and CTX_USER bits24..28
as channel. If invalid or different, it sets waiting_for_context_switch and the
context-switch interrupt. DEBUG_3 bit2 hardware switching asserts unsupported
in this model. Validity cannot be inferred from CTX_USER alone. The new registers
therefore discriminate a real pending adapter decision; they do not confer an
ownership grant. New PFB reads report declared configuration and actual model
VRAM size, not PRAMIN physical backing. Both defaults/read bodies are privately
pinned against the actual685f24e3 model manifest.

Actual intended214/216 launcher c7a2b9c8 and FreeLoader c936b06e are matched to
historical build outputs. Launcher source/object are retained privately; current
historical FreeLoader source may include subsequent edits, so it is separately
pinned with that limitation. This is not a fresh reconstruction proof.

XBE's CPU CLI/paging/IDT transition replaces the dashboard interrupt handler.
Cromwell startReactOS stops USB, issues CLI, clears/reloads IDT and passes a
Multiboot map with top4MiB type0 on the64MiB profile. Current Xbox loader source
maps type0 to LoaderFirmwarePermanent. The retained loader validates scanout
against that reservation. These establish a CPU/memory-map path, not GPU idle
or a GPU context release. No instance-memory ownership record is passed by the
inspected paths. The128MiB historical workaround is outside this64MiB run.

Actual bootvid's640*(480+13+1)=316160-byte indexed backbuffer ends at04000000.
Linux v6.12 Nouveau's NV04-family allocator reserves512KiB at VRAM end for
PRAMIN; envytools describes related write protection. These are specific leads,
not proof that NV2A has the same mapping. The previously commented pbkit20KiB
overlap remains counterfactual. xemu's independent1MiB RAMIN means a successful
emulator copy cannot validate a physical alias or boot-buffer collision.

Mock host checks cover both phases, read order/count, five rejected malformed
calls and32 joined concurrent same-phase callers. Parser corruption checks
require exact56 ON records/52 reads or two OFF markers, trace count/missed/IRQL,
all offsets and checksums. These do not emulate register semantics. Ordinary
runtime results, if produced, are reported separately and require one unique
child per case, normal shutdown/dashboard return, full cold allocation, five
hives, protected hashes/startup and unchanged event gates. Inherited Ftdisk49
remains a strict failure and cannot authorize GPU submission.

Physical0101/video0093, original0088 rollback and immutable0.1.0 stay unchanged.
There is no native resident submit/drain adapter in216. Synthetic215 witness
flags remain mock claims. Actual resource ownership, instance backing, bounded
context acquisition and completion/drain need concrete evidence before writes.
