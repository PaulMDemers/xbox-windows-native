# Preparation failures retained

prepare.py failed on a redundant no-op string assertion after writing the C
sources. The remaining description/schema edits were completed directly; the
failed generator and prepare-failure001.json remain unchanged.

model001, model002 and model003 failed before the first transaction, in the
harness memcpy. A broad namespace replacement changed the literal machine-code
bytes `8b742410` to `8b744410`. The latter addressed uninitialized EAX instead of
the intended stack argument. model002 added an invalid-access hook; model003
also recorded the exact PC (300006), stack and pre-CLI instruction count.
All three source versions and failed receipts remain. No hardware was accessed.

Fresh model004 restores the exact previous memcpy bytes and passes 98 cases
on fresh Unicorn instances. The untouched compiled probe and XBE are unchanged.
The same accidental literal change in the unexecuted layout harness was fixed
before its first run. The source review checks both literals against742.
These are harness/source-generation failures, not physical GPU evidence.
