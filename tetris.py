import MalmoPython
import os
import sys
import time
from random import randrange as rand
import pickle

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately

rewards_map = {'inc_height': -8, 'clear_line': 20, 'holes': -5}

colors = ["Lime_Wool", "Orange_Wool", "Blue_Wool", "Pink_Wool", "Red_Wool",
          "Magenta_Wool", "Yellow_Wool"]

missionXML='''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
    <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <About>
            <Summary>Hello world2!</Summary>
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

def new_board():
    board = [ [ 0 for x in xrange(cols) ]
              for y in xrange(rows) ]
    board += [[ 1 for x in xrange(cols)]]
    return board

class TetrisApp:
    def __init__(self):
        self.AI = TetrisAI()
        self.width = cols+6
        self.height = rows
        self.rlim = cols
        self.next_piece = tetris_shapes[rand(len(tetris_shapes))]
        self.init_game()

    def get_state():
        pass
        
    def new_piece(self):
        self.piece = self.next_piece[:]
        self.next_piece = tetris_shapes[rand(len(tetris_shapes))]
        self.piece_x = int(cols/2 - len(self.piece[0])/2)
        self.piece_y = 0

        self.draw_piece()
        if check_collision(self.board, self.piece, (self.piece_x, self.piece_y)):
            self.gameover = True

    def init_game(self):
        self.init_agent()
        self.init_mission()
        self.drawBoard()
        self.start_mission()
        
        #Tetris Board
        self.board = new_board()
        self.new_piece()
        self.level = 1
        self.score = 0
        self.lines = 0
        #set timer

    def init_agent(self):
        # Create default Malmo objects:
        self.agent_host = MalmoPython.AgentHost()
        try:
            self.agent_host.parse( sys.argv )
        except RuntimeError as e:
            print 'ERROR:',e
            print self.agent_host.getUsage()
            exit(1)
        if self.agent_host.receivedArgument("help"):
            print agent_host.getUsage()
            exit(0)

    def init_mission(self):
        self.my_mission = MalmoPython.MissionSpec(missionXML, True)
        self.my_mission.allowAllChatCommands()
        self.my_mission.forceWorldReset()
        self.my_mission_record = MalmoPython.MissionRecordSpec()

    def start_mission(self):
        # Attempt to start a mission:
        max_retries = 3
        for retry in range(max_retries):
            try:
                self.agent_host.startMission( self.my_mission, self.my_mission_record )
                break
            except RuntimeError as e:
                if retry == max_retries - 1:
                    print "Error starting mission:",e
                    exit(1)
                else:
                    time.sleep(2)
                    
        # Loop until mission starts:
        print "Waiting for the mission to start ",
        self.world_state = self.agent_host.getWorldState()
        while not self.world_state.has_mission_begun:
            sys.stdout.write(".")
            time.sleep(0.1)
            self.world_state = self.agent_host.getWorldState()
            for error in self.world_state.errors:
                print "Error:",error.text
        print
        print "Mission running ",

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

    def fake_drop(self):
        fake_board = self.board[:]
        fake_piece, fake_piece_x, fake_piece_y = self.piece, self.piece_x, self.piece_y
        
        while not check_collision(fake_board,
                           fake_piece,
                           (fake_piece_x, fake_piece_y+1)):
            fake_piece_y += 1
            
        fake_piece_y += 1
        fake_board = join_matrixes(
            fake_board,
            fake_piece,
            (fake_piece_x, fake_piece_y))

        return fake_board

    def insta_drop(self):
        if not self.gameover:
            while(not self.drop(True)):
                pass

    def rotate_piece(self):
        new_piece = rotate_clockwise(self.piece)
        if not check_collision(self.board, new_piece, (self.piece_x, self.piece_y)):
            self.piece = new_piece

    def rand_rotate_piece(self):
        val = rand(4)
        new_piece = self.piece
        for i in xrange(val):
            new_piece = rotate_clockwise(new_piece)
            if not check_collision(self.board, new_piece, (self.piece_x, self.piece_y)):
                self.piece = new_piece
            else: break
            
    def start_game(self):
        if self.gameover:
            self.init_game()
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
        
    def run(self):
        self.gameover = False
        # Loop until mission ends:
        print self.get_possible_actions()
        while self.world_state.is_mission_running and not self.gameover:
            time.sleep(0.1)
            self.rand_move()
            self.rand_rotate_piece()
            self.insta_drop()
            
            self.world_state = self.agent_host.getWorldState()
            for error in self.world_state.errors:
                print "Error:",error.text

        print self.score
        print "Mission ended"

        # Mission has ended.
    
    def drawBoard(self):
        self.my_mission.drawLine(0,58,3,0,80,3,"obsidian")
        self.my_mission.drawLine(10,58,3,10,80,3,"obsidian")
        self.my_mission.drawLine(0,58,3,10,58,3,"obsidian")
        self.my_mission.drawLine(0,80,3,10,80,3,"obsidian")

    def get_curr_state(self):
        for i, row in enumerate(self.board[:-1]):
            if 0 not in row:
                if i  == 0:
                    return self.board[-1:1]
                else:
                    return self.board[i:i+1]

    def get_possible_actions(self):
        actions = []
        original_x, original_y = self.piece_x, self.piece_y
        for i in range(4):
            self.piece_x = 0
            while self.piece_x <= cols - len(self.piece[0]):
                if not check_collision(self.board,
                                       self.piece,
                                       (self.piece_x, self.piece_y)):
                    temp = self.fake_drop()
                    print temp
                    if temp not in actions:
                        actions.append(temp)
                self.piece_x += 1
                self.piece_y = original_y
            self.rotate_piece()
        self.rotate_piece()
        self.piece_x = original_x
        
        return actions
            
        

class TetrisAI:
    def __init__(self, alpha=0.3, gamma=1, n=1):
        self.epislon = 0.1
        self.q_table = {}
        self.n, self.alpha, self.gamma = n, alpha, gamma
        

    def action(self, possible_states):
        return rand(len(possible_states))

    def choose_action(self, curr_state, possible_actions):
        if curr_state not in self.q_table:
            self.q_table[curr_state] = {}
        for action in possible_actions:
            if action not in self.q_table[curr_state]:
                self.q_table[curr_state][action] = 0

        rnd = random.random()
        if rnd < self.eps:
            a = random.randint(0, len(possible_actions) - 1)
            best_action = possible_actions[a]
        else:
            best_actions = [possible_actions[0]]
            qvals = q_table[curr_state]
            for action in possible_actions:
                if qvals[action] > qvals[best_actions[0]]:
                    best_actions = [action]
                elif qvals[action] == qvals[best_action[0]]:
                    best_actions.append(action)
            a = random.randint(0, len(best_actions) - 1)
            best_action = best_actions[a]
        return best_action

    def update_q_table(self, tau, S, A, R, T):
        curr_s, curr_a, curr_r = S.popleft(), A.popleft(), R.popleft()
        G = sum([self.gamma ** i * R[i] for i in range(len(S))])
        if tau + self.n < T:
            G += self.gamma ** self.n * self.q_table[S[-1]][A[-1]]

        old_q = self.q_table[curr_s][curr_a]
        self.q_table[curr_s][curr_a] = old_q + self.alpha* (G - old_q)

    def best_policy(self, agent_host):
        pass
    

rewards = {"line_clear": 100, "hole": -50, "bump": -30, "total_height": -75}

App = TetrisApp()
App.run()
