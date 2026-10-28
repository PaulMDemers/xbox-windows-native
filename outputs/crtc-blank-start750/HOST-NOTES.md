# Post-freeze host notes

A read-only lookup of observe_dashboard.py in closed748 failed because that
filename does not exist. No console command or collection was involved.
Use a fresh bounded observer for750; never rerun a closed observer/runtime.

A read-only rg command used unsupported PowerShell brace-list syntax and failed
parsing before execution. Corrected to directory/glob search; no runtime affected.
