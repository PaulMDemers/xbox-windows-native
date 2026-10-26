# 682: incoming console composite baseline

The user identifies the incoming console as revision 1.6. They clarified that
the first requested test is **480i over composite**, followed by HDMI/720p.
The prepared680 progressive-only tool was not used for the composite test.

A separate kernel-assisted SD build requests720×480×32 at60Hz only for a
standard AV pack and NTSC-M/J. It retains the owned SDK framebuffer guard,
exclusive checkpoint files and20-second pattern. The progressive geometry
comparison is recorded rather than used to reject an interlaced mode; it checks
dimensions/stride/format, **not whether the signal is progressive**. No native
Xcalibur programming, Windows boot, EEPROM change or startup hook is involved.

`host001.json` records3,145,728 compiled admission assertions. The pattern helper
is byte-identical to the sanitizer-tested681 helper. `build001.json` pins the
compiled XBE and source. Stage readback verified the exact bytes under the new
owned E path. The shared build lease was used and released.

## Actual launches and collection

- One agent SITE launch was accepted. The first FTP collection and a later
  connection check timed out; both failures are retained. The user initially
  reported seeing only the dashboard.
- The user independently launched the staged XBE manually and saw the colored
  bars display properly. They confirmed automatic return to UnleashX and said
  the first run was probably missed. No agent retry was sent.
- Collection002 recovered six new reports in two complete sequences:00–02 and
  03–05, each containing pre-mode, pattern-submitted and restart-requested phases.
  Every report was read twice and matched. This establishes two application
  sequences; only the manual run has a direct visible-pattern observation.
- Both report720×480×32/60, pitch2880,64MiB, kernel1.0.5838.1 and standard AV pack.
  The user did not separately confirm every border/stripe detail or provide a
  display input-information readout. No detailed image-fidelity claim is made.

The current raw GPU revision is0xd3 and MCP revision0xd5. The older630 inventory
reported GPU0xe1. Keep these reports distinct; raw fields are not a revision
decoder. The user revision label remains the provenance for1.6. The present
tool does not positively identify the encoder.

Owned staged files remain exact, and unrelated E-root/application directory
entries are unchanged. This is not a whole-volume audit. No console C files,
Windows hives, ordinary launcher or startup were accessed. The FTP greeting
itself lists free space for all drives; that is not a C filesystem traversal.
The owned tool and six reports remain on E; no hook requires removal.

The user's requested FTP defaults were added only to the private local Xbox
development skill, with session-specific addresses and explicit overrides.
Both skills pass validation using existing WSL PyYAML. The unavailable Windows
PyYAML validation attempts are recorded; no packages were installed and no
credentials were committed.

Next: switch cables with power off, confirm HDMI readiness, then use a fresh
683 attempt for the720p kernel baseline. These results do not qualify the
native Xcalibur driver or Windows installation on this unit.
