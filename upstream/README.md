# Upstream profiles

[components.json](components.json) records base commits, complete reviewed trees,
overlays, file modes/hashes, build definitions, targets and output names. The
recorded repository URLs are provenance references; anonymous access has not
been qualified. Supply a Git cache containing the exact base commit.

`tools/xwn.py source` creates a detached checkout, applies `src/` and compares the
complete tree. It also verifies recorded checkout-byte rules, including the
AC'97 INF's CRLF conversion. Outputs borrow Git objects read-only through
alternates: retain the cache while using them. They are build workspaces, not
standalone source exports.

The framebuffer target is `xboxbvidnt5`; its installation filename is
`xboxbvid.dll`. The earlier historical review bundle incorrectly called the
target `xboxbvid`. This manifest corrects the recipe without rewriting evidence.

Compiler hashes pin recorded tools. A successful build establishes compilation,
not historical binary reproducibility or hardware qualification.
