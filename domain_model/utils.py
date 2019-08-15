import xes
from copy import copy

# Format: [[(actor name, method name)*]]
action_log = [[]]
experimental_environment = dict()

skip_log = False
verbose_logs = True


def set_skip_log(val):
    global skip_log
    skip_log = val


def new_trace():
    action_log.append([])

    if 'fuzzed tasks' not in experimental_environment.keys():
        experimental_environment['fuzzed tasks'] = [[]]
    else:
        experimental_environment['fuzzed tasks'].append([])


def log_fuzz(fuzz_type, fuzzed_task_name, actor="unknown actor name"):
    if 'fuzzed tasks' not in experimental_environment.keys():
        experimental_environment['fuzzed tasks'] = [[]]
    experimental_environment['fuzzed tasks'][-1].append((str(len(experimental_environment['fuzzed tasks'])),
                                                         fuzz_type,
                                                         fuzzed_task_name,
                                                         actor))


def log_activity(func):
    '''
    A decorator that logs an activity being performed by some actor.
    :param func: The decorated method, should be a method call in a process.
    :return: A decorated function.
    '''
    def logged_func(*args, **kwargs):
        # For XES stuff:
        # 1. agent name comes from arg[0] being the agent the method relates to.
        # 2. How do I pick up the trace? Maybe tag each task _object_ with its trace, so I can pick it up here?
        global skip_log
        if not skip_log:
            if verbose_logs:
                CustomerServiceWorkflow = __import__("domain_model").CustomerServiceWorkflow
                new_entry = (args[0].actor_name,
                             func.func_name,
                             "specialist" if func.func_name not in dir(CustomerServiceWorkflow) else "any",
                             args[0].__class__.__name__)
            else:
                new_entry = (args[0].actor_name,
                             func.func_name)
            action_log[-1].append(new_entry)

        skip_log = False
        return func(*args, **kwargs)
    logged_func.func_name = func.func_name
    return logged_func


def manually_log(func, actor):
    '''
    Manually add something to an activity log.
    :param func: A function representing work which needs to be logged.
    :param actor:
    :return:
    '''
    global skip_log
    if not skip_log:
        action_log[-1].append((actor.actor_name, func.func_name))
    skip_log = False


# 3. Function for outputting an XES log
def generate_XES(events=None, log_path='log.xes'):
    # Borrow from the XES example at https://github.com/maxsumrall/xes
    log = xes.Log()

    global action_log
    if events is None:
        events = copy(action_log)

    def makeEvent(logged_event):
        event = xes.Event()

        event.attributes = [xes.Attribute(type="string",
                                          key="concept:name",
                                          value=logged_event[1]),

                            xes.Attribute(type="string",
                                          key="org:resource",
                                          value=logged_event[0])
                            ]

        if len(logged_event) == 4:
            event.attributes.append(xes.Attribute(type="string",
                                                  key="concept:required_privileges_for_action",
                                                  value=logged_event[2]))
            event.attributes.append(xes.Attribute(type="string",
                                                  key="concept:actor_class",
                                                  value=logged_event[3]))

        return event

    for ev_index in range(len(events)):
        event_set = events[ev_index]
        trace = xes.Trace()
        trace.add_attribute(xes.Attribute(type="int",
                                          key="trace_id",
                                          value=str(ev_index+1)))
        [trace.add_event(makeEvent(logged_event)) for logged_event in event_set]
        log.add_trace(trace)

    log.classifiers = [
        xes.Classifier(name="org:resource",
                       keys="org:resource"),
        xes.Classifier(name="concept:name",
                       keys="concept:name")
    ]

    with open(log_path, 'w') as log_file:
        log_file.write(str(log))


def generate_CSV(csv_path='log.csv'):
    with open(csv_path, 'w') as csv_file:
        # Write header
        csv_file.write("Trace ID,Modification Type,Modified Task,Actor Involved\n")

        # For every invocation, for every task modified, log the modification
        for fuzzing_invocations in experimental_environment['fuzzed tasks']:
            for invocation in fuzzing_invocations:
                line = ','.join(invocation)
                csv_file.write(line + "\n")
