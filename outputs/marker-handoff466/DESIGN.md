# Two early-entry checkpoints

This emulator diagnostic is an exact462 wrapper child. It inserts the tested465
marker immediately before the original wrapper restores its saved registers and
jumps to the privileged loader. First-marker failure follows the existing
exclusive fallback mechanism with new reason12 and the raw marker result.
The earlier primary record cannot prove either marker or the paging transition.

The second hook replaces only the five-byte MOV ESP at original payload offset
0xf0. The owned diagnostic tail at02680000 executes that original stack setup
first, preserves registers/flags, runs the second marker and returns to026000f5.
The tail is beyond original BSS0265f048 and within the existing one-MiB copied
image ending02700000; the stack top remains02800000. Original privileged loader
copy size, relocated pointer offsets and 224-byte critical span are unchanged.

Stage1 requests patternff and stage2 patterna5. Each uses a distinct immutable
record. A second-marker failure quarantines in CLI/HLT; the owned emulator
watchdog bounds the process. This is not yet a qualified physical recovery
policy. No kernel or file API is invoked after the paging transition.

Host tests execute the actual wrapper and linked stub with explicitly modeled
kernel/file/SMBus/CLI/TSC interfaces. The emulator controller uses read-only GDB
memory/register access and hardware breakpoints, restores physical-memory mode,
removes all breakpoints and requests orderly host stop/quit. Debugger timing
means this is not an ordinary boot reliability trial. The original physical
launcher, Windows startup and 720p configuration stay as installed.
