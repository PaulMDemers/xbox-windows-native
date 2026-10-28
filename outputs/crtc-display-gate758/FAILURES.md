# Preserved758 preparation failures

model001 FAILED in the c17-before-read fault case. Its injection condition
persisted into the final prefix readback, unexpectedly injecting the same fault
twice; raw result correctly reported additional prefix mismatch4096. No console
access. model.py and model001.json retained. Fresh model002.py/model002.json
limits the before-read fault to pre-recovery; the guest probe/build is unchanged.
