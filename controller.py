from model import GameState, Direction, GameNode, Game
from search import AlphaBetaSearch
import sys
import time

class GameController(object):
    def __init__(self, display, solver=None):
        self.model = GameState(root=True)
        self.display = display
        self.running = False
        self.plies = 4
        self.display.event({"state": self.model.create_representation()})
        if not solver: self.solver = AlphaBetaSearch()
        else: self.solver=solver

    def set_solver(self, solver, all_min_children=False):
        '''
        Setter for the solver to be used. Choices are minmax with alpha Alpha
        pruning or expectimax
        '''
        Game.all_min_children = all_min_children
        self.solver = solver

    def action(self, direction):
        '''
        Method will do a move, and send a model representation to the display.
        Ideal for manually solving 2048 game. action can be called inside 
        key listener functions.
        '''
        moved = self.model.perform_action(direction)
        self.display.event({"state": self.model.create_representation()})
        if moved:
            self.model.set_random_tile()
            self.display.event({"state": self.model.create_representation()})

    def start_solving(self):
        '''
        Method will run as long as start_solving has not been called, and
        the state is not terminal. For each iteration, the solver
        (minmax/expectimax) will find the best move for the player, place 
        a random tile in a random empty slot on the board, and send snapshots
        containing board representations to the display.
        '''
        self.running = True
        while self.running: #or not self.model.terminal_state()
            node = GameNode(self.model)
            selected_child = self.solver.search(node, self.plies)
            #sys.exit(0)
            if not selected_child:
                print(max(node.state.board))
                self.running = False
                break
            self.model = selected_child.state
            self.send_state_snapshot()
            self.model.set_random_tile()
            self.send_state_snapshot()
            time.sleep(0.04)
    
    def stop_solving(self):
        self.running = False

    def set_new_board(self, board):
        if Game.nr_of_tiles == len(board):
            self.model.board = board
            print("Setting new board")
            self.send_state_snapshot()

    def send_state_snapshot(self):
        self.display.event({"state": self.model.create_representation()})