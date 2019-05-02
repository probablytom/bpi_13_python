from domain_model import Clock, Troupe, construct_universe, CustomerServiceWorkflow, SpecialistWorkflow, generate_XES
from drawer import weave_clazz


def run_model(FuzzerClass,
              outputfile='model_output.xes',
              num_ticks=100000,
              num_start_messages=1000,
              fuzzer_args=list(),
              fuzzer_kwargs=dict()):
    clock = Clock()
    reps = Troupe()
    specialists = Troupe()
    company = Troupe()
    num_reps = 5
    num_specialists = 2

    construct_universe(clock,
                       specialists,
                       reps,
                       company,
                       num_reps,
                       num_specialists)

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

    generate_XES(log_path=outputfile)
