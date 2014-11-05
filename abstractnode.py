from abc import ABCMeta, abstractmethod
from enum import Enum
#Node object, important for traversing the search graph. Abstract class
#that contain abstract methods that has to be implemented by subclasses.
#These abstract methods, is what constitute the specialization of the A*
#for this problem domain.
class Node(object):
    __metaclass__ = ABCMeta
    max_depth = 3

    def __init__(self, parent=None):
        self.children = None
        self.parent = parent
        self.level = 0
        self.root = True
        if parent:
            self.root = False
            self.level += parent.level +1

    #Generate successor nodes/states from itself.
    @abstractmethod
    def generate_successors(self, player):
        pass


    @abstractmethod
    def get_heuristic_value(self):
        pass

    @abstractmethod
    def is_state_terminal(self):
        pass

    def get_min_children(self):
        self.children = self.generate_successors(Player.MIN)
        return self.children

    def get_max_children(self):
        self.children = self.generate_successors(Player.MAX)
        return self.children

    def set_parent(self, node):
        self.parent = node

    def get_children(self):
        return self.children

    def get_parent(self):
        return self.parent

    def get_level(self):
        return self.level

    def terminal_state(self):
        return self.is_state_terminal() or self.reached_max_depth()

    def reached_max_depth(self):
        return Node.max_depth < self.level

    def __lt__(self, other):
        #return self.calc_F() < other.calc_F()
        pass


class Player(Enum):
    MAX = 1
    MIN = 2