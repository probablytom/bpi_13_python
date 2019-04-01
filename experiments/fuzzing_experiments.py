from unittest import TestCase
from drawer import AdviceBuilder
from functools import partial
from domain_model import CustomerServiceWorkflow, construct_universe, Clock, Troupe
from pydysofu import set_fuzzer


def counting_encore(state, attribute, context, result):
    state['invocations'] += 1


class Target(object):
    def foo(self):
        return self


class TestFuzzingAppliesProperly(TestCase):
    def test_fuzzing_application(self):
        state = {'invocations': 0}
        advice = AdviceBuilder()

        encore = partial(counting_encore, state)
        advice.add_encore(Target.foo, encore)
        advice.apply()

        Target().foo().foo().foo()

        self.assertEqual(state['invocations'], 3)


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
            return steps

        set_fuzzer('a_submitted', example_fuzzer)

        self.company.recieve_message('start')
        self.clock.tick(2)
        self.assertEqual(True, False)

