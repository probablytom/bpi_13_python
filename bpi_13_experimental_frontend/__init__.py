from run_model import *
from domain_model import manually_log

def skip_current_action():
    from domain_model import set_skip_log
    set_skip_log(True)
