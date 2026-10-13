# First outline utility: rejected redirected arguments

Build001 compiled and passed NT5 import review, but the actual373 startup command
left trailing whitespace before redirected output. The exact argument comparison
printed usage and exited before changing the setting. The automatic workload
never started. Do not deploy this binary or package001.

The actual log is preserved under demo-runtime373/control001/artifacts.
Corrected source is a distinct demo-settings376 kit; the original source,
binary, package and frozen373 inputs remain unchanged.
