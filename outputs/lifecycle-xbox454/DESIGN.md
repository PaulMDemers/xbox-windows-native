# Matched physical lifecycle control

Use the exact [453 sample and contract](../lifecycle453/DESIGN.md) on the unchanged
720p Xbox. The physical controller changes only the result namespace and source
copy path. Require unique owned paths, completed PC controls, exact modules
including PSAPI, read-back payloads, and a single launch request. Normal restart,
hook removal before collection, cold hives/events and independent complete pixel
validation remain mandatory. Preserve partial failures; never repeat an uncertain
launch. Keep syscall outcomes, focus scope and memory observations separate from
actual loss/restore, GPU, scanout and system-wide release gates.
