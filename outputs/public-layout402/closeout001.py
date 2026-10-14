from pathlib import Path
import json,hashlib
kit=Path('outputs/public-layout402')
report='''# Public-facing source layout and guides

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
'''
(kit/'REPORT.md').write_text(report,encoding='utf-8',newline='\n')
(kit/'NEXT.md').write_text('''# Next

1. Finish corresponding-source inventory for the exact installed HAL/network/input
   binaries, retaining separate proven configurations until a unified tree is tested.
2. Establish anonymous pinned-source/toolchain acquisition and a clean-machine
   build, then investigate build determinism separately from source reconstruction.
3. Design and validate owned-media provisioning in a disposable fixture; prove
   installation, first boot and restoration before calling it a fresh installer.
4. Curate a public tree/package with complete notices and source correspondence;
   scan contents and dependencies. Do not publish private Git history or archives.

Do not rerun402 consumed attempts or change frozen399/401 evidence. New build
outputs are disposable build workspaces borrowing upstream cache objects; retain
those caches while using them. No hardware work is queued by this task.
''',encoding='utf-8',newline='\n')
intro='''# Source layout and newcomer guides implemented (402)

Actual maintained source is now under src/ with six independent pinned profiles,
MIT-scoped original work and preserved upstream licenses. New portable tools/xwn.py
reconstructs exact full trees and builds selected components. Six fresh profile
builds plus the settings utility pass (nine artifacts); ten guard tests and49
local guide links pass.37 frozen399/34 frozen401 inputs unchanged. No physical
access, tag/publication or baseline changes. Build hashes are not asserted equal
to installed binaries. See outputs/public-layout402/REPORT.md and NEXT.md.

Remaining: complete HAL/network/input provenance, public dependency acquisition,
clean-machine build and disposable fresh-install/restore qualification. Current
working E720p demo remains unchanged. All owned build sessions closed.

'''
for name in ['CONTINUATION.md','STATUS.md']:
    p=Path('outputs/engineering-notes')/name
    p.write_text(intro+p.read_text(encoding='utf-8'),encoding='utf-8',newline='\n')
inputs=[Path('tools/xwn.py'),Path('tools/build_space.py'),Path('upstream/components.json'),Path('src/utilities/display-settings/settings.c'),Path('tests/test_xwn.py')]
(kit/'implemented-inputs.json').write_text(json.dumps({str(p).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},indent=2)+'\n')
