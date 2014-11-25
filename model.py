import random
import copy
from enum import Enum
from abstractnode import Node,Player
import math

class Game(object):
    '''
    Game contains static variables containing values defining the game of
    2048. For example the spawn_probability, number of tiles and so on.
    '''
    spawn_probability = [[4, 0.1],[2, 0.9]]
    probability = {4: 0.1, 2: 0.9}
    dim = 4
    nr_of_tiles = 16
    all_min_children = False

class GameState(object):
    '''
    If the GameState is root, a board has to be constructed.
    Otherwise the GameState has been copied, start conditions does not apply.
    '''
    def __init__(self, root=False):
        self.board = []
        self.nr_empty_tile = Game.nr_of_tiles
        if root:
            for i in range(Game.dim*Game.dim):
                self.board.append(0)
            self.set_random_tile()
            self.set_random_tile()

    def set_random_tile(self):
        '''
        Will populate a random empty slot with a 2 or 4 tile decided by
        the 2048 spawn probability. 
        '''
        empty = self.get_empty_tiles()
        random.shuffle(empty)
        i = empty.pop()
        n = self.pick_random()
        self.set(i, n)

    def pick_random(self):
        r, s = random.random(), 0
        for num in Game.spawn_probability:
            s += num[1]
            if s >= r:
                return num[0]
        return 2 #This value will neer be returned

    def get_XY(self, i):
        return ( i%Game.dim, math.floor(i/Game.dim))

    def get_index(self, x, y):
        return (Game.dim*y)+x

    def get(self, x, y):
        return self.board[(Game.dim*y)+x]

    def set(self, i, value):
        self.board[i] = value
        self.nr_empty_tile -= 1

    def copy_state(self):
        '''
        Creates a copy of the state. Ideal for creating successors.
        '''
        child = GameState()
        child.board = self.board[:]
        child.nr_empty_tile = self.nr_empty_tile
        return child

    def get_empty_tiles(self):
        '''
        Return the index of all empty slots in the board.
        '''
        empty_indices = []
        for i in range(Game.dim*Game.dim):
            if self.board[i] == 0:
                empty_indices.append(i)
        return empty_indices

    def create_representation(self):
        return self.board

    def perform_action(self, direction):
        '''
        Method will move board into a new state. A direction is provided 
        (Left, right, up, down), and will decide how tiles should be moved
        or combined. The method makes sure that the board transition into a state
        that is valid.
        '''
        movement = False
        for row in range(Game.dim):
            combined = False
            for col in self.calc_range(direction):
                i = self.calc_index(direction, row, col)
                for c in self.calc_range2(direction, col):
                    j = self.calc_index(direction, row, c)
                    if self.board[i] >0 and self.board[j]>0:
                        if not combined and self.board[i] == self.board[j]:
                            self.combine(i, j)
                            combined = True
                            movement = True
                        break
                    elif self.board[i]==0 and self.board[j]>0:
                        movement = True
                        self.move(i, j)
        return movement
        

    def calc_range2(self, d, col):
        '''
        Creates a range for a for-loop. The range depends on the
        direction of the move.
        '''
        if d is Direction.RIGHT or d is Direction.DOWN:
            return range(col -1, -1, -1)
        elif d is Direction.LEFT or d is Direction.UP:
            return range(col+1, Game.dim)
       
        raise Exception("Not a valid Enum")

    def calc_range(self, d):
        '''
        Creates a range for a for-loop. The range depends on the
        direction of the move.
        '''
        if d is Direction.RIGHT or d is Direction.DOWN:
            return range(Game.dim-1, -1, -1)
        elif d is Direction.LEFT or d is Direction.UP:
            return range(0, Game.dim)
       
        raise Exception("Not a valid enum")


    def calc_index(self, d, row, col):
        '''
        Will calculate 1D index from row and column index. This 1D index
        differ depending on move direction.
        '''
        if d is Direction.LEFT or d is Direction.RIGHT:
            return (Game.dim * row) + col
        else:
            return (Game.dim*col) + row


    def combine(self, s, t):
        '''
        Method for combining two tiles on the board.
        s - index of slot where the tile should be combined to a new larger tile
        t - the tile that should be removed.
        Note that combine will not check the validity of the tile combine.
        IE if there are tiles inbetween or the tiles are dissimilar.
        '''
        new_value = self.board[t] + self.board[s]
        self.board[s] = new_value
        self.board[t] = 0
        self.nr_empty_tile += 1

    def terminal_state(self):
        '''
        A terminal state is reached if there are no empty slots, and
        there are not neighboring tiles that has the same values. The latter would
        constitute a merge possibilities, and that the Game has not yet reached a
        terminal state.
        '''
        if self.nr_empty_tile > 0:
            return False
        else:
            #No empty slots so merge has to be done somehow between
            #imediate neighbors
            dim = Game.dim
            for i in range(0, dim):
                for j in range(1, dim):
                    #print("i: " + str(i) +" : j:" + str(j))
                    if self.get(j,i) == self.get(j-1, i) or self.get(i,j) == self.get(i, j-1):
                        return False
            return True

    def move(self, to_index, from_index):
        '''
        A tile is moved from one index, to another index on the board.
        The method does not check the validity of the move to be performed.
        IE tiles inbetween.
        '''
        self.board[to_index] = self.board[from_index]
        self.board[from_index] = 0

    def __repr__(self):
        representation = ""
        for i in range(0, Game.dim):
            representation +="|"
            for j in range(0, Game.dim):
                value = self.board[(Game.dim*i)+j]
                representation += str(value) + "\t"
            representation +="|\n"
        return representation

class Direction(Enum):
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4


class GameNode(Node):
    def __init__(self, state, parent=None, player=Player.MAX, tile=None):
        super().__init__(parent=parent, player=player)
        self.state = state
        self.last_tile = tile
        self.all_children = True

    def __repr__(self):
        return self.state.__repr__()

    def get_heuristic_value(self):
        '''
        The method will return a score, created from the combined weighted sum
        of each heuristics component. available slots and monotonicity is weighted
        higher, because these are important for avoiding terminal states.
        '''
        corner = self.largest_in_corner()
        available = self.available_tiles()
        monotonicity = self.monotonicity()
        merges = self.merge_possibilities()
        score = (4500*(available)) + (500*corner) + (4000*monotonicity) + (1000*merges)
        #print("------------------------------------")
        #print(self.state)
        #print("AVAILABLE: " + str(available))
        #print("CORNER: " + str(corner))
        #print("SMOOTHNESS: " + str(smoothness))
        #print("MONOTONICITY: " + str(monotonicity))
        #print("TOTAL-SCORE: " + str(score))
        #print("------------------------------------")
        return score

    def available_tiles(self):
        '''
        Partial heuristics, that return a number between 0 and 1 indicating how
        many available tiles there are. If all tiles are available 1 is returned,
        and if all slots are occupied 0 is returned. 
        '''
        open_tiles = self.state.nr_empty_tile
        return float(open_tiles/16)

    def monotonicity(self):
        '''
        monotonicity measure the how structured the board is. A perfect state where
        all tiles is monotonically increasing left to right and top to bottom will
        receive a score of 1, and the opposite will receive 0. The method is 
        biased to put more importance on monotonicity in the left bottom corner. 
        '''
        score = 0
        #max_score = 24
        max_score = 48
        for i in range(0, Game.dim):
            for j in range(1, Game.dim):
                if self.state.get(j-1,i) < self.state.get(j,i):
                    #score += 1
                    score += j
                elif self.state.get(j-1,i) > self.state.get(j,i):
                    #score -= 1
                    score -= j

                if  self.state.get(i,j-1) < self.state.get(i,j):
                    score += j
                elif  self.state.get(i,j-1) > self.state.get(i,j):
                    score -= j
        return float(score/max_score)

    def largest_in_corner(self,):
        '''
        Method will return 1 if the largest value on the board is in the left
        bottom corner. Heuristics component will encourage picking states that
        keep the largest value in the corner, which is highly desirable. 
        '''
        largest_value = max(self.state.board)
        if self.state.get(3,3) >= largest_value:
            return 1
        else:
            return 0

    def merge_possibilities(self):
        '''
        Return a score for merge possibilities. If two large values can be merged
        a high merge score is returned. The method is biased to give out higher
        scores to merge possibilities between larger values. Combining two 
        1024's is highly desirable, compared to combining two 2's
        '''
        largest_value = math.log2(max(self.state.board))
        score = 0
        for i in range(0, Game.dim):
            for j in range(1, Game.dim):
                if self.state.get(j-1,i) == self.state.get(j,i) and self.state.get(j,i)>0:
                    score += float(math.log2(self.state.get(j,i)) / largest_value)
                if self.state.get(i,j-1) == self.state.get(i,j) and self.state.get(i,j)>0:
                    score += float(math.log2(self.state.get(i,j)) / largest_value)
        return score


    def is_state_terminal(self):
        return self.state.terminal_state()

    def probability(self, n):
        '''
        For imp. of expectimax
        '''
        return float((1/n)*Game.probability[self.last_tile])

    def generate_successors(self, p):
        '''
        Will generate successors for the current GameState. The children will
        be different depending if it's the max or min players turn. For example
        will MAX's children include a child node for each possible direction
        that actually alter the GameState. If it's the MIN's a child for each 
        empty slot is returned.
        '''
        succ = []
        if p is Player.MIN:
            empty_slots = self.state.get_empty_tiles()
            #Make 2C cases. Need to consider C approches
            #THere is not a large change for a 4 anyway so
            #2C branching might be excessive
            for i in empty_slots:
                if Game.all_min_children or len(empty_slots) <=4:
                    new_state = self.state.copy_state()
                    new_state.set(i, 2)
                    succ.append(GameNode(
                        new_state,
                        parent=self,
                        player=Player.MIN,
                        tile=2
                    ))
                    new_state = self.state.copy_state()
                    new_state.set(i, 2)
                    succ.append(GameNode(new_state,
                        parent=self,
                        player=Player.MIN,
                        tile=4
                    ))
                else:
                    new_state = self.state.copy_state()
                    tile_value = self.state.pick_random()
                    new_state.board[i] = tile_value
                    succ.append(GameNode(new_state,
                        parent=self,
                        player=Player.MIN,
                        tile=tile_value
                    ))
        elif p is Player.MAX:
            for i in range(1, Game.dim+1):
                new_state = self.state.copy_state()
                movement = new_state.perform_action(Direction(i))
                if movement:
                    succ.append(GameNode(
                        new_state,
                        parent=self,
                        player=Player.MAX
                        ))
        #random.shuffle(succ)
        return succ

board = [
    64, 32, 16, 8,
    32, 16, 8, 4,
    16, 8, 4, 2,
    8, 16, 2, 4,
    ]

board2 = [
    0,0,0,0,
    2,2,2,0,
    2,4,2,2,
    4,2,1028,1028,
    ]

state = GameState()
state.board = board2
node =GameNode(state)
#print(state.terminal_state())
print(node.monotonicity())
print(node.largest_in_corner())
print(node.available_tiles())
print(node.merge_possibilities())