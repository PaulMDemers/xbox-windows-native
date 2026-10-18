# Preserved review001 process-query failure

The source/byte/fixture checks completed, but WSL invoked the unquoted no-space
pgrep expression through bash, which rejected its parentheses and exited2.
This was a process-inventory command failure, not observed live emulator evidence.
An independent ps -eo pid=,comm= returned0 with no qemu/xemu process names.
Review002 replaces only that query with the checked ps inventory, recording all
PID/comm rows. Original review001 source/result remain immutable; no host tests,
transport/parser/observer/candidate bytes or historical captures changed.
