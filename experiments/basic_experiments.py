import unittest
from theatre_au import Clock
from actor_au import Troupe
from domain_model import construct_universe, action_log, generate_XES, new_trace


class ExperimentalScratchpad(unittest.TestCase):

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

    def test_actors_actually_act(self):
        # Submit some work for the company to do.
        self.company.recieve_message('a_submitted')

        self.clock.tick(2)
        # Check work has moved on
        self.assertTrue(len(action_log) is not 0)

    def test_handoff_to_specialists(self):
        self.company.recieve_message('w_nabellen_incomplete_dossiers_scheduled')
        self.clock.tick(2)
        self.assertTrue('w_valideren_aanvraag_complete' in [event[1].lower() for event_sequence in action_log
                                                                             for event in event_sequence])

    # def test_plenty_of_activities(self):
    #     [self.company.recieve_message('a_submitted') for _ in range(10)]  # Lots of work
    #     self.clock.tick(400)  # Lots of time
    #     self.assertTrue('end' in map(lambda x: x[1], action_log))



class TestExperimentsMakeXES(unittest.TestCase):

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

    def test_simple_XES_trace(self):
        self.company.recieve_message('start')
        self.clock.tick(100)
        generate_XES()

    def test_generate_50_traces(self):
        def run_sim():
            self.company.recieve_message('start')
            self.clock.tick(100)

        for i in range(49):
            run_sim()
            new_trace()
        run_sim()

        generate_XES(log_path="50_traces.xes")


if __name__ == '__main__':
    unittest.main()
