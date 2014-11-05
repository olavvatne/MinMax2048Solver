import random
import copy
from enum import Enum
from abstractnode import Node,Player
import math

class GameState(object):
    '''
    x -column
    y - row
    '''
    spawn_probability = [[4, 0.1],[2, 0.9]]
    dim = 4
    def __init__(self, root=False):
        self.board = []
        if root:
            self.empty_slots = []
            for i in range(GameState.dim*GameState.dim):
                self.board.append(GameTile(math.floor(i/GameState.dim),i% GameState.dim, 0))
            self.set_random_tile()
            self.set_random_tile()

    def set_random_tile(self):
        self.update_empty_slots()
        random.shuffle(self.empty_slots)
        if not self.empty_slots:
            print("GAME OVER")
        y,x = self.empty_slots.pop()
        n = self.pick_random()
        self.board[GameState.dim*y +x] = GameTile(x,y,n)

    def pick_random(self):
        r, s = random.random(), 0
        for num in GameState.spawn_probability:
            s += num[1]
            if s >= r:
                return num[0]
        raise Exception("Should not be here")

    def copy_state(self):
        child = GameState()
        for tile in self.board:
                child.board.append(GameTile(tile.x, tile.y, tile.value))
        child.update_empty_slots()
        return child

    def update_empty_slots(self):
        self.empty_slots = []
        for i in range(GameState.dim*GameState.dim):
            if self.board[i].value == 0:
                self.empty_slots.append((math.floor(i/GameState.dim),i% GameState.dim))

    def create_representation(self):
        representation = []
        for tile in self.board:
            representation.append(copy.deepcopy(tile))
        return representation

    def perform_action(self, direction):
        movement = False
        for row in range(GameState.dim):
            combined = False
            for col in self.calc_range(direction):
                i = self.calc_index(direction, row, col)
                for c in self.calc_range2(direction, col):
                    j = self.calc_index(direction, row, c)
                    if self.board[i].value >0 and self.board[j].value>0:
                        if not combined and self.board[i] == self.board[j]:
                            self.combine(i, j)
                            combined = True
                            movement = True
                        break
                    elif self.board[i].value==0 and self.board[j].value>0:
                        movement = True
                        self.move(i, j, col, row, direction)
        return movement
        

    def calc_range2(self, d, col):
        if d is Direction.RIGHT or d is Direction.DOWN:
            return range(col -1, -1, -1)
        elif d is Direction.LEFT or d is Direction.UP:
            return range(col+1, GameState.dim)
       
        raise Exception("Not a valid Enum")

    def calc_range(self, d):
        if d is Direction.RIGHT or d is Direction.DOWN:
            return range(GameState.dim-1, -1, -1)
        elif d is Direction.LEFT or d is Direction.UP:
            return range(0, GameState.dim)
       
        raise Exception("Not a valid enum")


    def calc_index(self, d, row, col):
        if d is Direction.LEFT or d is Direction.RIGHT:
            return (GameState.dim * row) + col
        else:
            return (GameState.dim*col) + row


    def combine(self, s, t):
        new_value = self.board[t].value + self.board[s].value
        col = self.board[s].x
        row = self.board[s].y
        self.board[s] = GameTile(col, row, new_value)
        self.board[t] = GameTile(self.board[t].x, self.board[s].y, 0)

    def terminal_state(self):
        if len(self.empty_slots) > 0:
            return False
        else:
            #No empty slots so merge has to be done somehow between
            #imediate neighbors
            dim = GameState.dim
            for i in range(0, dim):
                for j in range(1, dim):
                    #print("i: " + str(i) +" : j:" + str(j))
                    if self.board[(dim * i) + j] == self.board[(dim*i) + j-1] or self.board[(dim*j)  + i] == self.board[(dim*(j-1)) +i]:
                        return False
            return True

    def move(self, to_index, from_index, x, y, d):
        fx = self.board[from_index].x
        fy = self.board[from_index].y
        if d is Direction.LEFT or d is Direction.RIGHT:
            self.board[from_index].x = x
            self.board[from_index].y= y
        else:
            self.board[from_index].x = y
            self.board[from_index].y= x

        self.board[to_index] = self.board[from_index]
        self.board[from_index] = GameTile(fx,fy, 0)

    def __repr__(self):
        representation = ""
        for i in range(0, GameState.dim):
            representation +="|"
            for j in range(0, GameState.dim):
                value = 0
                if self.board[(GameState.dim*i)+j]:
                    value = self.board[(GameState.dim*i)+j].value
                representation += str(value) + "\t"
            representation +="|\n"
        return representation

class GameTile(object):
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value

    def __eq__(self, other): 
        if not other or not self:
            return False
        return self.value == other.value
    def __lt__(self, other):
        #if not other:
        #    return False
        return self.value < other.value
    def __gt__(self, other):
        #if not other:
        #    return True
        return self.value > other.value
    def __repr__(self):
        return "( x:"+str(self.x) + " y:" + str(self.y) + " v:" + str(self.value) + ")"


class Direction(Enum):
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4


class GameNode(Node):
    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state

    def __repr__(self):
        return self.state.__repr__()

    def get_heuristic_value(self):
        open_tiles = len(self.state.empty_slots)
        #sortedList = sorted(filter(None, self.state.board) )
        largest_value = max(value for value in self.state.board if value is not None)
        
        corner = self.largest_in_corner(largest_value)
        empty = float(open_tiles/16)
        monotonicity = self.monotonicity()
        #top_row = self.keep_top_row_full()
        smoothness = self.neighborhood_smoothness(largest_value)
        score = (1000*empty) + (600*corner) + (700*monotonicity) + (300*smoothness)
        #print("------------------------------------")
        #print(self.state)
        #print("EMPTY: " + str(empty))
        #print("CORNER: " + str(corner))
        #print("SMOOTHNESS: " + str(smoothness))
        #print("TOTAL-SCORE: " + str(score))
        #print("------------------------------------")
        return score

    def monotonicity(self):
        score = 0
        max_score = 78
        for i in range(0, GameState.dim):
            for j in range(1, GameState.dim):
                r = self.state.board[(GameState.dim *i) + j] 
                d = self.state.board[(GameState.dim *j) + i]
                if self.state.board[(GameState.dim *i) + j-1].value <= self.state.board[(GameState.dim *i) + j].value:
                    score += j
                if  self.state.board[(GameState.dim *j-1) + i].value <= self.state.board[(GameState.dim *j) + i].value:
                    score += j
        return float(score/max_score)

    def largest_in_corner(self, lv):
        if lv.x == 3 and lv.y == 3:
            return 1
        else:
            return 0

    def neighborhood_smoothness(self, lv):
        x = lv.x
        y = lv.y
        diff_score = 0
        max_score = 8
        neighborhood = [(x-1, y+1),(x+1,y+1),(x-1, y),(x+1,y),(x-1, y-1),(x+1,y-1),(x, y-1),(x,y+1)]
        for nx, ny in neighborhood:
            value = 0
            diff = 1
            if ( nx >=0 and nx <4 ) and ( ny >=0 and ny <4 ):
                tile = self.state.board[(GameState.dim * ny) + nx]
                value = math.log2(tile.value+1)
                diff = lv.value+1 -value
                if diff == 0:
                    #Dont want it to be too preferred to have same valued neighbors.
                    diff = 1
        #bigger difference lead to lower score
        diff_score+= float(1/diff)
        return float(diff_score/max_score)



    def in_corner(self, lv):
        if (lv.x == 0 or lv.x == 3) and (lv.y == 0 or lv.y==3):
            return 1
        else:
            return 0

    def is_state_terminal(self):
        return self.state.terminal_state()

    def generate_successors(self, p):
        succ = []
        if p is Player.MIN:
            empty_slots = self.state.empty_slots
            #Make 2C cases. Need to consider C approches
            #THere is not a large change for a 4 anyway so
            #2C branching might be excessive
            for y,x in empty_slots:
                new_state = self.state.copy_state()
                new_state.board[GameState.dim*y +x] = GameTile(x,y, self.state.pick_random())
                succ.append(GameNode(new_state, parent=self))
                #new_state = self.state.copy_state()
                #new_state.board[GameState.dim*y +x] = GameTile(x,y,2)
                #succ.append(GameNode(new_state, parent=self))
                #new_state = self.state.copy_state()
                #new_state.board[GameState.dim*y +x] = GameTile(x,y,4)
                #succ.append(GameNode(new_state, parent=self))
        elif p is Player.MAX:
            for i in range(1, GameState.dim+1):
                new_state = self.state.copy_state()
                movement = new_state.perform_action(Direction(i))
                if movement:
                    succ.append(GameNode(new_state, parent=self))
        random.shuffle(succ)
        return succ

