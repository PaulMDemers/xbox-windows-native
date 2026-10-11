# Exact comparison scope

The worker's expected buffer is a separate allocation initialized from VRAM, then filled through surface_download_to_buffer. Actual surface_download calls that same conversion/readback implementation to write VRAM. The full memcmp verifies that VRAM receives the expected downloaded representation, including retained padding, while the worker's fences and locks constrain execution.

This is not an independent graphics-format, pixel-correctness or renderer oracle. The phrase “independent expected buffer” in the frozen DESIGN describes separate buffer storage, not an independent algorithm. A shared conversion defect could affect both downloads identically. Post-success physical RAM captures use GPU read callbacks and do not add an independent GPU source oracle.

The qualified scope is bounded exact consistency of this actual GL readback-to-VRAM path at the sampled Xromwell entry. Complete reference retirement, persistent producer closure, native ownership, ordinary acceleration and physical correctness remain unqualified. A future graphics correctness test must compare against an independently specified pattern/format oracle and preserve these earlier limits.
