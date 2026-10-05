# Public repository preparation

Status: preparation only. The private repository and immutable v0.1.0 remain
the recovery/evidence history. No visibility change or upstream submission is
part of this preparation. The local system archives include Windows, dashboard
and user data and are not public release assets.

## Deliverables and gates

1. **Public source set.** Start from a reviewed export of the current patch
   manifest, parameterized build tools, focused tests and edited engineering
   notes. Retain source copyright/license headers and attribution. Make a
   per-component provenance/license inventory for ReactOS, Cromwell, nxdk-derived
   tools and original scripts. Do not apply one blanket license to derived code.
2. **Data review.** Audit every proposed file and every revision that would be
   made public. `tools/audit-public-readiness.py` inventories patterns across
   reachable local history without emitting matched values. It complements the
   current tracked-payload check; neither proves secret/provenance clearance.
   Remove machine paths, console addresses, credential literals, personal event
   data and private attachment references from a new public export. Review Git
   author metadata without stripping required upstream author attribution.
3. **Input boundary.** Public builds consume source pins and redistributable
   dependencies. Windows media, firmware, EEPROM, dashboard and saved profiles
   remain user-provided local inputs. Packaging must verify identities without
   redistributing these files or embedding local credentials.
4. **Fresh reconstruction.** Establish one-command source replay and compilation,
   then extend it to launcher, all installed custom drivers, config generation
   and a package manifest. Test from an empty output directory and document the
   host prerequisites. Run a second independent build and explain binary changes
   (timestamps, paths or generated data) before claiming deterministic binaries.
5. **Public documentation.** Short quick start, supported hardware/cables, exact
   experimental scope, known failures, recovery steps, test commands, contributor
   guide and issue template. Publish bounded evidence, not an implied stable OS.
6. **Release review.** Inspect a final archive including its licenses and hashes;
   verify that its build/deploy instructions match the intended artifact. Only
   then decide with the user whether to publish a new sanitized repository or
   undertake a separately backed-up history sanitization of this one.

## Preferred initial route

A new sanitized source export is the least disruptive route: keep this private
forensic history, failed experiments and v0.1.0 tag intact, while presenting a
small auditable public tree. That is a proposal, not an action taken. Simply
changing this repository's visibility would expose historical contents too.
No history rewriting is needed to continue development here.

## Current tools and remaining work

The reconstruction recipe is in [reproducible-build](../reproducible-build/README.md).
The installed reusable skill has a versioned copy under
[developer-skills](../developer-skills/README.md). The existing
[FATX handoff](../engineering-notes/FATX.md) is the starting technical note for
Linux maintainers; it needs the same public-data/provenance pass as other docs.
Run and inspect the history audit before selecting the public files. None of
these checks constitutes legal clearance or a complete security audit.

The initial [history audit](history-audit-001.json) scanned 2,790 unique reachable
blobs at private commit f0b10e4. It flagged 772 for machine paths, 172 for private
IPv4 addresses, 142 for credential-literal review and two for email review.
Categories overlap and include historical versions; these are not counts of
distinct secrets. No binary/payload or token/private-key pattern hit was found
by these limited rules. Required copyright/author email attribution must not be
removed merely because it matched. New uncommitted work is outside that scan.
