import MalmoPython
import os
import sys
import time
import random
from random import randrange as rand
from collections import deque
from tetris_game import *
import copy

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately

rewards_map = {'inc_height': -8, 'clear_line': 20, 'holes': -5}

missionXML='''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
    <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <About>
            <Summary>Tetris!</Summary>
        </About>
        <ServerSection>
                    <ServerInitialConditions>
                <Time>
                    <StartTime>1000</StartTime>
                    <AllowPassageOfTime>false</AllowPassageOfTime>
                </Time>
            </ServerInitialConditions>
            <ServerHandlers>
                <FlatWorldGenerator generatorString="3;7,44*49,73,35:1,159:4,95:13,35:13,159:11,95:10,159:14,159:6,35:6,95:6;12;"/>
                <DrawingDecorator>
                    <DrawLine x1="5" y1="56" z1="22" x2="5" y2="66" z2="22" type="obsidian"/>
                </DrawingDecorator>
                <ServerQuitFromTimeUp timeLimitMs="600000"/>
                <ServerQuitWhenAnyAgentFinishes/>
            </ServerHandlers>
        </ServerSection>
        <AgentSection mode="Creative">
            <Name>MalmoTutorialBot</Name>
            <AgentStart>
                <Placement x="5" y="67" z="22.8" yaw="180"/>
            </AgentStart>
            <AgentHandlers>
                <ObservationFromFullStats/>
                <ContinuousMovementCommands turnSpeedDegs="180"/>
            </AgentHandlers>
        </AgentSection>
    </Mission>'''
    
def magic(X):
    return ''.join(str(i) for i in X)

class TetrisAI:
    def __init__(self, alpha=0.3, gamma=1, n=1):
        self.epsilon = 0.1
        self.q_table = {}
        self.n, self.alpha, self.gamma = n, alpha, gamma

    def run(self, agent_host, tetris_game):
        states, actions, rewards = deque(), deque(), deque()
        curr_reward = 0
        done_update = False
        while not done_update:
            init_state = self.get_curr_state(tetris_game)
            possible_actions = self.get_possible_actions(tetris_game)
            init_action = self.choose_action(init_state, possible_actions)
            states.append(init_state)
            actions.append(init_action)
            print(actions)
            rewards.append(0)

            T = sys.maxint
            for t in xrange(sys.maxint):
                time.sleep(0.1)
                if t < T:
                    curr_reward = self.act(tetris_game, actions[-1])
                    rewards.append(curr_reward)

                    if tetris_game.gameover == True:
                        tetris_game.start_game()

                    curr_state = self.get_curr_state(tetris_game)
                    states.append(curr_state)
                    possible_actions = self.get_possible_actions(tetris_game)
                    next_action = self.choose_action(curr_state, possible_actions)
                    actions.append(next_action)

                tau = t - self.n + 1
                if tau >= 0:
                    self.update_q_table(tau, states, actions, rewards, T)

                if tau == T - 1:
                    while len(states) > 1:
                        tau = tau + 1
                        self.update_q_table(tau, states, actions, rewards, T)
                    done_update = True
                    break
                
    def act(self, game, action):
        game.move(action[0] - game.rlim)
        for i in range(action[1]):
            game.rotate_piece()
        game.insta_drop()
        return game.score()

    def get_curr_state(self, tetris_game):
        for i, row in enumerate(tetris_game.board[::-1]):
            if 0 not in row:
                if i  == 0:
                    new_state = tetris_game.board[-2:]
                    new_state = [[1 if x!= 0 else x for x in row]for row in new_state]
                    return new_state
                else:
                    new_state = tetris_game.board[i:i+2]
                    new_state = [[1 if x!= 0 else x for x in row]for row in new_state]
                    return new_state
                
    def get_possible_actions(self, my_game):
        actions = []
        piece = my_game.piece
        piece_x, piece_y = my_game.piece_x, my_game.piece_y
        action = (0,0)
        
        for i in range(4):
            piece_x = 0
            while piece_x <= my_game.rlim - len(piece[0]):
                if not check_collision(my_game.board,
                                       piece,
                                       (piece_x, piece_y)):
                    if action not in actions:
                        actions.append(action)
                piece_x += 1
                action = (action[0]+1, action[1])
                piece_y = my_game.piece_y
            piece = self.rotate_piece(piece, piece_x, piece_y, my_game.board)
            action = (0, action[1]+1)

        return actions

    def score(self, board):
        current_r = 0
        height = 0
        complete_lines = 0
        holes = 0
        
        for row in board:
            if (all(i == 0 for i in row) == False):
                height += 1
        current_r += height * rewards_map['inc_height']
                
        for row in board:
            if (all(i != 0 for i in row)):
                complete_lines += 1
        current_r += complete_lines * rewards_map['clear_line']
        
        pieces = copy.deepcopy(board[rows - height:])
        for i, row in enumerate(pieces):
            if i != 0:
                for index, item in enumerate(row):
                    if item == 0 and pieces[i-1][index] != 0:
                        holes += 1
        current_r += holes * rewards_map['holes']
        
        return current_r
    
    def rotate_piece(self, piece, piece_x, piece_y, board):
        new_piece = rotate_clockwise(piece)
        if not check_collision(board, new_piece, (piece_x, piece_y)):
            return new_piece
        else:
            return piece
            
    def pred_insta_drop(self, piece, piece_x, piece_y, board):
        new_board = copy.deepcopy(board)

        while not check_collision(new_board,
                           piece,
                           (piece_x, piece_y+1)):
            piece_y += 1
            
        piece_y += 1
        new_board = join_matrixes(
            new_board,
            piece,
            (piece_x, piece_y))

        return new_board
    
    def choose_action(self, state, possible_actions):
        curr_state = magic(state)
        if curr_state not in self.q_table:
            self.q_table[curr_state] = {}
        for action in possible_actions:
            if action not in self.q_table[curr_state]:
                self.q_table[curr_state][action] = 0

        rnd = random.random()
        if rnd < self.epsilon:
            a = random.randint(0, len(possible_actions) - 1)
            best_action = possible_actions[a]
        else:
            best_actions = [possible_actions[0]]
            qvals = self.q_table[curr_state]
            for action in possible_actions:
                if qvals[action] > qvals[best_actions[0]]:
                    best_actions = [action]
                elif qvals[action] == qvals[best_actions[0]]:
                    best_actions.append(action)
            a = random.randint(0, len(best_actions) - 1)
            best_action = best_actions[a]
        return best_action

    def update_q_table(self, tau, S, A, R, T):
        curr_s, curr_a, curr_r = magic(S.popleft()), A.popleft(), R.popleft()
        G = sum([self.gamma ** i * R[i] for i in range(len(S))])
        if tau + self.n < T:
            G += self.gamma ** self.n * self.q_table[magic(S[-1])][A[-1]]

        old_q = self.q_table[curr_s][curr_a]
        self.q_table[curr_s][curr_a] = old_q + self.alpha* (G - old_q)
    
if __name__ == "__main__":
    random.seed(0)

    #Initialize agent_host
    agent_host = MalmoPython.AgentHost()
    try:
        agent_host.parse( sys.argv )
    except RuntimeError as e:
        print("ERROR:",e)
        print(agent_host.getUsage())
        exit(1)
    if agent_host.receivedArgument("help"):
        print(agent_host.getUsage())
        exit(0)

    #Initialize Mission
    mission = MalmoPython.MissionSpec(missionXML, True)
    mission.allowAllChatCommands()
    mission.forceWorldReset()
    mission_record = MalmoPython.MissionRecordSpec()

    #Build Tetris Board
    left_x, right_x = -1, 10
    bottom_y, top_y = 58, 81
    z_pos = 3
    mission.drawLine( left_x, bottom_y, z_pos, left_x, top_y, z_pos, "obsidian" )
    mission.drawLine( right_x, bottom_y, z_pos, right_x, top_y, z_pos, "obsidian" )
    mission.drawLine( left_x, bottom_y, z_pos, right_x, bottom_y, z_pos, "obsidian" )
    mission.drawLine( left_x, top_y, z_pos, right_x, top_y, z_pos, "obsidian" )
    for i in range(-1,10):
        mission.drawLine(i, bottom_y, z_pos-1, i, top_y, z_pos-1, "quartz_block")
    
    #Attempt to start Mission
    max_retries = 3
    for retry in xrange(max_retries):
        try:
            agent_host.startMission( mission, mission_record )
            break
        except RuntimeError as e:
            if retry == max_retries - 1:
                print("Error starting mission:",e)
                exit(1)
            else:
                time.sleep(2)

    #Loop until mission starts
    print("Waiting for the mission to start")
    world_state = agent_host.getWorldState()
    while not world_state.has_mission_begun:
        sys.stdout.write(".")
        time.sleep(0.1)
        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print("Error:",error.text)
    print()
    print("Mission running")

    numIter = 1000
    n = 1
    my_AI = TetrisAI()
    my_game = TetrisGame(agent_host)
    print("n=", n)
    for n in range(numIter):
        my_AI.run(agent_host, my_game)
    print(my_AI.q_table)
