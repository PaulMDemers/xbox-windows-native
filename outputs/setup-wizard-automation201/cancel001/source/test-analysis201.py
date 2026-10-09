"""Synthetic grammar adversaries only; cannot qualify a UI action."""
import importlib,json
from pathlib import Path
k=Path(__file__).resolve().parent;dest=k/'analysis-tests.json';assert not dest.exists()
f=importlib.import_module('analyze-cancel201').analyze
log=b'START201 1 1 120000\r\nINSTALL_STATE 258 0 0\r\nMATCHED_WINDOW 928 131216 1\r\nCANCEL_INTENT 928 131216 1\r\nCANCEL_SENT 928 131216 1\r\nCANCEL_WINDOW_CLOSED 928 131216 0\r\nIDLE201 5100 1 6200\r\n'
g=b'GUARDIAN201 1\r\nHELPER_JOIN_RESULT 0\r\nHELPER_EXIT 0\r\nSETUP_IDLE_OBSERVED_MS 5100\r\nINSTALL_WAIT_RESULT 0\r\nINSTALL_FINAL_RESULT 0\r\nNORMAL_RESTART_REQUEST 0\r\n'
assert f(log,g)['cancellation_lifecycle_passed']
bad=[(log[:-2],g),(log.replace(b'CANCEL_WINDOW_CLOSED 928 131216 0\r\n',b''),g),
     (log.replace(b'CANCEL_SENT 928',b'CANCEL_SENT 929'),g),
     (log.replace(b'131216 1',b'131216 6'),g),(log.replace(b'IDLE201 5100',b'IDLE201 4900'),g),
     (log,g.replace(b'HELPER_EXIT 0',b'HELPER_EXIT 15')),(log,g.replace(b'INSTALL_FINAL_RESULT 0',b'INSTALL_FINAL_RESULT 258')),
     (log,g.replace(b'NORMAL_RESTART_REQUEST 0\r\n',b'')),(log+b'TIMEOUT201 1 1 120000\r\n',g)]
for a,b in bad:
    try:r=f(a,b)
    except (AssertionError,ValueError):continue
    assert not r['cancellation_lifecycle_passed']
dest.write_text(json.dumps(dict(passed=True,positive=1,rejected=len(bad),scope='Synthetic parser grammar only; no guest or UI action',physical_access=False),indent=2)+'\n');print('Parser synthetic adversaries:1 accepted,9 rejected')
