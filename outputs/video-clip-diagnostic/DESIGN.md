# RAM0111 is an enumeration diagnostic, not an optimization

Based on exact RAM0110, add a bounded helper called by XwnUpload for DC_COMPLEX.
It starts two independent enumerations of the relevant rectangles,CT_RECTANGLES,
CD_ANY,first without counting then with limit4096. Each pass reads at most128
batches of8 rectangles. The helper does not alter RAM pixels,upload bounds or
screen-copy behavior. Only the helper/call and identity revision111 differ.

This explicitly changes enumeration state within the owned rendering call,so it
is a diagnostic intervention requiring actual pixel and cold validation. It is
not deployable optimization evidence. A debugger captures actual paired API calls,
counts,final buffers and repeated traversal; missing or invalid output fails.

The first host build failed before compilation because a CRLF patch did not match
LF source. Exact failed inputs/report are in failure-build001. Corrected LF bytes
and hashes use a fresh build002 with exact post-patch source verification. Preserve
both; no guest ever used build001. Existing compiler pins and20GiB guard remain.
