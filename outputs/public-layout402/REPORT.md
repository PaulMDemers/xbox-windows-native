# Public-facing source layout and guides

The repository now exposes 414 byte-preserved overlay files across six independently
reviewed profiles in src/, plus the original display-settings utility. Upstream
base commits, reference trees, file modes/hashes, definitions and artifacts are
recorded in upstream/components.json. The framebuffer target is corrected to
xboxbvidnt5; historical401 artifacts were not edited.

Root README and eight new user/developer guides explain architecture, builds,
installation boundaries, display configuration, troubleshooting, recovery and
licensing without private host paths. All49 local links resolve. Original work
is MIT under the scoped root LICENSE/NOTICE; upstream headers/license texts remain.
Separate source profiles retain their tested differences instead of being merged.

## Validation

- Portable tools/xwn.py verifies overlays, materializes an explicit detached base
  checkout (including linked-cache support and INF checkout-byte rules), verifies
  the complete tree, checks compiler hashes/capacity and builds into fresh output.
- Six fresh complete source trees exactly match recorded references. All six
  profiles compiled, producing eight selected artifacts. Separate settings
  utility compiled, producing the ninth artifact. Shared build lease used.
- Ten guard test cases pass: traversal, changed/missing/unlisted sources, modes,
  actions, protected output roots, existing-output refusal and fresh siblings.
- All37 frozen399 inputs and34 frozen401 inputs remain byte-exact.
- Source overlays and licenses retain original whitespace/bytes; scoped Git
  whitespace exceptions preserve upstream formatting rather than editing it.

Builds live under /home/paul/xbox-windows-native/build/public-layout402-<profile>001
in WSL (backed on C). No new work used D or changed E/console contents. Full
commands/source/tool/artifact hashes are in the component build records here.
The FATX binary differs from installed390 despite identical full source tree and
pinned compilers. No binary reproducibility or deployment qualification claimed.
Build logs remain with the fresh build directories; no guest/FTP operation ran.

## Limits and release status

This is a source/layout/docs/build improvement, not a new release/tag or public
visibility change. Full current HAL/network/input source correspondence,
anonymous dependency bootstrap, complete clean-machine installation and a
restore test remain open. The same-console stock-E migration tool is not a
fresh Windows installer. Private archives/history are not public release assets.

Physical E720p FATX390/software303/audio004 baseline and rollback remain unchanged.
720p text/dragging confirmation, unconfirmed stereo routing and strict Ft49 failure
remain distinct. No acceleration or1080i promotion. All owned build sessions closed.

Repository payload/credential checks passed33784 tracked files. Initial staged
source/license/evidence check confirmed469 byte-exact files. Git attribute
precedence initially normalized CRLF script input at staging; corrected rules
are last in the file and re-staging preserves executed bytes. Original working
files were not rewritten. Initial CRLF diff-check output is retained; corrected
diff check passes. No new guest or physical test was performed.
