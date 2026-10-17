# Resolution and desktop preferences

Use **720p** for the current demo. Text and full-window dragging were confirmed
clean on the tested console/adapter/display. At 1080i, photographed text had
missing-looking strokes and dragged contents jostled, although a saved Windows
screenshot looked clean. A later pattern test also found exact pixels and no
shadow-to-framebuffer mismatch at eight checkpoints in each mode, including
after window movement. That does not verify the interlaced signal reaching the
TV. Timing, encoder, adapter and TV processing remain under investigation.
Font smoothing is not a demonstrated fix for it.

A standalone test through the stock Xbox video API also produced correct
framebuffer pixels, while the tester reported clean 720p and solid alternate
bands at 1080i. The visual issue therefore also occurs without Windows running.
1080i remains experimental; this is not evidence of a completed fix or a faulty
adapter specifically. Follow-up photos show the one-line stripe area collapsing
to black or white, paired with its magenta/green row-parity marker, while two-line
stripes survive. This is consistent with field-based processing or lost alternate
row detail, but still photos cannot establish permanently missing fields or
identify which device is responsible.
The tester also sees green/purple alternation and black/white flashing during
movement, so this is not solely a camera artifact. Moving unchanged pixels by
an odd number of rows can produce those swaps when output processing selects
one row parity at a time; the responsible processing stage remains unconfirmed.

A fresh run of the same standalone test on a second display produced the same
reported artifact, with exact captured pixels. This makes a TCL-specific cause
less likely, but the adapter and Xbox interlaced output have not been isolated.

Normal PBKit graphics initialization also left the artifact unchanged in a
watched comparison using the same framebuffer. Its captured address-mode change
from 3 to 2 is not a demonstrated fix. The investigation is paused; see the
[1080i findings and resume criteria](1080i-investigation.md) for the consolidated
evidence. No further display test is queued.

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
in `C:\xwndemo372`. That is a guest path, not a required host build location.
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
