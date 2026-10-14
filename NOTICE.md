# License scope and provenance

The root [MIT license](LICENSE) applies to original project work, including new
documentation and original tooling, except where a file's notice or upstream
derivation requires other terms. It does not relicense upstream components.

- ReactOS-derived files retain their copyright and license notices. See
  [LICENSES/reactos](LICENSES/reactos). HAL, loader and driver modifications
  retain applicable upstream terms and corresponding-source requirements.
- Cromwell/Xromwell retains its notices and [license](LICENSES/cromwell/COPYING).
- The AC'97 sample has [Microsoft's MIT notice](LICENSES/audio-ac97.txt).
  Linked ReactOS support code can have different terms: the whole driver is
  not declared MIT merely because the sample is.
- The original settings utility retains its [MIT notice](LICENSES/utility-MIT.txt).
- Historical nxdk-derived experiments retain their own notices. The historical
  `outputs/` tree is not a curated public release.

[upstream/components.json](upstream/components.json) identifies the maintained
profiles and bases. No ownership of upstream work is asserted. Windows files,
keys, firmware, EEPROMs, proprietary dashboards and user data are not licensed
by this project and are excluded from public assets. See [licensing](docs/licensing.md).
