# Preserved760 model001 failure

model.py/model001.json failed at the new c17-after-c1-read negative case.
The harness neighbor list used decimal17 instead of register0x17 (decimal23),
so that fault did not reach the intended read; actual guest returned success.
No console stage/launch occurred. Guest source and build001 are unchanged.
New model002.py uses0x17 consistently in injection/coupling/result assertions.
Generated c23 fault names denote decimal register23, i.e. CR17. Earlier failed
receipt is preserved; model002 is a fresh isolated run, not a closed VM rerun.
All earlier historical failures remain preserved including758model001.
