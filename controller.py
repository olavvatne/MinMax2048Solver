from model import GameState, Direction, GameNode
from search import AlphaBetaSearch
class GameController(object):
    def __init__(self, display):
        self.model = GameState(root=True)
        self.display = display
        self.running = False
        self.display.event({"state": self.model.create_representation()})


    def action(self, direction):
        moved = self.model.perform_action(direction)
        self.display.event({"state": self.model.create_representation()})
        if moved:
            self.model.set_random_tile()
            self.display.event({"state": self.model.create_representation()})

    def start_solving(self):
        solver = AlphaBetaSearch()
        self.running = True
        while self.running: #or not self.model.terminal_state()
            print("\n")
            print("SOLVING")
            node = GameNode(self.model)
            selected_child = solver.search(node, 4)
            if not selected_child:
                print(max(node.state.board))
                self.running = False
                break
            self.model = selected_child.state
            self.display.event({"state": self.model.create_representation()})
            self.model.set_random_tile()
            self.display.event({"state": self.model.create_representation()})
    def stop_solving(self):
        self.running = False