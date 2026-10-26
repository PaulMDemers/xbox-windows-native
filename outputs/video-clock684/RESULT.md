# 684 read-only physical clock observation — closed

One launch was accepted on the user-identified1.6. The utility wrote its two
exclusive reports, requested a restart, and the dashboard became reachable.
Both reports were collected twice byte-identically; staged payload hashes and
unrelated E-root/application directory entries were unchanged. No hook, encoder
transaction, display-mode request or Windows launch was installed or performed.

The kernel reports QPC frequency **3,375,000Hz**. Over6.464 seconds of interrupt
time, port0x8008 advanced21,813,571 ticks: **3,374,624Hz**, about0.011% below that
reported rate at this coarse measurement resolution. RDTSC advanced at about
733.252MHz against the same elapsed interval. The raw timer samples exceed
24 bits, and none descended during this run. Largest read bracket was11 ticks.
QPC closely follows the raw port values; it is **not an independent clock** for
this evidence. No microsecond-accuracy or full32-bit-wrap physical test is claimed.

SMBus status read at entry and after sampling was **0x0000** both times. This
shows two clear kernel-context observations, not exclusive native ownership or
permission to acknowledge inherited work at a future handoff.

The legacy Cromwell delay and684's initial host candidate assumed3,579,545Hz.
That assumption is not supported by this console measurement. Its1790-tick wait
would last about530.37us at3.375MHz, so this mismatch is not evidence of an
insufficient minimum500us delay or a cause of the earlier boot/network failures.
The old candidate remains unchanged, unlinked and unqualified. The fresh
[685 candidate](../xcal-binding685/REPORT.md) uses1688 ticks and integer arithmetic.

Validation: sanitizer acquisition/model tests passed; the actual nxdk COFF
IN32/IN16 functions passed14 simulated instruction cases with no OUT operations.
Seven individual build-lock refusals plus one three-check batch were retained;
compilation subsequently succeeded under the shared lease. The initial free-space
parser selected the greeting's C statistic rather than E. `target001.json` is
superseded by `target002.json`, which specifically selects E (4,836.63MB before
staging). This caused no C filesystem access or staging on the wrong volume.

Raw evidence: [collection](collection001.json), [analysis](analysis001.json),
[closure](closure001.json). This runtime is closed; never relaunch or recollect it.
