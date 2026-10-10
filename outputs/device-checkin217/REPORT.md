# Device workstream check-in

The user authorized this check-in. Follow-up messages went to the three existing
device chats; each replied without launching a guest or touching the physical
console. Local owner checkouts are clean and match the reported pushed commits.
Delivered audio and USB package hashes were readback verified. See checkin.json
for exact identities and source/report paths. No branch was merged and combined
compatibility with video bacbde5 has not been tested.

| Chat | Current result | Remaining qualification |
| --- | --- | --- |
| Xbox Windows 2000 audio | Experimental ACI driver; genuine installation and two playback boots in xemu, independently checked stereo and normal restarts | Physical Wolfson/audible behavior, digital output, APU01B0; inherited Ftdisk49 remains |
| Xbox Windows 2000 PCI devices | Exact01B4 SMBus installation and fresh telemetry on a second boot | Pending installation prevented normal shutdown; power/lifecycle/security gates, physical testing and modem01C1 evidence |
| Xbox Windows 2000 USB and gamepad | Descriptor collector captured XID controller, HID keyboard and mouse | Functional XID transport/minidriver, persistent binding, normal reboot and physical descriptors; no gamepad driver delivered |

Audio commit7cdb191 uses only its assigned ACI MMIO aperture and PortCls interrupt,
with no HAL/kernel or GPU changes. Its DMA allocations must remain consistent
with the future GPU reservation. Audio's known unrelated wizard cancellation
does not qualify a prompt-free combined boot. The experimental package is ready
for coordinator review, not already physically qualified.

PCI commit801bdbd retains the HAL's C000 SMBus address through resource filtering.
Its private mutex does not serialize telemetry with HAL reboot or video encoder
clients. Concurrent encoder transactions require an explicit shared ownership
protocol. The normal-shutdown failure is preserved; the global pending query
does not prove audio is the only pending device. Modem01C1 shares AC'97 link/reset
resources with audio and lacks a corresponding actual xemu function, so a stale
registry binding cannot qualify it.

USB commit5d86c99 queries the existing OHCI/hub stack and introduces no direct
MMIO, interrupt or GPU ownership. Its screenshots were scrambled and establish
no visual/input success. Standard hub requests do not collect vendor XID reports;
the next driver needs the actual descriptor/report transport contract. Its
physical collection protocol remains separate from video experiments.

Keep the original installed baseline and immutable0.1.0. Coordinator integration
must be serialized, preserve fresh rollback bundles and qualify actual combined
installation, reboot, cold integrity and runtime behavior. None of the individual
reports waives Ftdisk49 or replaces a combined qualification run.
