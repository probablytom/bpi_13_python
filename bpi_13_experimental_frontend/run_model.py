from domain_model import Clock, Troupe, CustomerServiceWorkflow, SpecialistWorkflow, SimulationActor, SpecialistActor, CustomerServiceActor, old_man_time
from domain_model import construct_universe as dm_cu
from drawer import weave_clazz

clock = old_man_time
reps = Troupe()
specialists = Troupe()
company = Troupe()
num_reps = 5
num_specialists = 2


def reset_universe():
    global clock, reps, specialists, company
    clock = Clock()
    reps = Troupe()
    specialists = Troupe()
    company = Troupe()

    # Reset their names.
    CustomerServiceActor.count_customer_service_actors = 0
    SpecialistActor.count_specialist_actors = 0

    construct_universe()


def construct_universe():
    dm_cu(clock,
          specialists,
          reps,
          company,
          num_reps,
          num_specialists)


def run_model(FuzzerClass,
              num_ticks=100000,
              num_start_messages=1000,
              fuzzer_args=list(),
              fuzzer_kwargs=dict()):

    advice_to_apply = FuzzerClass(*fuzzer_args, **fuzzer_kwargs)
    advice_dict = {}
    for target in dir(CustomerServiceWorkflow):
        if target[:2] != "__":
            advice_dict[eval('CustomerServiceWorkflow.' + target)] = advice_to_apply
            advice_dict[eval('SpecialistWorkflow.' + target)] = advice_to_apply

    weave_clazz(CustomerServiceWorkflow, advice_dict)
    weave_clazz(SpecialistWorkflow, advice_dict)

    '''
    @issue: correct-message-pickup
    @description
    I'd bet that, because work gets put to the back of a queue, these start messages all get processed
    before any of the work they produce --- not ideal. Should change to either pick up work from the queue randomly,
    or space them after random (but sensible) number of ticks.

    (This might be a change to the Troupe, if they pick up work randomly, or a change to
    how I deploy the messages otherwise.)
    '''

    [company.recieve_message('start') for _ in range(num_start_messages)]
    clock.tick(num_ticks)

    # generate_XES(log_path=outputfile)

def run_model_advanced_aspect_application(class_identifier_tuple,  # Format (FuzzerClass, target_identifying_string, args, kwargs)
                                          num_ticks = 10000,
                                          num_start_messages = 100):
    '''

    :param class_identifier_tuple: Format (FuzzerClass, target_identifying_string, args, kwargs)
    :param num_ticks:
    :param num_start_messages:
    :param fuzzer_args:
    :param fuzzer_kwargs:
    :return:
    '''

    for FuzzerClass, fuzzer_target_identifier, args, kwargs in class_identifier_tuple:

        advice_to_apply = FuzzerClass(*args, **kwargs)


        def apply_to_customer_service_workers():
            advice_dict = dict()
            forbidden = ['START', 'END']
            for target in dir(CustomerServiceWorkflow):
                if target[:2] != "__" and target not in forbidden:
                    advice_dict[eval('CustomerServiceActor.' + target)] = advice_to_apply
            weave_clazz(CustomerServiceActor, advice_dict)
        def apply_to_specialist_workers():
            advice_dict = dict()
            forbidden = ['START', 'END']
            for target in dir(SpecialistWorkflow):
                if target[:2] != "__" and target not in forbidden:
                    advice_dict[eval('SpecialistActor.' + target)] = advice_to_apply
            weave_clazz(SpecialistActor, advice_dict)


        if fuzzer_target_identifier == 'get_next_task':
            advice_dict = dict()
            advice_dict[CustomerServiceActor.get_next_task] = advice_to_apply
            weave_clazz(CustomerServiceActor, advice_dict)
            advice_dict = dict()
            advice_dict[SpecialistActor.get_next_task] = advice_to_apply
            weave_clazz(SpecialistActor, advice_dict)
        elif fuzzer_target_identifier == 'customer service actors':
            apply_to_customer_service_workers()
        elif fuzzer_target_identifier == 'specialist actors':
            apply_to_specialist_workers()
        elif fuzzer_target_identifier == 'all workflows':
            apply_to_specialist_workers()
            apply_to_customer_service_workers()
        elif fuzzer_target_identifier == 'end':


            advice_dict = dict()
            advice_dict[SpecialistActor.END] = advice_to_apply
            weave_clazz(SpecialistActor, advice_dict)


            advice_dict = dict()
            advice_dict[CustomerServiceActor.END] = advice_to_apply
            weave_clazz(CustomerServiceActor, advice_dict)

        elif fuzzer_target_identifier == 'start':


            advice_dict = dict()
            advice_dict[SpecialistActor.START] = advice_to_apply
            weave_clazz(SpecialistActor, advice_dict)


            advice_dict = dict()
            advice_dict[CustomerServiceActor.START] = advice_to_apply
            weave_clazz(CustomerServiceActor, advice_dict)


    [company.recieve_message('start') for _ in range(num_start_messages)]
    # clock.tick(num_ticks)
    old_man_time.tick(num_ticks)
