# Preserved host-only failures

chain001 failed at compile time: the new XboxMemInit branch called the map helper
before its declaration. source002 adds the forward declaration; chain002 passed.
No failed binary was deployed.

A PowerShell inline Python quoting error prevented an intended controller path
edit. host005 and cpu-build009 then correctly rejected the failed chain001.
Their failed output folders and receipts remain intact. Fresh host006/cpu010 use
the successful chain002, with all13 CPU fixtures closed. A separate PowerShell
brace-list parser error rejected a search/CPU command before execution; the
subsequent correctly formed command performed the single cpu010 run.

These failures are host tooling/compilation evidence, not console or transport
failures. Capacity834 is the only hardware launch so far in this direction.

The default Git whitespace check reported CRLF lines and inherited whitespace in
the byte-preserved source/evidence kit. Those files intentionally use -text so
the committed bytes remain identical to the compiled and hashed inputs. The
independent exact-index-byte comparison passed, as did the repository binary,
media and credential-pattern check. No source normalization was applied after
compilation to hide that formatting result.
