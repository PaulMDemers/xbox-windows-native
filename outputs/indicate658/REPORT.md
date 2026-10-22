# 658: post-capture LED status and persistent UDP firewall

658 is prepared and staged; it has not launched. Closed657 received no UDP
datagrams, so its silence does not establish whether the exporter, admission,
sender or delivery path failed. This fresh diagnostic adds bounded LED status
after freezing the original display capture. It never starts Windows.

## Candidate and qualification

- Private source tree: `f3f58003dd6a988bcb4443ebd589f7ed33979e38`.
- XBE: 314736 bytes, SHA256
  `d67a7d9c355afc96509c501d9fab1aaf9c909cf34d62f04ce6d73290eef0d36d`.
- Staged/read back at `/E/Applications/XWNIndicate658/default.xbe`.
- `build001.json`, `host001.json`, `compiled-wrapper001.json`, `review001.json`
  and `controller-review001.json` preserve qualification and source pins.
- Host sanitizer checks pass, including all eight LED codes, bounded transaction
  failures and classification paths. The 119690 assertion count includes repeated
  polling callbacks; it is not a count of independent test cases.
- 83 exact linked caller cases pass with modeled display/MMIO/NIC/LED callbacks.
  The LED core is tested separately. Neither proves physical timing or delivery.
- 23 review checks pass, including 16 unchanged old module sections. Original
  capture, bridge, encoder, native admission and sender remain unchanged.

The new entry marker adds about six seconds before the network attempt. This is
an instrumentation timing change after capture, not a timing-neutral observation.
Signal errors are retained independently. Safe native cleanup permits one bounded
reset; unsafe cleanup or a failed reset holds. No firmware state, mappings, IRQ
state or admission gates are changed to make the probe pass.

## Watched indication

After packet freeze, green/off marks exporter entry for four seconds. Four result
signals then last ten seconds each, with two-second dark separators. These are
intended durations; physical timing is not yet qualified.

| Digit | LED signal |
| --- | --- |
| 0 | Solid green |
| 1 | Green/off |
| 2 | Red/off |
| 3 | Amber/off |
| 4 | Alternating red/green |
| 5 | Alternating red/amber |
| 6 | Alternating green/amber |
| 7 | Solid amber |

The four slots encode category, error high base-eight digit, error low digit,
and failed phase. Category 0 means three local completions, 2 admission rejection,
3 sender error, 4 unexpected/incomplete result, 5 unsafe cleanup, 7 encoder error.
Three local completions do not prove packet arrival. Ambiguous or missing visual
observations remain unknown; do not infer successful indication from a reset.

## Persistent firewall

The user explicitly authorized permanent rules for the development Xbox. The
first elevation request was canceled; `firewall-elevation001.json` preserves it.
The user subsequently ran `C:\xwn-network\Install.ps1` in Administrator PowerShell.
`firewall-install001.json` records successful creation at 20:48:55 UTC on
2026-10-22. `firewall-confirm001.json` independently verifies persistent and active
policy. The earlier `manual-install001.json` is preparation evidence, not an
execution receipt.

`tools/Set-XboxDiagnosticFirewall.ps1` manages the single named rule
`XWN-DevelopmentXbox-UDP50657`: inbound UDP50657 from the configured development
Xbox, on the resolved LAN interface, with any profile/program and edge traversal
blocked. It has no expiry and is intentionally retained after captures. This
removes the temporary-rule lifetime and Python executable filter as variables;
it does not prove external packet delivery or eliminate all filtering causes.

The private configuration is `C:\xwn-network\firewall.json`; no credentials are
published. Run the tool with `-Action Verify`, `Install` or `Remove` and a fresh
`-Receipt` path. Install/remove require administrative rights. A conflicting rule
is rejected, not silently widened. Remove targets only this named rule.

The existing offline sandbox block was inspected read-only. Its user scope is a
different local account from the current Paul receiver context. It was left
untouched; this is not proof about previous receiver identities or other filters.

## Lifecycle

28 selected files were captured twice before staging. Ordinary720p, ordinary
startup and savedXBOX480 remain protected. No startup hook was installed. A fresh
180-second listener and one 20-second-bounded SITE request are prepared. A watched
readiness record and active firewall verification are required before launch.
No receiver, capture or launch exists yet. All build/review processes are closed.
Console was reachable at staging; physical lease retained, build lease free.
Automation remains paused. Earlier closed attempts must not be rerun/recollected.
Historical Ftdisk49 and Popup26 remain unresolved. No Windows, normal restart,
NIC/DMA/cache/timer, GPU or full FATX health claim follows from these host checks.
