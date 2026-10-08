# Bounded FTP greeting correction

Packet evidence from151 candidate001 shows 40 UnleashX greetings transmitted
2.046431 to16.271158 seconds after their SYN (2.046155 to16.270989 after SYN/ACK);
every connection had already sent FIN. The initial sample's2.534459-second maximum
did not represent all40 flows; delayed/backlogged replies remain in the full capture.
The supervisor gave the entire greeting only two seconds. DHCP and device receive
activity were present, and the screen showed10.0.2.15. This is a demonstrated host
observation failure; it does not explain150 control's earlier0.0.0.0 screenshot.

New152 children retain the same binaries, apps, packet/trace selection, explicit
reset and original overall return deadlines. Each FTP greeting/login attempt
receives at most eight seconds, capped by the original absolute return deadline.
DeadlineFTP updates the socket budget before every reply line and command; a
multiline greeting cannot keep the attempt alive indefinitely. A socketpair test
checks complete fragmented greetings and expiry with a drip-fed reply, including
bounded worker joins. Failed151 remains failed; no old run is retried or recollected.

Initial draft pins were preserved before a pre-launch review corrected per-line
timeout renewal into a whole-exchange deadline. No guest was prepared or launched
using the draft. Final frozen-inputs.json identifies the actual tested helper and
supervisor. No emulator/network driver or dashboard configuration changes are made.
Require both fresh cases to pass all original rendering/reset/cold disk gates.
