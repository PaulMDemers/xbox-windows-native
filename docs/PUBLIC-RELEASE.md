# Public source and tester readiness

The source repository is public. A public repository, a tester preview and a
qualified Windows installation are different deliverables. No new release tag
is implied by the tester kit.

## Available now

- Maintained source under `src/`, upstream pins and license notices.
- [Dependency setup and component builds](building.md). All eight profiles have
  been compiled with recorded tools; see the documented reproducibility limits.
- [Hardware inventory utility and tester instructions](testers.md).
- [Local bundle planning, creation and verification](tester-bundles.md).

Corrected inventory preview 421 has an emulator cold report readback and one
successful development-console run with a saved report and dashboard return.
Obsolete 417/417b utilities must not be used. Other encoders and revisions are
unqualified. The integrated Windows demo is physically tested on one 64 MiB
Conexant console. Other revisions are test targets, not supported claims.

## Windows bundle gates

| Gate | Current state / next evidence |
|---|---|
| Clean media | Customized SP4 assembly boots in xemu; six FATX long-name exclusions remain unresolved |
| Rebuilt boot chain | Full loader correspondence recorded; candidate temporarily activated for the pending 422 physical comparison |
| Registry/install | Fresh physical provisioning and strict event qualification remain incomplete |
| Display | E/720p first on the known configuration; 1080i text/motion defects remain |
| Recovery | Prepared-image restore tested offline; fresh-console FTP recovery is not qualified |
| Distribution | Public utilities/source separate from user-owned Windows/firmware and private recovery data |
| Multi-revision | Collect reports, then qualify each revision/encoder and cable combination |

Do not ship the current console's private recovery archive to other testers, or
present the six excluded files as resolved. A preview package needs an explicit
known-issues manifest, verified matched boot chain, unused prepared Windows input,
and a checked backup/restore route. Firmware flashing, formatting, dashboard
replacement and Xbox C installation are outside this workflow.

## Public history review

The 417 scan inspected 24,532 unique blobs reachable from local refs at
`904f6c67`. It found no binary/payload or supported token/private-key pattern
matches. It did find local paths, private-network addresses, email addresses and
credential-like expressions. Follow-up classification distinguished default
standard Xbox FTP defaults, environment-variable lookups and non-secret setup/test
expressions. These limited patterns do not prove the absence of every secret.
Author metadata, unreachable objects and remote-only refs were outside scope.

Historical evidence remains intact. Current user-facing commands should not
depend on development-PC paths. Before publishing any binary archive, verify
every entry and retain corresponding source, build identity and notices.
`tools/check-repository.py` checks tracked payload exclusions, not licensing.
See [417's report](../outputs/tester-readiness417/REPORT.md) for actual results.
