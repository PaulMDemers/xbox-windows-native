# Bounded greeting observer: matched reset pair passes

Both new152 cases pass the original rendering, reset, return and cold disk gates.
verification.json reuses the independent151 network/reset verifier; no151 or150
case was repeated or requalified. The apps and xemu build003 binaries are unchanged.

DeadlineFTP gives each greeting/login exchange at most eight seconds, capped by
the original absolute return deadline. Every line/command uses remaining budget;
a drip-fed multiline reply cannot extend the exchange. The socketpair regression
accepts a fragmented complete greeting and rejects an incomplete drip-fed greeting
at0.25 seconds with bounded worker joins. Draft pre-launch pins preserve the
discarded per-line timeout draft; no fixture or guest used it.

Each case completes one explicit system_reset, dashboard return, a second native
probe and normal reboot. All twelve32768-byte snapshots match. E allocation is
complete and consistent; existing E contents/chains and entire F are unchanged.
Each startup/reset/probe phase contains matched DHCP REQUEST/ACK and link/RX
evidence. Successful greeting delays after SYN are1.784591/2.017570/5.101370 seconds
for control and1.704446/1.563605/1.885081 for candidate. Other failed connection
replies, including a20.159287-second control reply, remain recorded; eight seconds
does not guarantee every connection succeeds. Both cases return within the
unchanged overall deadline.

This is a host observation correction, not a network driver fix.150 control's
DHCP0.0.0.0 cause remains unresolved. No Windows, physical, forced callback-race,
GPU-only RAM persistence or performance claim. All owned sessions are closed;
series-closure.json is stored in sibling gpu-reset-network151. Raw packet captures
remain private; physical baselines and failed evidence are preserved.
