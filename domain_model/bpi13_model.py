from random import choice
from functools import partial
from theatre_au import default_cost
from actor_au import PatternMatchingActor
from utils import log_activity
import bpi13_actors


def schedule_all(task_list, actor):
    for task in task_list:
        actor.recieve_message(task)


def schedule_task_with_actor(actor, task):
    '''
    Produces a function which schedules a task with some other actor or department.
    TODO: move to actor_au?
    :param actor: Actor to perform the task
    :param task: Task to be scheduled
    :return:
    '''
    @default_cost(0)
    def scheduler():
        actor.schedule_task(task)
    return scheduler


def sync(funcs, next_step, signals=[]):
    '''
    Constructs tasks which can be executed like functions, but will act "concurrently" and stochastically in that,
    regardless of their execution order, they'll synchronise back to another function which won't continue until it's
    finished.
    TODO: move to actor_au?
    sync :: [func] -> func -> [] -> [func]
    :param funcs: List of Functions to synchronise.
    :param post_join: The function that should execute on joining the synced tasks.
    :return:
    '''

    def synchronise(joiner, func):
        func()
        signals.append(func)
        joiner()

    def join():
        for func in funcs:
            if func not in signals:
                return

        # All signals found. Remove them all from the list, spending them to execute the next step.
        [signals.remove(func) for func in funcs]
        next_step()  # NOTE: THIS SHOULD PROBABLY BE TO SCHEDULE A TASK.

    # return list(map(partial(synchronise, join), funcs))
    return [partial(synchronise, join, f) for f in funcs]


class BPI13Flow(object):
    '''
    Actions an actor from the BPI13 workflow can follow.
    TODO: make this an abstract base class?
    '''

    def __init__(self, actor):
        super(BPI13Flow, self).__init__()
        self.actor = actor  # :: Theatre_au actor with a .schedule_task method

    @default_cost(1)
    def START(self):
        possible_paths = [
            self.A_submitted
        ]

        # Make a random choice out of possible future paths
        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @default_cost(1)
    def END(self):
        '''
        Ends the flow.
        :return: None
        '''
        pass

    @log_activity
    @default_cost(1)
    def A_submitted(self):
        possible_paths = [
            self.A_partlysubmitted
        ]

        # Make a random choice out of possible future paths
        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @log_activity
    @default_cost(1)
    def A_partlysubmitted(self):
        possible_paths = [
            self.W_beoordelen_fraude_schedule,
            self.W_afhandelen_leads_schedule,
            self.A_preaccepted
        ]

        # Make a random choice out of possible future paths
        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @log_activity
    @default_cost(1)
    def W_beoordelen_fraude_schedule(self):
        possible_paths = [
            self.W_beoordelen_fraude_start
        ]
        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @log_activity
    @default_cost(1)
    def W_beoordelen_fraude_start(self):
        possible_paths = [
            self.W_beoordelen_fraude_complete,
            self.A_declined
        ]

        # Make a random choice out of possible future paths
        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @log_activity
    @default_cost(1)
    def W_beoordelen_fraude_complete(self):
        possible_paths = [
            self.END,
        ]
        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @log_activity
    @default_cost(1)
    def A_declined(self):
        next_task = self.END
        bpi13_actors.Company.recieve_message(next_task)

    @log_activity
    @default_cost(1)
    def W_afhandelen_leads_schedule(self):
        possible_paths = [
            self.W_afhandelen_leads_start
        ]
        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @log_activity
    @default_cost(1)
    def W_afhandelen_leads_start(self):
        possible_paths = [
            self.A_preaccepted,
            self.W_afhandelen_leads_complete
        ]
        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @log_activity
    @default_cost(1)
    def W_afhandelen_leads_complete(self):
        possible_paths = [
            self.W_afhandelen_leads_start,
            self.W_completeven_aanvraag_start
        ]

        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @log_activity
    @default_cost(1)
    def A_preaccepted(self):
        possible_paths = [
            self.W_completeven_aanvraag_scheduled
        ]

        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @log_activity
    @default_cost(1)
    def W_completeven_aanvraag_scheduled(self):
        possible_paths = [
            self.W_completeven_aanvraag_start
        ]

        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @log_activity
    @default_cost(1)
    def W_completeven_aanvraag_start(self):
        possible_paths = [
            self.W_completeven_aanvraag_complete,
            self.A_accepted
        ]

        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @log_activity
    @default_cost(1)
    def W_completeven_aanvraag_complete(self):
        possible_paths = [
            self.A_cancelled,
            self.W_nabellen_offertes_start,
            self.W_completeven_aanvraag_start
        ]

        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @log_activity
    @default_cost(1)
    def W_wijzigen_contractgegevens_schedule(self):
        possible_paths = [
            self.END
        ]

        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @log_activity
    @default_cost(1)
    def A_accepted(self):

        possible_paths = []

        synchronous_possible_paths = [self.A_finalised,
                                      self.O_selected]

        syncronised_tasks = sync(synchronous_possible_paths,
                                 schedule_task_with_actor(bpi13_actors.Company,
                                                          'o_created'))

        possible_paths.append(partial(schedule_all, syncronised_tasks, bpi13_actors.Company))

        next_task = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_task)

    @log_activity
    @default_cost(1)
    def A_finalised(self):
        '''
        This function schedules no more work; it just joins next.
        Joining is handled by `sync` and so this process is unaware of its next action; do nothing.
        :return: None
        '''
        pass

    @log_activity
    @default_cost(1)
    def A_cancelled(self):
        possible_paths = [
            self.W_completeven_aanvraag_complete
        ]

        next_action = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_action)

    @log_activity
    @default_cost(1)
    def O_selected(self):
        '''
        This function schedules no more work; it just joins next.
        Joining is handled by `sync` and so this process is unaware of its next action; do nothing.
        :return: None
        '''
        pass

    @log_activity
    @default_cost(1)
    def O_created(self):
        possible_paths = [
            self.O_sent
        ]

        next_action = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_action)

    @log_activity
    @default_cost(1)
    def O_sent(self):
        possible_paths = [
            self.W_nabellen_offertes_scheduled,
            self.W_nabellen_incomplete_dossiers_scheduled
        ]

        next_action = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_action)

    @log_activity
    @default_cost(1)
    def O_cancelled(self):
        possible_paths = [
            self.O_created
        ]

        next_action = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_action)

    @log_activity
    @default_cost(1)
    def O_sent_back(self):
        possible_paths = [
            self.W_valideren_aanvraag_scheduled
        ]

        next_action = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_action)

    @log_activity
    @default_cost(1)
    def W_nabellen_offertes_scheduled(self):
        possible_paths = [
            self.W_completeven_aanvraag_complete
        ]

        next_action = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_action)

    @log_activity
    @default_cost(1)
    def W_nabellen_offertes_start(self):
        possible_paths = [
            self.O_cancelled,
            self.O_sent_back,
            self.W_nabellen_offertes_complete
        ]

        next_action = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_action)

    # This one's tricky: first time we schedule something for a specialist.
    @log_activity
    @default_cost(1)
    def W_nabellen_offertes_complete(self):
        possible_paths = [
            self.W_nabellen_offertes_start,
            self.W_nabellen_offertes_complete
        ]
        possible_paths.append(schedule_task_with_actor(bpi13_actors.SpecialistDepartment, 'w_valideren_aanvraag_start'))

        next_action = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_action)

    @log_activity
    @default_cost(1)
    def W_valideren_aanvraag_scheduled(self):
        possible_paths = [
            self.W_nabellen_offertes_complete
        ]

        next_action = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_action)

    @log_activity
    @default_cost(1)
    def W_nabellen_incomplete_dossiers_scheduled(self):
        possible_paths = [
            schedule_task_with_actor(bpi13_actors.SpecialistDepartment, 'w_valideren_aanvraag_complete')
        ]

        next_action = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_action)

    @log_activity
    @default_cost(1)
    def W_nabellen_incomplete_dossiers_start(self):
        possible_paths = [
            self.W_nabellen_incomplete_dossiers_complete
        ]

        next_action = choice(possible_paths)
        bpi13_actors.Company.recieve_message(next_action)

    @log_activity
    @default_cost(1)
    def W_nabellen_incomplete_dossiers_complete(self):
        possible_paths = [
            self.W_nabellen_incomplete_dossiers_start,
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

    @log_activity
    @default_cost(1)
    def W_valideren_aanvraag_start(self):
        possible_paths = [
            self.O_declined
        ]
        synchronous_possible_paths = [self.A_approved,
                                      self.A_registered,
                                      self.A_activated,
                                      self.O_accepted
                                      ]

        syncronised_tasks = sync(synchronous_possible_paths,
                                 schedule_task_with_actor(bpi13_actors.SpecialistDepartment,
                                                          self.W_valideren_aanvraag_complete))

        possible_paths.append(partial(schedule_all, syncronised_tasks, bpi13_actors.SpecialistDepartment))

        next_action = choice(possible_paths)
        bpi13_actors.SpecialistDepartment.recieve_message(next_action)

    @log_activity
    @default_cost(1)
    def W_valideren_aanvraag_complete(self):
        possible_paths = [
            schedule_task_with_actor(bpi13_actors.Company, 'w_nabellen_incomplete_dossiers_start'),
            schedule_task_with_actor(bpi13_actors.Company, 'w_wijzigen_contractgegevens_schedule'),
            self.W_valideren_aanvraag_start
        ]

        next_action = choice(possible_paths)
        bpi13_actors.SpecialistDepartment.recieve_message(next_action)

    @log_activity
    @default_cost(1)
    def O_declined(self):
        possible_paths = [
            self.W_valideren_aanvraag_complete
        ]

        next_action = choice(possible_paths)
        bpi13_actors.SpecialistDepartment.recieve_message(next_action)

    @log_activity
    @default_cost(1)
    def O_accepted(self):
        pass  # Do nothing; next is a join managed by sync().

    @log_activity
    @default_cost(1)
    def A_approved(self):
        pass  # Do nothing; next is a join managed by sync().

    @log_activity
    @default_cost(1)
    def A_activated(self):
        pass  # Do nothing; next is a join managed by sync().

    @log_activity
    @default_cost(1)
    def A_registered(self):
        pass  # Do nothing; next is a join managed by sync().


class CustomerServiceActor(PatternMatchingActor, CustomerServiceWorkflow):

    count_customer_service_actors = 0

    def __init__(self):
        CustomerServiceActor.count_customer_service_actors += 1
        self.actor_name = "Customer Service Actor " + str(CustomerServiceActor.count_customer_service_actors)

        super(CustomerServiceActor, self).__init__()

        # blanket recognise a _lower case_ method name as a request to call that method
        self.message_patterns.update( { name.lower(): self.__getattribute__(name) for name in dir(self) } )


class SpecialistActor(PatternMatchingActor, SpecialistWorkflow):

    count_specialist_actors = 0

    def __init__(self):

        SpecialistActor.count_specialist_actors += 1
        self.actor_name = "Specialist Actor " + str(SpecialistActor.count_specialist_actors)

        super(SpecialistActor, self).__init__()

        # blanket recognise a _lower case_ method name as a request to call that method
        self.message_patterns.update( { name.lower(): self.__getattribute__(name) for name in dir(self) } )

