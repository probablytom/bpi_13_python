from random import choice
from functools import partial
from theatre_au import task
from actor_au import PatternMatchingActor
from utils import log_activity
from pydysofu import fuzz
import bpi13_actors


def schedule_all(task_list, actor):
    for task in task_list:
        actor.recieve_message(task)


def schedule_task_with_actor(actor, task_to_schedule):
    '''
    Produces a function which schedules a task with some other actor or department.
    TODO: move to actor_au?
    :param actor: Actor to perform the task
    :param task: Task to be scheduled
    :return:
    '''

    @task(cost=0)
    def scheduler():
        actor.schedule_task(task_to_schedule)
    return scheduler


def sync(funcs, next_step, signals=[]):
    '''
    Constructs tasks which can be executed like functions, but will act "concurrently" and stochastically in that,
    regardless of their execution order, they'll synchronise back to another function which won't continue until it's
    finished.
    TODO: move to actor_au?
    sync :: [(func, capable_troupe)] -> func -> [] -> [func]
    :param funcs: List of Functions to synchronise.
    :param post_join: The function that should execute on joining the synced tasks.
    :return:
    '''

    def synchronise(joiner, func, troupe):

        @task(cost=0)
        def signal_complete():
            signals.append(func)
            joiner()

        troupe.recieve_message(func)
        troupe.recieve_message(signal_complete)

    def join():
        for func, _ in funcs:
            if func not in signals:
                return

        # All signals found. Remove them all from the list, spending them to execute the next step.
        # We do it this way for scoping reasons on the signals list used earlier in the function.
        for _ in signals:
            signals.pop()
        next_step()  # NOTE: THIS SHOULD PROBABLY BE TO SCHEDULE A TASK.

    schedulable_funcs = []
    for f, troupe in funcs:
        schedulable_funcs.append(partial(synchronise, join, f, troupe))
    return schedulable_funcs


class BPI13Flow(object):
    '''
    Actions an actor from the BPI13 workflow can follow.
    TODO: make this an abstract base class?
    '''

    def __init__(self, actor):
        super(BPI13Flow, self).__init__()
        self.actor = actor  # :: Theatre_au actor with a .schedule_task method

    @task(cost=1)
    def START(self):
        possible_paths = [
            self.A_submitted
        ]

        # Make a random choice out of possible future paths
        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @task(cost=1)
    def END(self):
        '''
        Ends the flow.
        :return: None
        '''
        pass

    @task(cost=1)
    @log_activity
    @fuzz(label='a_submitted')
    def A_submitted(self):
        possible_paths = [
            'a_partlysubmitted'
        ]

        # Make a random choice out of possible future paths
        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @task(cost=1)
    @log_activity
    def A_partlysubmitted(self):
        possible_paths = [
            'w_beoordelen_fraude_schedule',
            'w_afhandelen_leads_schedule',
            'a_preaccepted'
        ]

        # Make a random choice out of possible future paths
        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @task(cost=1)
    @log_activity
    def W_beoordelen_fraude_schedule(self):
        possible_paths = [
            'w_beoordelen_fraude_start'
        ]
        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @task(cost=1)
    @log_activity
    def W_beoordelen_fraude_start(self):
        possible_paths = [
            'w_beoordelen_fraude_complete',
            'a_declined'
        ]

        # Make a random choice out of possible future paths
        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @task(cost=1)
    @log_activity
    def W_beoordelen_fraude_complete(self):
        possible_paths = [
            'end',
        ]
        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @task(cost=1)
    @log_activity
    def A_declined(self):
        next_task = self.END
        bpi13_actors.Company.recieve_message(next_task)

    @task(cost=1)
    @log_activity
    def W_afhandelen_leads_schedule(self):
        possible_paths = [
            'w_afhandelen_leads_start'
        ]
        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @task(cost=1)
    @log_activity
    def W_afhandelen_leads_start(self):
        possible_paths = [
            'a_preaccepted',
            'w_afhandelen_leads_complete'
        ]
        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @task(cost=1)
    @log_activity
    def W_afhandelen_leads_complete(self):
        possible_paths = [
            'w_afhandelen_leads_start',
            'w_completeven_aanvraag_start'
        ]

        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @task(cost=1)
    @log_activity
    def A_preaccepted(self):
        possible_paths = [
            'w_completeven_aanvraag_scheduled'
        ]

        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @task(cost=1)
    @log_activity
    def W_completeven_aanvraag_scheduled(self):
        possible_paths = [
            'w_completeven_aanvraag_start'
        ]

        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @task(cost=1)
    @log_activity
    def W_completeven_aanvraag_start(self):
        possible_paths = [
            'w_completeven_aanvraag_complete',
            'a_accepted'
        ]

        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @task(cost=1)
    @log_activity
    def W_completeven_aanvraag_complete(self):
        possible_paths = [
            'a_cancelled',
            'w_nabellen_offertes_start',
            'w_completeven_aanvraag_start'
        ]

        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @task(cost=1)
    @log_activity
    def W_wijzigen_contractgegevens_schedule(self):
        possible_paths = [
            'end'
        ]

        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @task(cost=1)
    @log_activity
    def A_accepted(self):

        possible_paths = []

        synchronous_possible_paths = [self.A_finalised,
                                      self.O_selected]

        path_options_with_troupes = zip(synchronous_possible_paths,
                                        [bpi13_actors.Company for _ in synchronous_possible_paths])

        syncronised_tasks = sync(path_options_with_troupes,
                                 schedule_task_with_actor(bpi13_actors.Company,
                                                          'o_created'))

        possible_paths.append(partial(schedule_all, syncronised_tasks, bpi13_actors.Company))

        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @task(cost=1)
    @log_activity
    def A_finalised(self):
        '''
        This function schedules no more work; it just joins next.
        Joining is handled by `sync` and so this process is unaware of its next action; do nothing.
        :return: None
        '''
        pass

    @task(cost=1)
    @log_activity
    def A_cancelled(self):
        possible_paths = [
            'w_completeven_aanvraag_complete'
        ]

        next_action = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_action)

    @task(cost=1)
    @log_activity
    def O_selected(self):
        '''
        This function schedules no more work; it just joins next.
        Joining is handled by `sync` and so this process is unaware of its next action; do nothing.
        :return: None
        '''
        pass

    @task(cost=1)
    @log_activity
    def O_created(self):
        possible_paths = [
            'o_sent'
        ]

        next_action = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_action)

    @task(cost=1)
    @log_activity
    def O_sent(self):
        possible_paths = [
            'w_nabellen_offertes_scheduled',
            'w_nabellen_incomplete_dossiers_scheduled'
        ]

        next_action = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_action)

    @task(cost=1)
    @log_activity
    def O_cancelled(self):
        possible_paths = [
            'o_created'
        ]

        next_action = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_action)

    @task(cost=1)
    @log_activity
    def O_sent_back(self):
        possible_paths = [
            'w_valideren_aanvraag_scheduled'
        ]

        next_action = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_action)

    @task(cost=1)
    @log_activity
    def W_nabellen_offertes_scheduled(self):
        possible_paths = [
            'w_completeven_aanvraag_complete'
        ]

        next_action = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_action)

    @task(cost=1)
    @log_activity
    def W_nabellen_offertes_start(self):
        possible_paths = [
            'o_cancelled',
            'o_sent_back',
            'w_nabellen_offertes_complete'
        ]

        next_action = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_action)

    # This one's tricky: first time we schedule something for a specialist.
    @task(cost=1)
    @log_activity
    def W_nabellen_offertes_complete(self):
        possible_paths = [
            'w_nabellen_offertes_start',
            'w_nabellen_offertes_complete',
            schedule_task_with_actor(bpi13_actors.SpecialistDepartment, 'w_valideren_aanvraag_start')
        ]

        next_action = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_action)

    @task(cost=1)
    @log_activity
    def W_valideren_aanvraag_scheduled(self):
        possible_paths = [
            'w_nabellen_offertes_complete'
        ]

        next_action = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_action)

    @task(cost=1)
    @log_activity
    def W_nabellen_incomplete_dossiers_scheduled(self):
        possible_paths = [
            schedule_task_with_actor(bpi13_actors.SpecialistDepartment, 'w_valideren_aanvraag_complete')
        ]

        next_action = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_action)

    @task(cost=1)
    @log_activity
    def W_nabellen_incomplete_dossiers_start(self):
        possible_paths = [
            'w_nabellen_incomplete_dossiers_complete'
        ]

        next_action = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_action)

    @task(cost=1)
    @log_activity
    def W_nabellen_incomplete_dossiers_complete(self):
        possible_paths = [
            'w_nabellen_incomplete_dossiers_start',
            schedule_task_with_actor(bpi13_actors.SpecialistDepartment, 'w_valideren_aanvraag_start')
        ]

        next_action = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_action)


class CustomerServiceWorkflow(BPI13Flow):
    '''
    The standard actor class.
    '''
    pass


class SpecialistWorkflow(BPI13Flow):
    '''
    Special actor with extra actions only specialists can execute.
    TODO: should CustomerServiceActors have these too, so that some of the variance in our model can be unauthorised
    people performing these actions?
    '''

    @task(cost=1)
    @log_activity
    def W_valideren_aanvraag_start(self):
        possible_paths = [
            'o_declined'
        ]
        synchronous_possible_paths = ['a_approved',
                                      'a_registered',
                                      'a_activated',
                                      'o_accepted'
                                      ]

        path_options_with_troupes = zip(synchronous_possible_paths,
                                        [bpi13_actors.SpecialistDepartment for _ in synchronous_possible_paths])

        syncronised_tasks = sync(path_options_with_troupes,
                                 schedule_task_with_actor(bpi13_actors.SpecialistDepartment,
                                                          'w_valideren_aanvraag_complete'))

        possible_paths.append(partial(schedule_all, syncronised_tasks, bpi13_actors.SpecialistDepartment))

        next_action = choice(possible_paths)
        bpi13_actors.SpecialistDepartment.recieve_message(next_action)

    @task(cost=1)
    @log_activity
    def W_valideren_aanvraag_complete(self):
        possible_paths = [
            schedule_task_with_actor(bpi13_actors.Company, 'w_nabellen_incomplete_dossiers_start'),
            schedule_task_with_actor(bpi13_actors.Company, 'w_wijzigen_contractgegevens_schedule'),
            'w_valideren_aanvraag_start'
        ]

        next_action = choice(possible_paths)
        bpi13_actors.SpecialistDepartment.recieve_message(next_action)

    @task(cost=1)
    @log_activity
    def O_declined(self):
        possible_paths = [
            'w_valideren_aanvraag_complete'
        ]

        next_action = choice(possible_paths)
        bpi13_actors.SpecialistDepartment.recieve_message(next_action)

    @task(cost=1)
    @log_activity
    def O_accepted(self):
        pass  # Do nothing; next is a join managed by sync().

    @task(cost=1)
    @log_activity
    def A_approved(self):
        pass  # Do nothing; next is a join managed by sync().

    @task(cost=1)
    @log_activity
    def A_activated(self):
        pass  # Do nothing; next is a join managed by sync().

    @task(cost=1)
    @log_activity
    def A_registered(self):
        pass  # Do nothing; next is a join managed by sync().


class SimulationActor(PatternMatchingActor):
    def __init__(self):
        super(SimulationActor, self).__init__()

        @task(cost=1)
        def taskIdle():
            pass

        self.idle = taskIdle

class CustomerServiceActor(SimulationActor, CustomerServiceWorkflow):

    count_customer_service_actors = 0

    def __init__(self):
        CustomerServiceActor.count_customer_service_actors += 1
        self.actor_name = "Customer Service Actor " + str(CustomerServiceActor.count_customer_service_actors)

        super(CustomerServiceActor, self).__init__()

        # blanket recognise a _lower case_ method name as a request to call that method
        self.message_patterns.update( { name.lower(): self.__getattribute__(name) for name in dir(self) } )


class SpecialistActor(SimulationActor, SpecialistWorkflow):

    count_specialist_actors = 0

    def __init__(self):

        SpecialistActor.count_specialist_actors += 1
        self.actor_name = "Specialist Actor " + str(SpecialistActor.count_specialist_actors)

        super(SpecialistActor, self).__init__()

        # blanket recognise a _lower case_ method name as a request to call that method
        self.message_patterns.update( { name.lower(): self.__getattribute__(name) for name in dir(self) } )

