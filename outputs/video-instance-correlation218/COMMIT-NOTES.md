The pre-commit literal/uniform-newline checker rejected the older physical FTP
helper's mixed LF/CRLF working bytes. physical-stagecheck001-failure.json preserves
that host failure; no commit followed it. Corrected staged checking records exact
per-line CRLF reconstruction and requires byte-for-byte equality, retaining all
runtime hashes. No helper/source input was rewritten to satisfy the check.

The failure's original checker is retained privately under artifacts/host-staged001.py.
physical-commit-validation.json is separate from the already closed physical
capture/audit/review; those records are not regenerated for this host check.
