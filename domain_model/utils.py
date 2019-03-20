import xes


action_log = [[]]

def new_trace():
    action_log.append([])


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
        action_log[-1].append((args[0].actor_name, func.func_name))
        func(*args, **kwargs)
    return logged_func


# 3. Function for outputting an XES log
def generate_XES(traces=None, log_path='log.xes'):
    # Borrow from the XES example at https://github.com/maxsumrall/xes
    log = xes.Log()

    def makeEvent(logged_event):
        event = xes.Event()

        event.attributes = [xes.Attribute(type="string",
                                          key="concept:name",
                                          value=logged_event[1]),

                            xes.Attribute(type="string",
                                          key="org:resource",
                                          value=logged_event[0])
                            ]

        return event

    for event_set in action_log:
        trace = xes.Trace()
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
