from unittest import TestCase
from drawer import AdviceBuilder, weave_clazz, prelude
from functools import partial
from domain_model import CustomerServiceWorkflow, SpecialistWorkflow, construct_universe, Clock, Troupe, set_skip_log, action_log
from pydysofu import set_fuzzer


def counting_encore(state, attribute, context, result):
    state['invocations'] += 1


class TestFuzzingAppliesToModel(TestCase):

    def setUp(self):
        self.clock = Clock()
        self.reps = Troupe()
        self.specialists = Troupe()
        self.company = Troupe()
        self.num_reps = 5
        self.num_specialists = 2

        construct_universe(self.clock,
                           self.specialists,
                           self.reps,
                           self.company,
                           self.num_reps,
                           self.num_specialists)

    def test_model_aspect_application(self):
        state = {'invocations': 0}
        advice = AdviceBuilder()

        encore = partial(counting_encore, state)
        advice.add_encore(CustomerServiceWorkflow.A_submitted, encore)
        advice.apply()

        self.company.recieve_message('start')
        self.clock.tick(2)

        self.assertEqual(state['invocations'], 1)

    def test_model_fuzzing(self):
        def example_fuzzer(steps, context):
            steps[0].targets = []
            return steps

        set_fuzzer('a_submitted', example_fuzzer)

        exceptions_raised = []

        def handleExpectedErr(attribute, context, exception):
            exceptions_raised.append(exception)

        catch_expected_err = AdviceBuilder()
        catch_expected_err.add_error_handler(CustomerServiceWorkflow.A_submitted, handleExpectedErr)
        catch_expected_err.apply()

        self.company.recieve_message('start')
        self.clock.tick(2)
        self.assertTrue(len(exceptions_raised) is not 0)


class TestSkeppingSteps(TestCase):

    def setUp(self):
        self.clock = Clock()
        self.reps = Troupe()
        self.specialists = Troupe()
        self.company = Troupe()
        self.num_reps = 5
        self.num_specialists = 2

        construct_universe(self.clock,
                           self.specialists,
                           self.reps,
                           self.company,
                           self.num_reps,
                           self.num_specialists)

    def test_skipping_steps_prototype(self):
        class SkipLogAdvice(object):

            def should_skip(self, attr):
                '''
                Skip all scheduling actions.
                :return:  Bool indicating whether to activate.
                '''
                return 'schedule' in attr.func_name

            def prelude(self, attr, _):
                if self.should_skip(attr):
                    set_skip_log(True)

        advice_to_apply = SkipLogAdvice()
        advice_dict = {}
        for target in dir(CustomerServiceWorkflow):
            if target[:2] != "__":
                advice_dict[eval('CustomerServiceWorkflow.' + target)] = advice_to_apply
                advice_dict[eval('SpecialistWorkflow.' + target)] = advice_to_apply

        weave_clazz(CustomerServiceWorkflow, advice_dict)
        weave_clazz(SpecialistWorkflow, advice_dict)

        self.company.recieve_message('start')
        self.clock.tick(100)

        for logged_item in map(lambda event: event[1], action_log[0]):
            self.assertTrue('schedule' not in logged_item)


