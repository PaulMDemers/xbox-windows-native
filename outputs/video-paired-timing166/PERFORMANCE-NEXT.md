# Discriminator after paired timings

Inspect the qualified RAM0112 shadow.c before changing code. XwnBitBlt renders
through EngBitBlt into ShadowObject and then XwnUpload copies the destination
rectangle to the mapped framebuffer row by row. XwnCopyBits follows the same
two-stage path for screen destinations. Screen reads substitute the RAM surface.
This provides a plausible explanation for readback/overlap gains together with
fill/upload cost, but source structure alone does not localize measured latency.

Static actual-binary inspection is retained in upload-instructions.json and the
two disassembly files. XwnUploadBox calls13f10 per row; memcpy/memmove alias that
address. The forward large-copy path already aligns the destination and uses
REP MOVSL, with byte handling only for edges/small copies. There is no evidence
for a naive byte-at-a-time bulk upload; replacing it with a word-copy loop would
be speculative. The captured range includes labeled constructor/destructor data
after13fb4; those are not executed copy instructions. This does not measure cost.

If fresh paired hardware samples confirm the regression, separately measure
engine rendering versus upload work with bounded counters/timing, or use a
matched isolated upload primitive test. Preserve exact clipping, RGB pixel
checks, RAM/scanout coherence and framebuffer ownership. Only then choose a
narrow optimization. No speculative cache-attribute change, SSE use in kernel
without state ownership, GPU acceleration or encoder/mode switch in this kit.

Five unchanged probe invocations within each boot expose variance but retain
the same operation order. Two boots/control-first cannot remove every thermal,
background-activity or order effect. Report raw samples and median/ranges, never
translate these small-rectangle synchronous timings into window-drag FPS.
