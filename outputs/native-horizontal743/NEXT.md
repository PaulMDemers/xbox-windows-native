# 743 CLOSED; review next bounded horizontal CRTC step

Kernel742 and native743 both pass the preserving prefix followed by the seven
horizontal MMIO timing writes and own-value recovery.743 photo:743/743, first
mismatchesFFFFFFFF, cleanup0/0, selectors1, nativeCPU4001003b/0/610, count7.
All416bits cross-checked. Individual native timing words are not exposed.
Nine preparation files collected once after user-confirmed manual reset;
audit001 PASS. Console authenticated UnleashX, no hook/process/VM.

Next review the immediately following SetGPURegister horizontal CRTC writes in
outputs/xcal-transaction704/gpu_legacy.c, beginning CR04=(nvhtotal-32)/8=93.
Establish full readback and own-value restoration under the unchanged blanking/
CR11 admission conditions before writing more fields. Consider a narrow kernel
CR04 control with742's qualified prefix, then native counterpart if justified.
Check CRTC index ownership, register protection, mixed timing bounds, restore
order and behavior on restore failure. Do not jump to CR05/other CRTC, pitch,
vertical/encoder/full-mode or Windows. No744 kit or launch exists yet.

Keep original704 checks/failures, CR1b22/33 unresolved write contracts, all host
failures and exact frozen source bytes. All743/prior runtimes CLOSED: never
relaunch/recollect/parent. Routine disk-reporting kernel tests remain authorized;
intentional native holds require current watcher/photo/reset availability.
