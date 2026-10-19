"""MIT. Validate all text before QMP HMP sendkey; reject textual HMP errors."""
import time
PUNCT={'\\':'0x2b',':':'shift-semicolon','.':'dot',' ':'spc','-':'minus','/':'slash','_':'shift-minus','=':'equal','"':'shift-apostrophe'}
def plan(text):
    result=[]
    for char in text:
        if 'a'<=char<='z' or '0'<=char<='9': result.append(char)
        elif 'A'<=char<='Z': result.append('shift-'+char.lower())
        elif char in PUNCT: result.append(PUNCT[char])
        else: raise ValueError('Unsupported text character U+%04X'%ord(char))
    return result

def submit(qmp,text,hold_ms=40,pause=time.sleep):
    if not 1<=hold_ms<=5000:raise ValueError('hold_ms outside bound')
    commands=plan(text) # Validate entire string before sending any input.
    for key in commands:
        response=qmp.call('human-monitor-command',{'command-line':'sendkey '+key+' '+str(hold_ms)})
        if response!='':raise RuntimeError('HMP did not return an empty success response: '+repr(response))
        pause(.15)
    return len(commands) # Submitted input only; no claim that UI/game acted.
