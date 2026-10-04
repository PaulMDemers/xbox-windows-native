# Physical B4 reproduction and framebuffer PCI candidate

The cycle008 photograph again shows B4(0,0,0,50000). Its persisted trace has
24 records, including a successful AddDevice return followed by optional PnP
queries. The Win32 startup report is still pending. The trace was preserved
before resetting its seed for cycle009.

The physical GPU's Windows-generated requirements include three memory ranges:
16 MiB of registers, a 128 MiB prefetchable framebuffer aperture, and an additional
unassigned 512 KiB prefetchable range (BAR2). The bridge's prefetchable window is
F0000000–F7FFFFFF, exactly the size occupied by BAR1. The earlier suspicion that
the framebuffer itself lay outside the bridge window is disproved by the trace.

The pinned xemu NV2A implementation exposes BAR0 and BAR1 but no BAR2. A separate
resource-model executable adds two selectable experiments without replacing the
shared emulator. It keeps the emulated RAM at 64 MiB. The extra range is an alias
used only to reproduce PCI resource requirements; this is not a complete physical
GPU model, and no claim is made about the real BAR2's purpose.

| Ordinary emulator run | HAL | GPU model | Result |
| --- | --- | --- | --- |
| resource-extra-001 | Baseline | 128 MiB BAR1 + 512 KiB BAR2 | Same B4 and same callback/status sequence as physical cycle008 |
| resource-control-001 | Baseline | 128 MiB BAR1 only | Desktop, probe PASS, cold audit PASS |
| framebuffer-pci-extra-001 | Candidate | 128 MiB BAR1 + 512 KiB BAR2 | Desktop, persisted probe PASS, cold audit PASS |

Full run IDs begin `nt5-physical-f-`. There were no debugger execution changes.
Both successful cold audits checked 6,495 files, including 3,439 immutable
binaries, the probe's 65,537-byte payload, allocation ownership and registry
integrity. The candidate desktop was captured, but its normal reboot was not
visually captured before the harness ended. Physical cycle009 is a separate test.

Correction to the initial trace interpretation: absence of a logged START_DEVICE
event alone does **not** prove that Windows never sent one; the successful control
also lacks that event. The paired resource experiment, the complete callback
sequence and the actual boot outcome provide the stronger evidence here.

## Candidate and limits

Patch0074 introduces default-OFF `XBOX_NT5_FRAMEBUFFER_ONLY_PCI`. With the option
enabled, the HAL latches the exact observed GPU identity/header/BAR layout under
its existing PCI lock. Only for that layout, BAR2 reads return zero and writes to
its four configuration bytes are suppressed. All surrounding bytes use the
existing hardware access path. The HAL does not size, assign or reprogram BAR2,
copy another machine's bridge configuration, or change BAR0/BAR1 behavior.

This is a compatibility view for the current framebuffer miniport, which uses
BAR0/BAR1. It must not be enabled for an accelerated GPU driver that needs BAR2.
Different devices/layouts, an already assigned BAR2 and normal xemu's absent BAR2
pass through unchanged. The clean patch series replays to tree
`da47c938fb0f3c334274f79230b46bff8c4f7902`.

Compiled HAL tests cover every one of 1,617 header intervals for both reads and
writes, mismatched layouts and buses/functions, guard latching before sizing,
and zero-length requests. Disabling the option preserves the baseline code and
imports except three embedded debug source-line numbers moved by the new block.

Candidate HAL SHA256:
`a3a84368d59936dfa6bbcdc6d5839d57b886342211142d305e9dde941e4d1648`.
Baseline HAL SHA256:
`59c889e177cee82e34c8ded326bffc33a659881031d3e0f7a9616d69c77447eb`.
The trace miniport remains `413098acf0066e48fde515b75d825578c23c17c4094ec2341ebdaa314a2d6b13`.

See `framebuffer-pci-validation.json`, `framebuffer-pci-tests.json`, the three
decoded trace files and `physical-gpu-requirements-008.json` for evidence.
`physical-cycle-009.json` records deployment and launch status independently.

## Reproduction and retained state

`Build-ResourceModel.ps1` builds the isolated xemu executable under the shared
build lease, then restores the two borrowed source files byte-for-byte. Its
scratch object cache contains the experimental build; the installed emulator and
original source checkout are unchanged. Use `XWN_NV2A_RESOURCE_MODEL=128-only`
or `128-plus-extra` only with this executable and its recorded hash.

`Build-FramebufferPci.ps1` builds the opt-in HAL. `Build-FramebufferDefault.ps1`
builds the default-OFF comparison; this is the current build-cache configuration.
`prepare-framebuffer-pci.py` creates a small delta changing only the existing HAL
file in an owned emulator fixture. It never operates on a physical disk.

Retain these backing images while their overlays exist:

- `artifacts/physical-video-trace-001.qcow2` (base, SHA `4c2f9bb7e000732401105f9600f311628e81dc8d5fef088a256c6021f9a248c8`)
- `artifacts/physical-framebuffer-pci-001.qcow2` (HAL delta, SHA `02e123d1cbab7b0b9c5207adecd43049aa459b097f29ec2ea15ad7d3424256af`)

The run overlays and screenshots are retained under `work/runs`. Firmware,
Windows files, raw traces and executable payloads remain untracked local inputs.


## Physical result after the emulator checks

Cycle009 passed on the physical Xbox. The saved Win32 startup report reports
zero failures and successful 65,537-byte create/write/flush/reopen. Dashboard FTP
returned the exact expected payload (SHA256
`c4bf3fb66f84ed12a3f529c2ac489b0dd72a6b749de38e9bbe52d433593f8c65`).
The report SHA256 is
`2bca82800ee575e20aee11d4d98ac9dbd386a7908668086eb6c060aa0ea0f41c`.
The installed HAL and miniport hashes were rechecked, and all 41 trace records
were preserved. Launch was 21:06:49 UTC; report collection was 21:08:54 UTC.
This establishes actual physical user-mode startup and bounded native FATX IO.
A desktop photograph and physical input validation are still separate steps.


## Desktop viewing launch

The normal miniport (72d33d...) and a no-op startup command were also validated
in the extra-resource emulator. Two captures show the Windows desktop with its
welcome and new-hardware wizards; it remains running instead of invoking the
probe/restart. That emulator is closed.

The identical configuration was readback-verified on the physical console and
launched once at 21:16:47 UTC. The diagnostic miniport is retained as
F:/winnt/system32/drivers/xboxvnt5.xwn-trace9, and the old startup command as
F:/xwn-startup-v2.bak. The cycle009 report, payload and trace are preserved.
A physical desktop photograph is pending. Do not treat the preserved cycle009
report as a fresh result of subsequent desktop boots. The normal miniport no
longer requires an empty trace seed.

An additional small immutable backing image, artifacts/physical-desktop-001.qcow2
(SHA 3b355cf0cba4aa8794a62e3a707767e44f3989a0ba5b5c383bff2382040ed62c),
depends on physical-framebuffer-pci-001.qcow2 and supports the desktop run overlay.


## Desktop regression and controlled retry

The desktop001 photograph (7E717C50..., SHA256 recorded with the run) shows
B4(0,0,0,50000) again. Post-photo FTP readback confirms the intended candidate
HAL, normal miniport and no-op startup command. The inspected video registry
entries match the successful cycle009 snapshot. Therefore cycle009 remains a
valid physical user-mode/file-IO success, but the normal-driver combination is
not yet reliable on hardware. The emulator-only normal-driver result does not
establish physical desktop success.

Cycle010 restores the exact 413098... trace miniport that passed cycle009,
keeping the same HAL and the automatic startup probe/restart disabled. The old
trace was preserved locally before reseeding. The normal driver is retained as
F:/winnt/system32/drivers/xboxvnt5.xwn-normal10. All changed files were read back;
one FTP launch was accepted at 21:20:47 UTC. A physical photograph is pending.
This isolates the driver configuration from the startup command. Timing, callback
wrapping and other diagnostic side effects have not yet been distinguished.

The trace driver again requires an empty seed for each launch. After the user
reboots, collect-video-trace.py --cycle 10 preserves its trace. Do not launch a
second time or overwrite the trace before collecting it. The old cycle009 probe
report remains preserved and is not evidence of a new cycle010 probe run.
