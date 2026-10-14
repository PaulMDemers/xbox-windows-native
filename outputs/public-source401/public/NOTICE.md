# Component provenance and license review

No blanket project license is asserted. The patches derive from the pinned
ReactOS and Cromwell trees. Reconstructing them preserves original file notices.
Upstream root license texts are copied unchanged under licenses/. The per-file
notices/ inventories record available header references for changed files and
their hashes. Missing header text is not a finding that a file has no license.

ReactOS includes multiple licenses. In particular, the AC97 source carries its
Microsoft MIT notice, copied under licenses/audio-ac97.txt, while its linked
ReactOS stdunk/support code has separate notices including GPL references.
The combined audio binary must not be labeled wholly MIT. Cromwell-derived
boot code retains its original notices and root copying terms.

The existing display selector and drag utility have MIT SPDX identifiers. The
new reconstruction and package-verification utilities also use MIT, with its
text in licenses/utility-MIT.txt. That permission does not relicense driver,
loader, upstream support code, Windows or other unrelated components.

Before publication, finish manual per-file and linked-component attribution and
license compatibility review, including new historical patch additions without
an explicit header. Confirm source-cache upstream availability and distribute
the corresponding source needed by any future binary release. This draft does
not make a legal clearance or license-compatibility determination.
