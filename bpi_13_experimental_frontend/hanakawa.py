from scipy.integrate import quad
from numpy import inf, sqrt, pi, exp

class HanakawaKnowledgeActor(object):
    '''
    Designed to be used as a mixin with a TheatreAU actor.
    '''

    def __init__(self):
        super(HanakawaKnowledgeActor, self).__init__()
        self.task_knowledge_map = dict()

    def maximum_productivity_for_task(self, task):
        '''
        Returns c(i,j); the maximum productivity an actor i can have for a task j.
        Productivity = 1/{ticks required}, for our purposes.
        :param task: A function annotated with au's `task` decorator,
        and given a knowledge with this package's `requires_knowledge_level` decorator.
        :return: maximum productivity (1/ticks).
        '''
        return 1  # TODO decide whether non-constant

    def c(self, j):
        return self.maximum_productivity_for_task(j)

    def a(self, j):
        return self.accuracy_required_for_task(j)

    def b(self, j):
        return self.task_knowledge_map[j]

    def theta(self, task):
        return task.func_dict['knowledge level']

    def accuracy_required_for_task(self, task):
        return task.func_dict['accuracy required']

    def p(self, j):
        return self.productivity_calculation_for_task(j)

    def productivity_calculation_for_task(self, task):
        integrand = lambda t: 1/sqrt(2*pi) * exp(-t**2/2)
        upper_limit = self.a(task) * (self.b(task) - self.theta(task))
        return self.c(task) * (quad(integrand, -inf, upper_limit))


def requires_knowledge_level(knowledge_level):
    '''
    A decorator which associates a required knowledge level with a given task (\theta in Hanakawa 2002)
    :param knowledge_level:
    :return:
    '''
    def knowledge_decorator(func):
        func.func_dict['knowledge level'] = knowledge_level
        return func
    return knowledge_decorator

def requires_accuracy_level(accuracy_level):
    '''
    A decoeator which associates a required activity level with a given task (a_j in Hanakawa 2002)
    :param accuracy_level:
    :return:
    '''
    def accuracy_decorator(func):
        func.func_dict['accuracy required'] = accuracy_level
        return func
    return accuracy_decorator

def hanakawa_requires(accuracy_level=None,
                      knowledge_level=None):
    def level_applicator(func):
        func.func_dict['accuracy required'] = accuracy_level
        func.func_dict['knowledge level'] = knowledge_level
        return func
    return level_applicator