# RAM0110 line uploads: matched ordinary runs pass

Both control001 (RAM0109) and candidate001 (RAM0110) are CLOSED and passed strict
ordinary emulator qualification and per-operation attribution. The same probe130,
immutable parent, startup, settings and protected payloads were used. Only the
display DLL differs. Control uses the frozen qualified109 binary; candidate110 was
freshly built from the pinned109 source tree with the reviewed0110 patch.

All18 cold images are identical between drivers and match the independent host
pixel oracle: 1,769,472 RGB pixel comparisons per run. Both returned normally to
the dashboard, with clean full allocation (326 directories,6778 files,327 directory
clusters,zero errors/orphans),five structural hives,unchanged protected payloads,
pagefile and configuration, and no warning/error/application event deltas.

| Operation | RAM0109 bytes | RAM0110 bytes |
| --- | ---: | ---: |
| Unclipped32-pixel horizontal or vertical line | 2,359,296 | 132 |
| Unclipped32-pixel45-degree diagonal | 2,359,296 | 4,356 |
| Tight-clipped horizontal line | 64 | 64 |
| Two separated clip islands on a line | 784 | 784 |
| Zero-length line | 2,359,296 | 4 |
| All18 samples | 21,258,272 | 42,564 |

The actual NT5 bounds include both endpoints conservatively; the short line uploads
33 pixels while changing32. There is no claim that byte savings translate directly
to FPS or that this measures physical window dragging. Rectangular bounds still
include unchanged pixels for diagonals and gaps between complex clip islands.

pair-review.json verifies both actual logs, reference identity, matching fixture
and probe pins and strict qualifications. Four mutations (cost,pixels,extra callback,
failed qualification) are rejected. The first host pair-verifier attempt passed
content validation but failed serializing a sibling evidence path; its exact script
and failure record are preserved. The corrected analysis did not rerun either guest.

Some frozen inherited captions and audit limitation text still say unchanged109
or desktop baseline. They are stale labels, preserved rather than rewritten in
completed evidence. Actual driver revisions, DLL hashes, source manifests and the
pair review establish the109/110 comparison. The separate line-bounds diagnostic
remains failed overall due to its late observer E14; only its completed paired line
intervals qualify as bounds evidence.

Control accepted2026-10-08T03:27:57.577358UTC; candidate accepted03:30:18.959045UTC.
Control sessions28151/6315/86300/14099 and candidate57307/81628/75212/87350 CLOSED.
Never relaunch or recollect. Broader GDI/cursor/mode-reset evidence is maintained
separately in ../video-line-gdi. No physical access or deployment occurred.
