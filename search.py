from abstractnode import Node

class AlphaBetaSearch(object):

    def __init__(self):
        self.evaluations =[]

    def search(self, root, depth=3):
        Node.max_depth = depth
        self.evaluations = []
        value = self.max_value(root, -float("inf"), float("inf"))
        #Return child specified by the value!
        #Print(value)min(data, key = lambda t: t[1])
        best = max(self.evaluations, key = lambda t: t[0])
        print(best[0])
        print(best[1])
        print("\n\n")
        return best[1]

    def max_value(self, node, alpha, beta):
        if node.terminal_state():
            print("Terminal")
            return node.get_heuristic_value()

        #print("MAX level " + str(node.level))
        value = -float("inf")
        for child in node.get_max_children():
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
        #print("MIN level " + str(node.level))
        for child in node.get_min_children():
            value = min(value, self.max_value(child, alpha, beta))
            if value <= alpha:
                return value
            beta = min(beta, value)
        return value
