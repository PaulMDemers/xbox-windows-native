from pathlib import Path
files = {
'docs/installation.md': '''# Installation and first boot

There are two different starting points. An already configured Xbox can use the
integrated demo now. A fresh Xbox still needs a qualified provisioning workflow;
this repository does not yet offer a general Windows-from-CD/ISO installer.
Building the drivers alone does not create a bootable Windows installation.

## Already configured demo

1. Connect the mouse before boot. Keep a keyboard known to hang Xromwell
   disconnected until Windows appears; the Razer keyboard did so during testing.
2. In UnleashX, choose **Windows**. For the current E installation its executable
   is `E:\\Applications\\XWNEBoot\\default.xbe`.
3. Windows should reach the desktop. Close unsupported-device wizards without
   disabling devices. These prompts are not evidence that all those devices
   have working drivers.
4. Use applications and save work on Windows C. Choose full-window or outline
   dragging using the supplied shortcuts; see [display settings](display-configuration.md).
5. Use Windows **Start → Shut Down → Restart** to return to the dashboard.

The normal demo has no benchmark or automatic timed restart enabled.

### Partition mapping on this E installation

| Dashboard namespace | Windows view/use |
|---|---|
| E | Windows C: system, applications and demo files |
| F | Original installation/rollback; preserve it |
| C | Dashboard/system files; appears as Windows F in this installation |

**Do not use Windows F as scratch.** It maps to the protected dashboard C here.
Do not assume these letters on a different console; verify its mapping first.
The host PC's C/E drives are unrelated to Xbox partition letters.

### Launch menu

If the menu starts an obsolete profile or a blank screen, first use UnleashX's
file explorer to inspect the intended E launcher. An authorized menu update
should change only the Windows item's launch action to the exact path above,
preserve the previous configuration and reload UnleashX. The old
`E:\\Applications\\XWNFBoot\\default.xbe` selects a different Windows installation.
Do not replace dashboard configuration from another machine.

## Fresh Xbox: what is still required

The intended route uses dashboard E so it can support stock-size disks, with F
optional for additional storage/rollback. It needs:

- An Xbox able to run the launcher, a working dashboard and compatible display
  path; the tested console has 64 MiB and a Conexant encoder.
- Your own Windows installation materials and appropriately obtained firmware
  for any emulator testing. Neither is distributed here.
- A matched launcher/loader/HAL/driver set, prepared Windows registry and files,
  a verified partition layout and sufficient space.
- A recoverable dashboard, preserved console-specific data and verified backups.

The existing [stock-E migration tool](../tools/install-stock-e.py) is an
engineering tool for a same-console captured baseline. It is **not** a fresh
Windows installer. Its create-only guards, capacity checks, launcher-last
ordering and readback journal have host tests; a complete disposable-fixture
install/restore qualification is still pending. It must not be used to overwrite
an occupied installation or to install someone else's private system archive.

A newcomer-ready installer remains a release requirement: independent source
and dependency retrieval, complete HAL/network/input provenance, owned-media
assembly, configuration, disposable installation and recovery testing. This
page deliberately provides no destructive fresh-disk recipe ahead of that work.

## Updating an existing installation

Use only a package explicitly naming your installation and prerequisite hashes.
Save work, return to the dashboard, preserve the exact previous bytes and verify
both upload and readback. Deploy the launcher last when an update needs one.
A compiler-success result alone is not hardware qualification. Keep rollback
separate and read [recovery](recovery-guide.md) before modifying the boot chain.
''',
'docs/display-configuration.md': '''# Resolution and desktop preferences

Use **720p** for the current demo. Text and full-window dragging were confirmed
clean on the tested console/adapter/display. At 1080i, photographed text had
missing-looking strokes and dragged contents jostled, although a saved Windows
screenshot looked clean. The cause has not been isolated to timing, scanout,
adapter or TV processing. Font smoothing is not a demonstrated fix for it.

Resolution is selected at boot. Windows Display Properties is not a supported
way to switch these profiles while Windows is running. An HDMI connector alone
does not establish the adapter's supported Xbox signal modes.

## Change the current E profile

Use an extracted, matched demo preview package with its `resolution/` binaries
and policy. The source checkout alone does not contain those binaries. Save work
and return to UnleashX. Supply dashboard FTP credentials through process-local
`XWN_FTP_HOST`, `XWN_FTP_USER` and `XWN_FTP_PASSWORD`; never commit them.

```sh
python tools/configure-e-display.py inspect --policy tools/e-display-policy.json
python tools/configure-e-display.py apply --policy tools/e-display-policy.json --profile 720p --launcher resolution/720p/default.xbe --receipt rollback-720p-001
```

The receipt must be a new directory. The selector verifies installed
prerequisites, captures the previous launcher, writes only the E launcher and
verifies readback. It does not launch Windows or modify EEPROM flags. Boot the E
entry afterward and check text, borders, colors, signal and actual dimensions.

Restore the exact previous launcher with:

```sh
python tools/configure-e-display.py restore --policy tools/e-display-policy.json --receipt rollback-720p-001
```

An explicit diagnostic 1080i selection uses `--profile 1080i` and the package's
`resolution/1080i/default.xbe` with a fresh receipt. It remains experimental.
The older `deploy-hd.py` targets the F installation; do not use it against E.

## Dragging and text preferences

The existing demo provides **Full window dragging.cmd** and **Outline dragging.cmd**
in `C:\\xwndemo372`. That is a guest path, not a required host build location.
The utility can also be invoked from its directory:

```bat
display-settings.exe status
display-settings.exe full
display-settings.exe outline
```

Changes apply immediately and persist for the current user through Windows
system-parameter APIs. They do not change drivers, GPU ownership or cache state.
At 720p, full dragging is a usable choice; outline avoids repainting while moving.
The utility source also documents its font-smoothing options. Those preferences
do not qualify an unresolved display mode.
''',
'docs/troubleshooting.md': '''# Troubleshooting

| Symptom | First checks |
|---|---|
| Blank screen after choosing Windows | Confirm the menu points to the current E launcher, not an old F profile; inspect through the dashboard file explorer |
| Xromwell hangs before Windows | Disconnect the keyboard that caused prior boot hangs; keep the mouse connected before boot |
| No mouse after hot-plugging | Input discovery can be blocked by hardware setup; connect the mouse before the next boot |
| Found New Hardware wizards | Record the device name; cancel unsupported devices without disabling them |
| Broken-looking text or moving window contents at 1080i | Return to the matched 720p profile; this was clean in the user comparison |
| Normal text at rest but repaint visible while dragging | Try outline dragging; the desktop is software-rendered |
| Build refuses a changed hash | Inspect the source/tool difference; use explicit development mode for source edits, not an arbitrary compiler substitution |
| Build output directory already exists | Preserve its log and use a fresh attempt directory |
| Resolution selector refuses prerequisites | Stop and identify the installation/package mismatch; do not bypass hashes |

If Windows is responsive, save work and restart normally. If the dashboard is
offline, that alone does not prove a crash: Windows may simply still be running.
Record the actual screen and whether a restart was normal or forced.

For a useful issue report include console revision/encoder if known, RAM,
adapter and display, requested/observed mode, exact package or source tree,
last successful configuration, steps, and expected versus actual result.
Photographs and saved screenshots are different evidence; include both when
investigating presentation defects. Remove credentials, product keys, personal
files and console-specific secrets from logs before sharing.

The retained Ftdisk 49 event is a failed strict gate, not silently ignored because
the desktop works. Historical emulator dump-path fixes and the current physical
configuration are separate results. See [development](development.md).
''',
'docs/recovery-guide.md': '''# Recovery and rollback

Preserve a working dashboard, original launchers, matching loader/driver bytes,
console-specific recovery material and your own saved files before updates.
Record hashes and partition names; do not assume Windows and dashboard letters
match. On the current E demo, Windows F maps to dashboard C and is not scratch.

## Display rollback

Return to UnleashX and use the display selector's captured receipt to restore
its previous launcher. If an interrupted upload leaves an unrecognized launcher,
preserve the receipt and restore its verified `before.xbe` to the receipt's
exact E launcher target through dashboard FTP. Do not substitute an F launcher.
A no-signal Windows boot must return to the dashboard before this recovery works.

## Driver or installation rollback

Use the exact previous files for the same installation, with upload/readback
verification. Preserve the original F installation separately from E. Do not
restore a private system archive over an occupied installation as an upgrade.
Restore user data only after confirming the destination mapping.

The project's private recovery archives were readback-verified, but are not
whole-disk images and have not passed a full-system restore test. They contain
historical Windows/user material, not necessarily the latest saved files, and
must not be published. Archive integrity is not proof of successful recovery.
A disposable install-and-restore test remains a public release prerequisite.
''',
'docs/development.md': '''# Development workflow

Start with the [source map](../src/README.md) and [build guide](building.md).
Change the smallest relevant component. Keep source revisions, compiler settings,
output hashes and test scope together. Profiles remain separate until a combined
source tree is deliberately built and qualified.

## Editing a profile

1. Run `python3 tools/xwn.py verify` on the baseline.
2. Edit the actual file in `src/`. Preserve upstream notices.
3. Build into a fresh directory with `--allow-modified` for existing listed files.
   New files, deletions and mode changes need explicit manifest updates.
4. Inspect build logs and the recorded tree/artifact hashes. Do not equate a
   successful build with binary reproducibility or deployment readiness.
5. Add a test that distinguishes the intended behavior from the defect. Prefer
   a disposable emulator fixture before a physical trial.
6. Preserve the failed attempt and its inputs; use a new attempt for corrections.

Use `python3 tests/test_xwn.py` for the portable command's guard tests and
`python3 tools/check-repository.py` for tracked payload/credential checks. On
shared development machines, acquire the existing build/emulator/hardware lease
and coordinate ownership before using those resources.

## Evidence levels

Host models prove only their modeled contracts. A debugger observation is not an
ordinary guest run; a synthetic API replay is not a user exercising Paint.
An emulator result is not physical-console qualification. Record what actually
ran, where, with which source and binaries, and what remains uncertain.

For persistence changes, verify exact final contents, absent intermediate files,
allocation consistency, relevant hives/protected files, shutdown and event deltas.
Never turn a scoped success into a strict pass by suppressing failed event gates.
A clean metadata audit alone is not a full file-content comparison.

For graphics, separate guest framebuffer contents from displayed output. Require
actual ownership, synchronization and content preservation before experiments
that release renderer resources or hand control to a new GPU path. The emulator
resource-lifetime experiments are not installed native acceleration.

## Before public release

Finish the complete HAL/network/input source inventory, verify anonymous upstream
and toolchain acquisition, validate builds in a clean environment, and qualify a
disposable owned-media installer and restore. Review per-component licensing and
corresponding source, then export a curated tree without private history or data.
Do not publish the historical `outputs/` directory wholesale.

Historical evidence remains in `outputs/`. New users should not need machine
paths, experiment IDs or private archives to understand the project. Maintain the
public guides separately from immutable test records.
''',
'docs/licensing.md': '''# Licensing and public distribution

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
'''
}
for name, text in files.items():
    Path(name).write_text(text, encoding='utf-8', newline='\n')
