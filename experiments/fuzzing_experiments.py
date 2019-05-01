from unittest import TestCase
from random import choice
from drawer import AdviceBuilder, weave_clazz, prelude
from functools import partial
from domain_model import CustomerServiceWorkflow, SpecialistWorkflow, construct_universe, Clock, Troupe
from domain_model import set_skip_log, action_log, generate_XES
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

        generate_XES(log_path='skipped_scheduling.xes')


class TestConfidenceIntervals(TestCase):
    class SkipWhenOverconfident(object):

        '''TODO
        @issue implement-skipping

        @description
        Implement skipping based on Wang 19's paper on simulation agile processes.
        '''

        def __init__(self):
            self.action_capacity_map = dict()

        def should_skip(self, attr):
            '''
            Skip an action depending on confidence interval for that action.
            :return:  Bool indicating whether to activate.
            '''
            if self.get_action_capacity(attr) > 5:
                return choice([True, False])

        def initialise_action_capacity(self, attr):
            # Note: attr is a suitable key because it is a *bound* method, so it identifies
            # both the action and the agent responsible
            if attr not in self.action_capacity_map.keys():
                self.action_capacity_map[attr] = 0.5  # TODO: initial value

        def update_action_capacity(self, attr, actor):
            if attr not in self.action_capacity_map.keys():
                self.initialise_action_capacity(attr)

            old_val = self.get_action_capacity(attr)
            self.action_capacity_map[attr] = old_val + (actor._learning_rate * (10-old_val)/old_val)

        def get_action_capacity(self, attr):
            if attr not in self.action_capacity_map.keys():
                self.initialise_action_capacity(attr)

            return self.action_capacity_map[attr]

        def prelude(self, attr, actor):
            self.update_action_capacity(attr, actor)
            if self.should_skip(attr):
                set_skip_log(True)
                # // TODO: improve output here
                with open('test.txt', 'w+') as skipped_methods:
                    skipped_methods.write(str(attr)+'\n')

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

    def test_confidence_interval(self):
        advice_to_apply = TestConfidenceIntervals.SkipWhenOverconfident()
        advice_dict = {}
        for target in dir(CustomerServiceWorkflow):
            if target[:2] != "__":
                advice_dict[eval('CustomerServiceWorkflow.' + target)] = advice_to_apply
                advice_dict[eval('SpecialistWorkflow.' + target)] = advice_to_apply

        weave_clazz(CustomerServiceWorkflow, advice_dict)
        weave_clazz(SpecialistWorkflow, advice_dict)

        [self.company.recieve_message('start') for _ in range(1000)]
        self.clock.tick(100000)


        generate_XES(log_path='confident_actor_trace.xes')

