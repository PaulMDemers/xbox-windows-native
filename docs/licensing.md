# Licensing and public distribution

Original project code and documentation may use MIT, as authorized by the
project owner. The [root license](../LICENSE) is scoped by [NOTICE.md](../NOTICE.md):
it does not override upstream terms or remove existing notices.

| Material | Treatment |
|---|---|
| Original project tooling/documentation | MIT unless a more specific notice applies |
| ReactOS-derived files and changes | Retain each file's upstream terms and notices |
| Cromwell/Xromwell and changes | Retain upstream license and notices |
| AC'97 sample | Microsoft MIT notice; linked support code reviewed separately |
| Historical nxdk-derived code | Preserve its applicable notices; not blanket MIT |
| Windows/firmware/EEPROM/dashboard/user data | Excluded from public project assets |

[LICENSES](../LICENSES) holds preserved texts. [components.json](../upstream/components.json)
records the source bases and trees. Corresponding source must cover the actual
shipped binaries and their build configuration, not merely a similar upstream
revision. The [provenance guide](provenance.md) records the HAL/network source
profiles and exact owned-media matches for twelve Microsoft input components.
The latter remain excluded from public binaries. HAL and network correspondence
checks now pass outside timestamp/checksum metadata. The complete release export
and component-specific distribution obligations still require final review.

The repository is now public. Current downloads should contain maintained source,
build recipes, required notices, configuration tools and user guides. Historical
engineering records retain development-machine paths and private-network addresses;
they are not portable installation instructions. The reachable-history pattern
audit in [417](../outputs/tester-readiness417/REPORT.md) is a limited review, not
a comprehensive privacy or licensing clearance. History was not rewritten.

Windows payloads, product keys, user registries, firmware, EEPROMs, private
screenshots and recovery archives are not public project downloads. The tester
ZIP tool can package a locally prepared, user-owned Windows tree; it does not
grant redistribution rights or sanitize a previously used installation.

The hardware-report utility is original MIT code linked with nxdk libraries.
Its bundle includes the applicable SDK notices and source files with their
copyright headers. nxdk's terms remain in force; the project MIT license does not
relicense those libraries. The recorded build uses pinned, prebuilt nxdk libraries,
not an independently rebuilt SDK.

Before publishing binaries, complete component-by-component license review and
source correspondence, dependency acquisition and clean build validation. The
MIT choice for new work does not remove those upstream obligations.
