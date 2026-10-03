# Native Windows 2000 on the original Xbox: development checkpoint



Development checkpoint: 3 October 2026, 09:00 EDT. See the evidence timestamps for individual observations.



**Windows 2000 boots to an interactive desktop on the 64 MiB Xbox hardware model in xemu.** The tested chain is UnleashX → Xromwell → experimental FreeLoader → Microsoft's Windows 2000 kernel and desktop. Autorun boots require no debugger intervention. The physical Xbox has not been tested.



![Windows 2000 and a working USB Start menu after the extended run](evidence/nt5-kernel-051/late-keyboard-menu.png)



## Current reproducible baseline



Run the hash-checking [Run-Desktop.ps1](Run-Desktop.ps1) from PowerShell 7.4; details are in [REPRODUCE.md](REPRODUCE.md). Use `artifacts/kernel-autorun-006.iso` with `artifacts/windows2000-integrated-001.qcow2` for the desktop, USB, Ethernet, audio and endurance baseline. The private 12 GiB emulator disk preserves the dashboard's FATX area and places Windows' NTFS partition at 8 GiB. It is **not an image to write over the physical Xbox disk**. The separately retained original Windows installation is unchanged. No additional ISO is needed for current development.



The installation came from the user-supplied OEM `Windows 2000 (SP4).iso`. The other supplied SP4 media also provides original Microsoft driver files. Neither Windows media nor installed Windows binaries belong in a public source release.



| Component | Observed result | Limits |

|---|---|---|

| Loader and NT 5.0 HAL | Repeated native kernel and desktop boots, 15,359 usable pages | Experimental; physical firmware and memory map unverified |

| IDE storage | Microsoft PCIIDE/ATAPI enumerates disk and DVD; 4 MiB write/flush/reopen/read comparison passes | Private emulator disk only |

| Display | Custom NV2A miniport plus Microsoft's framebuf.dll, 640×480×32 desktop | Retained firmware framebuffer; no acceleration or mode switching |

| USB | Original Microsoft OHCI/HID keyboard and mouse; Start menu and pointer respond | Emulated USB peripherals; Xbox gamepad unsupported |

| Ethernet | Native NDIS 5.0 miniport, DHCP, 136 pings with zero reported loss, three disable/enable cycles | Isolated virtual network; single transmit buffer; physical PHY/DMA unverified |

| Audio | 48 kHz stereo playback; thirty open/play/close cycles and thirty captured test tones | Prototype for the emulator codec; physical Xbox codec support remains separate |



## Latest validation



Run 043 boots the complete dashboard chain with the corrected HAL and stays at the desktop for the ten-minute run. Its guest log records zero failures: a 4 MiB disk comparison, twenty retention checks of an 8 MiB allocation, and Notepad message responsiveness. Windows reports 120 successful pings before three adapter disable/enable cycles and another sixteen afterward. The late screenshot retains the Start menu opened by injected USB keyboard input. These are bounded checks, not a general stability certification.



Runs 034 and 036 previously passed the same network cycles and 136-ping sequence using the latest bounded-copy Ethernet driver. Runs 035 and 041 exposed intermittent USB initialization stalls. The HAL had reported PCI interrupt resources as level-triggered even where the PIC's ELCR configured edge triggering. It now translates each PCI interrupt according to the actual ELCR bit, preserving unrelated flags. Runtime inspection confirms edge-triggered USB IRQ 1 and IRQ 9; runs 042, 043 and 045 reach the desktop. Run 046 also passes through direct Cromwell boot. The corrected HAL is retained in subsequent audio and combined tests.



The loader also stops advertising a nonexistent floppy controller. Shared PC enumeration had reserved IRQ 6 for that phantom device, conflicting with Xbox audio. The Xbox NT5 path retains disk geometry information while omitting the fabricated floppy node.



Run 047 completes the first 48 kHz, 16-bit stereo waveOut test. Windows reports a completed 96,000-sample buffer before reset; the captured waveform contains the expected two-second 400 Hz tone. Binding the native Microsoft SysAudio, KMixer and WDMAud software devices was necessary after installing the hardware miniport. Run 045 had already started the hardware device but exposed no waveOut endpoint. An earlier prototype wrote unsupported surround codec registers and triggered an xemu assertion; the current prototype rejects those writes and recording streams.



Run 051 boots the complete dashboard chain and remains at the desktop through ten minutes. Thirty independent audio open/play/close cycles each complete all 96,000 samples, with zero diagnostic failures and thirty corresponding tone segments in the capture. The concurrent disk, memory and GUI diagnostic reports zero failures. Windows receives all 136 pings across three Ethernet disable/enable cycles, matching the packet capture. USB Ctrl+Esc still opens the Start menu late in the run.



Run 052 repeats the combined test after another boot: thirty completed audio buffers and thirty captured tones, all 136 pings received, three adapter cycles, and zero disk/memory/GUI diagnostic failures. Together runs 051 and 052 provide sixty playback cycles and 272 successful ping replies. See `integrated-milestone.json`.

Shutdown remains unresolved. Runs 053 and 054 close Explorer after the privileged shutdown request, but service processes and kernel ticks continue. No completed shutdown or power-off is claimed. A read-only thread snapshot in run 054 places winlogon thread 160 in an in-page wait with PortCls code addresses on its kernel stack. These are scanned address candidates rather than a validated stack unwind; audio power handling and paging/storage completion are investigation leads, not established causes.

That repeated boot also uncovered and fixed an NTFS loader limitation. Installing audio grew SYSTEM beyond its first DATA attribute extent. The prior loader silently accepted a partial read and left its final 20 KiB missing. The on-disk hive had matching sequence numbers, a valid checksum and 5,305 readable keys. The revised file reader resolves later extents through ATTRIBUTE_LIST, respects their VCN boundaries, and rejects short underlying transfers. Hive loading now also checks the exact read count. The same unchanged disk that failed in runs 048–050 reaches the desktop in run 051. Six compiled-code tests cover spanning reads, unaligned boundaries, seeking into a later extent, EOF, missing extents and short disk I/O. This does not add compressed-file support or make malformed NTFS volumes safe.



## Implementation and source recovery



The HAL implements the Windows 2000 import/dispatch boundary, NT 5.0 interrupt translator, root PCI resource windows, and Xbox interrupt behavior. The loader creates the native NT5 handoff and reserves the retained framebuffer. Microsoft's kernel and supplied storage/USB drivers remain original binaries.



The offline registry helper converts reachable hivex lh indexes into Windows 2000-compatible li indexes without changing keys, types or values. Its checks cover full logical equality, an unchanged original hive, and idempotence. Fixture builders verify inserted file readback, source preservation and qemu-img consistency, and remove temporary raw partitions.



The Ethernet variant uses the older NDIS DMA interface accepted by Windows 2000, validates packet lengths before copying to a contiguous transmit buffer, handles serialized send ownership, and drains UP DPC work before teardown. Its build is isolated from the ordinary ReactOS driver. The audio variant is separately gated and maps the Xbox ACI BAR as memory instead of PC-style port I/O.



Apply the ordered patch list in `patch-check-0017.json` to ReactOS commit `afc0127e8f937ab68503d715d948844973756aa1`. The complete chain, including audio and the NTFS fix, produces verified tree `d98c8e753aff951f620a15d1d0eb118506b59176` and matched the working source tree at that checkpoint. Ordinary FreeLoader, HAL, boot video, Ethernet and AC97 targets also rebuild with every experimental option disabled.



Binary checks include the existing HAL boundary, interrupt and debugger tests; ten interrupt-translator groups; six root-resource groups; eight framebuffer groups; seven Ethernet groups; four AC97 MMIO groups; and six NTFS extent groups. Their JSON reports identify the tested binaries and assertions. Import audits resolve the installed Windows kernel/HAL/video/NDIS/PortCls interfaces. These modeled tests complement, and do not replace, emulator observations.



Invoke-Diagnostic.ps1 creates private managed xemu instances, disks, EEPROM copies and loopback-only test ports. Completed evidence and guest logs are under evidence/. The milestone JSON files, fixture metadata and patch-check reports capture provenance. The debugger-gated kernel-003.iso remains available for diagnosis; it is not the current unattended baseline.



For physical-console work, see [HARDWARE-PREFLIGHT.md](HARDWARE-PREFLIGHT.md) and the new [hardware inventory probe](../native-windows-hardware-probe/README.md). The probe is an independent UnleashX-launchable XBE, tested from a private FATX folder; it records RAM, kernel, PCI, interrupt and video details in an app-local text file. Revision identification, a verified recovery path and a separate test disk are still needed before preparing console-specific deployment steps. Physical Ethernet, video encoder handling, audio, controller support, power management and shutdown need separate validation or drivers.


## Physical console follow-up

Probe v2 has now completed on the physical Xbox: 64 MiB, visible 640x480x32 at 60 Hz, and all twelve selected PCI reads returned. Windows itself remains untested on the console. The [updated physical preflight](HARDWARE-PREFLIGHT.md) records the matching interrupt/device addresses, physical audio resource differences, and next loader/storage checks.

The subsequent physical FATX second-stage diagnostic extends the source chain with patch 0018, recorded in `../native-windows-physical-stage2/patch-check-0018.json`. It is opt-in and does not replace the validated Windows desktop ISO.

## Physical FATX Windows file-loading extension (0019)

The XWNF90 candidate in `../native-windows-physical-nt5` extends 0018 with a separately guarded FATX NT5 file-loading mode. The complete patch chain matches tree `33b5c16443021736bafb75b159869ca08263ff2c`. Existing native autorun artifacts remain unchanged. The candidate stops before phase 1, paging and Windows entry; ordinary builds exclude this path. Its 64 MiB xemu run loads 20 modules and 14 boot services, validates 1388 import slots and core executable code, and keeps the result visible. Missing NLS data stops at an error dialog. The user-supplied physical XWNF90 photo now confirms file-loading success with matching counts; final paging and Windows execution remain untested on hardware. The console package uses an unchanged PC SYSTEM hive solely for loading files, not for physical Windows startup. Refer to the candidate validation and FTP report for current transfer status.
