import pathlib,runpy,sys
sys.argv+=['--corrupt','descriptor']
runpy.run_path(str(pathlib.Path(__file__).with_name('trace-early.py')),run_name='__main__')
