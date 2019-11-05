from domain_model import *
from run_model import *
# from domain_model import manually_log, new_trace, action_log, experimental_environment, generate_CSV, log_fuzz, generate_XES
# from hanakawa import *

def skip_current_action():
    from domain_model import set_skip_log
    set_skip_log(True)
