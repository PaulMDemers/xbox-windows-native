# 742 CLOSED: horizontal timing writes and restoration pass

One accepted launch at2026-10-27T22:40:35.931431UTC. Seven new reports were
collected once and double-read identically after authenticated dashboard return.
Audit passed22:41:31UTC. No hook, owned VM or host process remains.

The actual kernel result is742/742. All15 prefix checks and all7 horizontal
checks pass. Prefix20-field cleanup and horizontal7-field cleanup masks are0;
selectors restored and output-enable attempted only after horizontal recovery.
Native handoff was not performed. Actual critical CR0/3/4=8001003b/f000/610;
entry/critical/restored flags246/46/246. Pre-file-write context stays separate.

| Horizontal word order | Before | Checked | Restored |
| --- | ---: | ---: | ---: |
| 680820 | 1279 | 719 | 1279 |
| 680824 | 1649 | 779 | 1649 |
| 680828 | 1279 | 719 | 1279 |
| 680834 | 0 | 0 | 0 |
| 68082c | 1389 | 738 | 1389 |
| 680830 | 1429 | 770 | 1429 |
| 680838 | 1279 | 719 | 1279 |

CR1b remains85, CR22fe and CR3311. Exact frozen source, built/staged XBE and
unrelated E-root/application entries match. Last durable record is complete
restart_requested. Automatic dashboard return is inferred; nobody observed the
picture. This is not Windows normal shutdown, a visible480p switch, complete
geometry/encoder programming, or native proof. XBE SHA256:
c6257b32cbbb021786e493f0ff29802a3473861f3551f353d605c9c18a9e83f7.

89 compiled COFF cases,2353 layout cases, independent result mutation checks,
linked PE/XBE code/data identity and repository payload checks passed. No failed
742 experiment. Source preparation99be6781. Prior failures remain unchanged.
