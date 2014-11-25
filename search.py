from abstractnode import Node
from abstractnode import Player
class AlphaBetaSearch(object):
    '''
    Based on the pseudo code found in the AI textbook, Artifical intelligence, 
    a modern approch
    '''
    def __init__(self):
        self.evaluations =[]

    def search(self, root, depth=3):
        '''
        Method will run a minmax search using the provided root object.
        The root object should be a object that support the methods found in
        Node. The depth parameter will determine how far the minmax will explore,
        before generating a heuristics value for the state. The child
        of root that has the best evaluation is returned by search.
        '''
        Node.max_depth = depth
        self.evaluations = []
        value = self.max_value(root, -float("inf"), float("inf"))
        #Return child specified by the value!
        #Print(value)min(data, key = lambda t: t[1])
        if len(self.evaluations) > 0:
            best = max(self.evaluations, key = lambda t: t[0])
            print("\n----------PREVIOUS------------")
            print(root)
            print("----------BEST NEXT------------")
            print(best[1])
            print(best[1].get_heuristic_value())
            print("\n----------ALTERNATIVES------------")
            for tile in self.evaluations:
                print(tile[1])
                print("HEURISTIC: " + str(tile[1].get_heuristic_value()))
                print("EVAL: " + str(tile[0]))
                print("-----------------")
            print("------------------------------")
            print("\n\n")
            return best[1]
        return None

    def max_value(self, node, alpha, beta):
        if node.terminal_state():
            return node.get_heuristic_value()

        value = -float("inf")
        for child in node.get_max_children():
            #print("MAX level " + str(child.level))
            value = max(value, self.min_value(child, alpha, beta))
            if node.root:
                self.evaluations.append((value, child))      
            if value >= beta:
                return value
            alpha = max(alpha, value)
        return value

    def min_value(self, node, alpha, beta):
        if node.terminal_state():
            return node.get_heuristic_value()
        value = float("inf")
        for child in node.get_min_children():
            #print("MIN level " + str(child.level))
            value = min(value, self.max_value(child, alpha, beta))
            if value <= alpha:
                return value
            beta = min(beta, value)
        return value


class Expectimax(object):

    def __init__(self):
        self.evaluations = []

    def search(self, root, depth=3):
        Node.max_depth = depth
        best_value = self.max_value(root)
        if len(self.evaluations) > 0:
            best = max(self.evaluations, key = lambda t: t[0])
            print("\n----------PREVIOUS------------")
            print(root)
            print("----------BEST NEXT------------")
            print(best[1])
            print(best[1].get_heuristic_value())
            print("\n----------ALTERNATIVES------------")
            for tile in self.evaluations:
                print(tile[1])
                print("HEURISTIC: " + str(tile[1].get_heuristic_value()))
                print("EVAL: " + str(tile[0]))
                print("-----------------")
            print("------------------------------")
            print("\n\n")
            return best[1]
        return None

    def value(self, s, p):
        if s.terminal_state():
            return s.get_heuristic_value()
        if p == Player.MIN:
            return self.max_value(s)
        if p == Player.MAX:
            return self.exp_value(s)

    def max_value(self, s):
        children = s.get_max_children()
        values = [self.value(c, Player.MAX) for c in children]
        if s.root:
            self.evaluations = list(zip(values, children))
        return max(values)

    def exp_value(self,s):
        children = s.get_min_children()
        values = [self.value(c, Player.MIN) for c in children]
        weights = [c.probability(len(children)) for c in children]
        return self.expectation(values, weights)
    
    def expectation(self,values, weights):
        expectation = 0.0
        for i in range(len(values)):
            expectation += values[i]*weights[i]
        return expectation