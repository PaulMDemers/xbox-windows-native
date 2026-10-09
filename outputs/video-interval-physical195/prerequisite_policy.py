"""Functional helper prerequisite only; never whole-boot/release qualification."""

def qualified_branches(idle, failed194, observed196, ordinary197):
    return (
        idle.get('case') == 'idle001'
        and idle.get('idle_branch_passed') is True
        and idle.get('diagnostic_usable') is True
        and idle.get('integrity_passed') is True
        and idle.get('debugger') is False
        and failed194.get('case') == 'pending001'
        and failed194.get('diagnostic_usable') is False
        and failed194.get('integrity_passed') is False
        and observed196.get('case') == 'pending002'
        and observed196.get('debugger') is True
        and observed196.get('pending_branch_passed') is True
        and observed196.get('diagnostic_usable') is True
        and observed196.get('integrity_passed') is True
        and observed196.get('snapshot_transactions_passed') is True
        and ordinary197.get('case') == 'pending001'
        and ordinary197.get('debugger') is False
        and ordinary197.get('pending_branch_passed') is True
        and ordinary197.get('diagnostic_usable') is True
        and ordinary197.get('integrity_passed') is True
        and ordinary197.get('normal_shutdown_count') == 0
        and ordinary197.get('dashboard_return') is False
        and ordinary197.get('ordinary_qualified') is False
        and ordinary197.get('physical_qualified') is False
    )
