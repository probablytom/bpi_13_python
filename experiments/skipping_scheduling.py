from run_model import run_model
from domain_model import set_skip_log as skip_current_action

class SkipLogAdvice(object):

    def should_skip(self, attr):
        '''
        Skip all scheduling actions.
        :return:  Bool indicating whether to activate.
        '''
        return 'schedule' in attr.func_name

    def prelude(self, attr, _):
        if self.should_skip(attr):
            skip_current_action(True)

run_model(SkipLogAdvice)
