# 675: host-only timer observability probe

The old diagnostic can end dark for several different reasons. Eight NEW
isolated function fixtures execute the pinned674 image with modeled ports and
clock samples: frozen/backward clock during the initial dark wait, frozen clock
during the green marker, normal marker completion, frozen clock before the final
header, after its header, or after a numeric pulse, and complete reporting.
Normal marker completion also turns the LED off before the sender runs. These
are possible paths, not identification of the physical674 failure. No closed
runtime was reopened, recollected, booted or used as a fixture parent.

The prototype keeps a visible progress pattern and records an unchanged timer
operation. The authored code is built into a private host ELF, not a firmware
image/XBE. No console connection, staging, reset, UDP listener or launch occurred.

## Raw timer evidence

probe675 atomically claims an owned zeroed record, records flags and requires IF
clear. It attempts the existing658 LED register8 mask0x5f and register7 enable.
After rechecking IF, it wraps exactly one unchanged delay656 call, requesting
at most1,000 microseconds. Every timer sample is the value returned by that
call's original callback: no extra reads are inserted to measure the observer.
The first64 samples, last sample, total sample count, actual return code, request
and unchanged delay656 accounting are retained. Entry/pre-timer/post-timer flags
are separate. Original packet/capture integration has NOT been performed here.

delay656 can return N656_ARGUMENT for invalid inputs, or N656_TIMER for a
sample delta above3,579,545 or exhaustion of200,000 loop samples. The native
prototype fixes the request to1,000us, so normal admission excludes its argument
failure. Maximum reads are200,001 including the initial sample. A successful
return only satisfies this implementation against the supplied counter values;
it does not calibrate the physical counter or establish one millisecond elapsed.

The native adapter reads port0x8008 through IN(%dx),%eax, matching the retained
configuration. No clock-width or frequency change is proposed. A hypothetical
24-bit truncated counter test is labeled as a model: it demonstrates how such
input would be handled, NOT that Xbox hardware has that counter width. The
retained legacy wait_us/wait_ms comments describe a32-bit timer, and no physical
timer trace was obtained by674. No wrap mask or timer repair was applied.

## Indication without depending on the tested clock

The existing write658 transaction code is unchanged. Its delay callback is
replaced only in this HOST-ONLY probe with refuse_wait: it records the requested
delay and returns failure immediately. It neither reads the timer, spins without
the required wait, retries a failed transaction, nor treats pending SMC status as
success. Thus the LED operation can succeed only when each required status is
already ready/completed at the existing polling points. This is intentionally
conservative and has NOT been qualified on physical hardware; SMC may need time.

No LED-off request is issued. The progress pattern is green/amber, controlled
by SMC hardware rather than software pauses. After the timer call and IF check,
one register8 transaction requests solid green for timer return0, red/green for
N656_TIMER, or red/amber for an unexpected return. No timed numeric sequence.
Raw result survives final-indicator failure. A failure to set the entry pattern
prevents timer execution. A required SMC wait is a reporting limitation, not
evidence of a faulty timer or LED controller.

Every admitted return is terminal-only. The native adapter calls retained
irq_hold669 (CLI/HLT) after the prototype; it never restores IF, boots Windows or
calls the NIC. A second call leaves the owned Record675 unchanged and performs
no I/O. Return675 is the adapter's latest API-return value; Record675 remains
the authoritative first-call evidence. Like prior bounded probes, callback and
bus transaction completion is assumed; there is no guaranteed hardware hang
timeout, and IF exclusion does not cover NMI/SMI/DMA.

## Validation

- host001:2,039 ASan/UBSan assertion groups, including every1..1000us request,
  frozen/backward/discontinuous and32-bit-wrap clocks, hypothetical24-bit wrap,
  raw-prefix/last/count checks, reentry, IF faults, and independent failure of
  both entry SMC transactions and the final transaction.
- linked001:19 fresh isolated i386 fixtures against the exact linked native
  adapter. Actual IN/OUT instructions execute against explicit models. NIC/frame
  calls are forbidden; all cases hold with IF clear, preserve first-call records
  on repeat, retain raw samples and never issue a dark LED mask.
- dark-paths001:eight fresh isolated old-code fixtures establish dark-state
  ambiguity, without changing the old source/binary or claiming physical cause.
- review003:68 source/artifact/linkage/scope checks pass. The original656 timer
  and658 SMC sources match the674 firmware sources exactly. No XBE was produced.

Build, sanitizer and instruction tests passed first attempt. Preserve review001
and review002 failures: the first audit regex mistook `incl` for an IN instruction;
the second required literal0x8008 and missed a compiler-generated sign-extended
0xffff8008 loaded intoEDX. The actual IN usesDX, whose low16bits are0x8008.
Review003 corrects these audit predicates; no executable was altered to pass.

## Remaining work

A fresh HOST-ONLY full-firmware integration must place the probe after the
existing explicit post-capture freeze and record encoding, verify original
capture/packet preservation and actual layout/call paths, and demonstrate no
native sender is called by this particular timer probe. It would not expect UDP
packets. Physical admission requires a justified new attempt and a readable held
outcome; do not repeat674 or assume this fail-fast SMC policy works on hardware.

The console remains at the last confirmed dashboard674. No hook or owned host
process remains. Build lease free; physical lease/firewall retained; automation
paused. Protected720p/startup/XBOX480, releases/private256 are unchanged. No
boot/480p/NIC/acceleration fix or physical timer diagnosis claimed. Boot/1080i,
Ftdisk49 and Popup26 limitations remain.
