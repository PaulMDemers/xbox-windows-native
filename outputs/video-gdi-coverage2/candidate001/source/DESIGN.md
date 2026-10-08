# Instrumented real GDI harness

Same unchanged RAM0109,26 cases and strict requirements. Fresh output xwngdi119.
First run ended HARNESS_FAILURE0/error8 before case records. This probe records
which existing prerequisite failed, the actual clip box and stats output if
relevant. It flushes every log record and requests normal restart even on harness
failure so the failed log/metadata can be recovered. Failure remains failure;
no COMPLETE or successful case is invented. Rendering algorithms and bounds
are unchanged. Stage1 visibility,2flush,3initialcopy,4flush,5refstats,6prestats,
7poststats,8readback,9flush,10counter order,11save,12logflush,13client coordinates.
No physical access, policy changes or driver modifications.
