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
revision. The current complete HAL/network/input inventory remains unfinished.

A public export should include maintained sources, reproducible build recipes,
required notices, configuration tools and user guides. It must exclude private
Git history, machine paths, credentials, proprietary media, user registries,
screenshots containing private data and recovery archives. The current source
layout is preparation for that export, not a declaration that the entire private
repository is cleared for publication.

Before publishing binaries, complete component-by-component license review and
source correspondence, dependency acquisition and clean build validation. The
MIT choice for new work does not remove those upstream obligations.
