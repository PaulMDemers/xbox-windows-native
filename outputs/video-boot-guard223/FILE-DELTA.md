# Supplemental comparison of existing directory captures

The candidate has6724 reachable files and the control6723. Read-only decoding of
their already captured80-byte directory records identifies the additional path
as winnt/system32/wbem/logs/wmiadap.log,93bytes. Neither disk was mounted or
recollected for this comparison. The capture hashes and exact path/size result
are in directory-comparison003.json; compare-directory-captures.py verifies that
existing record without replacing it.

The common paths have three size differences: WMI repository CIM.REC is705881
bytes in control and705880 in candidate, and the two workload/wizard logs differ.
No cause or content equality is inferred from sizes. This supplements the
bounded reset/CPU/integrity result; neither the structural allocation audit nor
the28 protected hashes is exhaustive file-content qualification.
