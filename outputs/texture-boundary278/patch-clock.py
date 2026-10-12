"""Proposed exact276 patch, privately generated and tested; not installed."""
from pathlib import Path
k=Path(__file__).resolve().parent
def one(s,a,b):
    assert s.count(a)==1,a
    return s.replace(a,b)
def apply(text):
    text=one(text,'static void do_mem_access_callback_insert(CPUState *cpu, run_on_cpu_data data)',
        (k/'clock.c').read_text()+'\nstatic void do_mem_access_callback_insert(CPUState *cpu, run_on_cpu_data data)')
    text=one(text,'    QTAILQ_INSERT_TAIL(&cpu->mem_access_callbacks, cb, entry);',
        '    QTAILQ_INSERT_TAIL(&cpu->mem_access_callbacks, cb, entry);\n    x277_clock_advance(cpu);')
    text=one(text,'    QTAILQ_REMOVE(&cpu->mem_access_callbacks, cb, entry);',
        '    QTAILQ_REMOVE(&cpu->mem_access_callbacks, cb, entry);\n    x277_clock_advance(cpu);')
    return text
