from utils import experimental_environment, manually_log

document_emission_active = True


def process_documents(produces=list(),
                       consumes=list()):
    if 'existing documents' not in experimental_environment.keys():
        experimental_environment['existing documents'] = dict()

    def decorator(func):

        def wrapper(*args, **kwargs):

            # Something to store the result of the function call. `None` by default.
            res = None

            # Run the function if all documents it needs to consume exist in the experimental environment
            if len(consumes) == 0 or \
                    all([consumed_doc in experimental_environment['existing documents']
                         and experimental_environment['existing documents']>0
                         for consumed_doc in consumes]):

                # Consume each document this process requires
                for consumed_doc in consumes:
                    experimental_environment['existing documents'][consumed_doc] -= 1

                # Run the process
                res = func(*args, **kwargs)

                # Produce anything this should produce
                for produced_doc in produces:
                    if produced_doc not in experimental_environment['existing documents'].keys():
                        experimental_environment['existing documents'][produced_doc] = 0
                    experimental_environment['existing documents'][produced_doc] += 1

            # If not, reschedule the work.
            # NOTE: THIS EXPECTS THAT THE TARGET OF THE DECORATOR IS A BOUND METHOD
            else:
                args[0].requeue_current_work()
                # TODO is this the right way to put this into the logs, even if it wasn't executed successfully?
                manually_log(func, args[0])

            return res

        return wrapper

    return decorator


### ========= BELOW IS SOME CODE I USED TO TEST THIS.

from actor_au import PatternMatchingActor
from theatre_au import Clock, task
import random

class A(PatternMatchingActor):

    def __init__(self):
        super(A, self).__init__()

        @task(1)
        def idle():
            pass
        self.idle = idle

        self.actor_name = random.choice(range(10))

    @task(1)
    def step_3(self):
        self.recieve_message(self.step_3)

    @task(1)
    @process_documents(consumes=['doc'])
    def step_2(self):
        self.recieve_message(self.step_3)

    @task(1)
    @process_documents(produces=['doc'])
    def step_1(self):
        self.recieve_message(self.step_2)


a = A()
clock = Clock()
clock.add_listener(a)
a.recieve_message(a.step_1)
clock.tick(5)
