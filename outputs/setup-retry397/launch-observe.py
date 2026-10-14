"""Single launch followed immediately by its observer; no launch retry."""
import physical as p
case='control001'
assert not (p.K/case/'trial.json').exists()
assert not (p.K/case/'return.json').exists()
p.launch(case)
p.observe(case)
