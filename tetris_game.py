import MalmoPython
import os
import sys
import time
from random import randrange as rand
import copy

rewards_map = {'inc_height': -8, 'clear_line': 20, 'holes': -5}

colors = ["Lime_Wool", "Orange_Wool", "Blue_Wool", "Pink_Wool", "Red_Wool",
          "Magenta_Wool", "Yellow_Wool"]

missionXML='''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
    <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <About>
            <Summary>Tetris!</Summary>
        </About>
        <ServerSection>
                    <ServerInitialConditions>
                <Time>
                    <StartTime>12000</StartTime>
                    <AllowPassageOfTime>false</AllowPassageOfTime>
                </Time>
            </ServerInitialConditions>
            <ServerHandlers>
                <FlatWorldGenerator generatorString="3;7,44*49,73,35:1,159:4,95:13,35:13,159:11,95:10,159:14,159:6,35:6,95:6;12;"/>
                <ServerQuitFromTimeUp timeLimitMs="20000"/>
                <ServerQuitWhenAnyAgentFinishes/>
            </ServerHandlers>
        </ServerSection>
        <AgentSection mode="Creative">
            <Name>MalmoTutorialBot</Name>
            <AgentStart>
                <Placement x="10" y="56" z="-27" yaw="0"/>
            </AgentStart>
            <AgentHandlers>
                <ObservationFromFullStats/>
                <ContinuousMovementCommands turnSpeedDegs="180"/>
                
            </AgentHandlers>
        </AgentSection>
    </Mission>'''

cols = 10
rows = 22

# Define the shapes of the single parts
tetris_shapes = [
	[[1, 1, 1],
	 [0, 1, 0]],
	
	[[0, 2, 2],
	 [2, 2, 0]],
	
	[[3, 3, 0],
	 [0, 3, 3]],
	
	[[4, 0, 0],
	 [4, 4, 4]],
	
	[[0, 0, 5],
	 [5, 5, 5]],
	
	[[6, 6, 6, 6]],
	
	[[7, 7],
	 [7, 7]]
]

def rotate_clockwise(shape):
    return [ [ shape[y][x]
                    for y in xrange(len(shape)) ]
            for x in xrange(len(shape[0]) - 1, -1, -1) ]

def check_collision(board, shape, offset):
    off_x, off_y = offset
    for cy, row in enumerate(shape):
        for cx, cell in enumerate(row):
            try:
                if cell and board[ cy + off_y ][ cx + off_x ]:
                    return True
            except IndexError:
                return True
    return False

def new_board():
    board = [ [ 0 for x in xrange(cols) ]
              for y in xrange(rows) ]
    board += [[ 1 for x in xrange(cols)]]
    return board

def remove_row(board, row):
    print "row removed"
    del board[row]
    return [[0 for i in xrange(cols)]] + board
	
def join_matrixes(mat1, mat2, mat2_off):
    off_x, off_y = mat2_off
    for cy, row in enumerate(mat2):
        for cx, val in enumerate(row):
            mat1[cy+off_y-1	][cx+off_x] += val
    return mat1
    
class TetrisGame:
    def __init__(self, agent_host):
        self.agent_host = agent_host
        self.width = cols+6
        self.height = rows
        self.rlim = cols
        self.next_piece = tetris_shapes[rand(len(tetris_shapes))]
        self.setup()
        self.start_game()

    def setup(self):
        self.board = new_board()
        self.new_piece()
        self.level = 1
        self.score = 0
        self.lines = 0
        self.gameover = False
            
    def new_piece(self):
        self.piece = self.next_piece[:]
        self.next_piece = tetris_shapes[rand(len(tetris_shapes))]
        self.piece_x = int(cols/2 - len(self.piece[0])/2)
        self.piece_y = 0

        self.draw_piece()
        if check_collision(self.board, self.piece, (self.piece_x, self.piece_y)):
            self.gameover = True

    def move(self, delta_x):
        if not self.gameover:
            new_x = self.piece_x + delta_x
            if new_x < 0:
                new_x = 0
            if x_new > cols - len(self.piece[0]):
                new_x = cols - len(self.piece[0])
            if not check_collision(self.board,
                                   self.piece,
                                   (new_x, self.piece_y)):
                self.piece_x = new_x

    def drop(self, manual):
        if not self.gameover:
            self.score += 1 if manual else 0
            if check_collision(self.board,
                               self.piece,
                               (self.piece_x, self.piece_y+1)):
                self.piece_y += 1
                self.board = join_matrixes(
                    self.board,
                    self.piece,
                    (self.piece_x, self.piece_y))
                self.new_piece()

                check_board = True
                clear_rows = 0
                while check_board:
                    check_board = False
                    for i, row in enumerate(self.board[:-1]):
                        if 0 not in row:
                            self.board = remove_row(self.board, i)
                            clear_rows += 1
                            check_board = True
                            break
                return True
            else:
                self.erase_piece()
                self.piece_y += 1
                self.draw_piece()
        return False

    def insta_drop(self):
        if not self.gameover:
            while(not self.drop(True)):
                pass

    def rotate_piece(self):
        new_piece = rotate_clockwise(self.piece)
        if not check_collision(self.board, new_piece, (self.piece_x, self.piece_y)):
            self.piece = new_piece
            
    def start_game(self):
        if self.gameover:
            self.setup()
            self.gameover = False

    def draw_piece(self):
        for cy, row in enumerate(self.piece):
            for cx, col in enumerate(row):
                if col != 0:
                    self.agent_host.sendCommand("chat /setblock " + str(0 + self.piece_x + cx) + " "
                                            + str(80 - self.piece_y - cy) + " 3 wool " + str(col))

    def erase_piece(self):
        for cy, row in enumerate(self.piece):
            for cx, col in enumerate(row):
                if col != 0:
                    self.agent_host.sendCommand("chat /setblock " + str(0 + self.piece_x + cx) + " "
                                            + str(80 - self.piece_y - cy) + " 3 air")
    def rand_move(self):
        if not self.gameover:
            new_x = rand(10)
            if not check_collision(self.board,
                                  self.piece,
                                  (new_x, self.piece_y)):
                self.piece_x = new_x
                return True
            else:
                return False

    def rand_rotate_piece(self):
        val = rand(4)
        new_piece = self.piece
        for i in xrange(val):
            new_piece = rotate_clockwise(new_piece)
            if not check_collision(self.board, new_piece, (self.piece_x, self.piece_y)):
                self.piece = new_piece
            else: break
            
    def run(self):
        self.gameover = False
        # Loop until mission ends:
            
        while not self.gameover:
            time.sleep(0.1)
            self.rand_move()
            self.rand_rotate_piece()
            self.insta_drop()
            
            self.world_state = self.agent_host.getWorldState()
            for error in self.world_state.errors:
                print "Error:",error.text

        # Mission has ended.
