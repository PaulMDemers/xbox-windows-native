# Narrowed to one independently owned executable

Read-only plan001 refused before compression:527/528 executable paths have four
hard links to the same file identity. Exclude all four entirely; do not weaken
the single-link requirement or operate on their shared file. No mutation occurred.

Plan002 selects only524, whose exact executable has one link and no excluded
attributes. All identity/hash/closed-process/provenance checks are unchanged.
Apply002 uses one bounded explicit compact call on that single resolved path.
Preserve both the plan001 refusal and unchanged528/527 files. This may restore
the collection64MiB/20GiB guard without reaching the512MiB extra-headroom target;
record actual capacity, never lower the guard. No retry of compression.
