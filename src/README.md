# Source map

These are actual source files. Each component contains the files changed from
its pinned upstream base, at their upstream-relative paths. The build tool
supplies unchanged upstream files in a fresh checkout and verifies its complete
Git tree identity.

| Profile | Source | Purpose |
|---|---|---|
| `fatx` | [FATX](drivers/fatx/drivers/filesystems/vfatfs) | Files, directories, allocation, cache and paging |
| `framebuffer` | [Miniport](drivers/video/framebuffer/win32ss/drivers/miniport/xboxvmp/nt5), [boot video](drivers/video/framebuffer/drivers/base/bootvid) | Physical display handoff and boot drawing |
| `loader` | [FreeLdr](boot/loader/boot/freeldr) | Windows boot adaptations |
| `display` | [Software display](drivers/video/display/win32ss/drivers/displays/framebuf) | GDI drawing and framebuffer updates |
| `launcher` | [Xromwell](boot/xromwell) | Dashboard boot entry and video timing |
| `audio` | [AC'97](drivers/audio/drivers/wdm/audio/drivers/ac97) | Audio controller support |
| utility | [Settings](utilities/display-settings/settings.c) | Dragging and font preferences |

Overlays also include supporting HAL, header and build-system changes. Their
presence does not mean every target in that tree is the installed version.
Only the explicit targets in [components.json](../upstream/components.json)
are selected. Complete HAL/network/input release provenance remains unfinished.

Profiles contain different versions of some upstream paths. Keep them separate:
merging them without new builds and regression checks would discard tested
configurations. Unification is development work, not a file-move operation.

Edit files here, then follow [development](../docs/development.md). New files,
deletions and executable modes require explicit manifest updates. Existing
file edits can be built with `--allow-modified`, which records their new identity
instead of claiming the tested baseline. Original license headers are preserved.
