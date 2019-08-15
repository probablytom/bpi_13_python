from actor_au import Troupe
from theatre_au import Clock
import bpi13_model

CustomerServiceReps = Troupe()
SpecialistDepartment = Troupe()
Company = Troupe()
old_man_time = Clock()

def set_up_new_actor(actor_type, associated_group):
    new_rep = actor_type()

    # Add the actor of the right type to the right group, and to the whole company too
    associated_group.add_member(new_rep)
    Company.add_member(new_rep)

    # The actor must act when the clock ticks, so add as a listener.
    old_man_time.add_listener(new_rep)


def construct_bpi_simulation(num_ordinary_customer_service_reps=3,
                   num_specialists=3):

    '''
    Construct the Company with specialists and regular reps
    :param num_ordinary_customer_service_reps: Number of customer service reps to construct
    :param num_specialists:
    :return:
    '''

    #                    Actor Type            Message Group         Count
    types_and_groups = [(bpi13_model.CustomerServiceActor, CustomerServiceReps,  num_ordinary_customer_service_reps),
                        (bpi13_model.SpecialistActor,      SpecialistDepartment, num_specialists)]

    for actor_type, message_group, count in types_and_groups:
        for _ in range(count):
            set_up_new_actor(actor_type, message_group)


def construct_universe(clock=Clock(),
                       specialist_troupe=Troupe(),
                       rep_troupe=Troupe(),
                       company=Troupe(),
                       reps=3,
                       specialists=3):
    global old_man_time, SpecialistDepartment, CustomerServiceReps, Company
    old_man_time = clock
    SpecialistDepartment = specialist_troupe
    CustomerServiceReps = rep_troupe
    Company = company

    # Make people to work in our bank
    construct_bpi_simulation(reps, specialists)
