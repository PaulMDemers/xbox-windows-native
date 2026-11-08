# 853 retrace and raster diagnostic

This separate 633-based diagnostic retains the native 480p guard, register programming, six ordered clear/set predicates, 100,000-sample limit and requested per-failed-sample delay. It adds one read of GPU offset `0x600808` per existing VGA status sample and RAM bookkeeping. Extra reads and bookkeeping change timing; the observations describe this diagnostic run only. It has not been launched. A changing low-word value is a sampled-register observation, not proof of physical scanout or output timing. A constant value may reflect routing, register behavior or sampling; it does not alone prove a stopped raster.

On error22, the 852 five-group LED code reports stage4 and error22. Detail is `10 * category + failed_wait`, where failed_wait ranges 1–6: pairs 1–3, clear then set. Category describes only that failed wait:

| Category | VGA status byte during failed wait | Raster low word |
| --- | --- | --- |
| 0 | Constant `ff` | No adjacent sample changed |
| 1 | Constant `ff` | At least one adjacent sample changed |
| 2 | Constant other byte | No adjacent sample changed |
| 3 | Constant other byte | At least one adjacent sample changed |
| 4 | Varied | No adjacent sample changed |
| 5 | Varied | At least one adjacent sample changed |

For example detail 33 means category3 and wait3. Constant `ff` cannot cause a set-bit wait to fail; seeing such a decoded combination indicates a reporting/observation problem. Status-byte reads retain their normal VGA attribute-controller side effect. There are no attribute index/data writes interleaved with the edge loop. On failure the code repeats the five LED groups described in `../native480p-error852/README.md` and holds until manually powered off. LED or timer failure can prevent a complete signal; color/count observations require care. Successful native display setup continues normal boot, which can write to disk.

XBE SHA-256 `02440a1018d13955dd92d73765c4a465d51a9f0b404a184e35b54ddf46f137c5`; source delta `raster853.patch` SHA-256 `e237b5c78b478fc0e4787cffcf90ba06c1a6ab3473b65eee9ce341cbe7c29f8f`. Host checks include 235,552 existing modeled adapter assertions and 30 compiled actual-edge classification cases across all six waits and applicable status/raster categories. These models do not validate live register semantics, real LEDs, wall-clock timing or hardware behavior. The earlier 648/649 wait3 observations cannot be assigned to 852 or 853 without new evidence.
