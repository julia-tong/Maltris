import MalmoPython
import os
import sys
import time
import random
from random import randrange as rand
from collections import deque
from tetris_game import *
import copy
from scipy.optimize import differential_evolution
import numpy
from numpy import zeros

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately

rewards_map = {'inc_height': -20, 'clear_line': 50, 'holes': -20, 'top_height':-100}

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
                    <DrawLine x1="2" y1="56" z1="22" x2="2" y2="72" z2="22" type="obsidian"/>
                </DrawingDecorator>
                <ServerQuitWhenAnyAgentFinishes/>
            </ServerHandlers>
        </ServerSection>
        <AgentSection mode="Creative">
            <Name>MalmoTutorialBot</Name>
            <AgentStart>
                <Placement x="2.5" y="73" z="22.8" yaw="180"/>
            </AgentStart>
            <AgentHandlers>
                <ObservationFromFullStats/>
                <ContinuousMovementCommands turnSpeedDegs="180"/>
            </AgentHandlers>
        </AgentSection>
    </Mission>'''
    
class TetrisAI:
    def __init__(self, game):
        self.game = game
        self.gamesplayed = 0
        self.listGameLvl = []
        self.listClears = []

    def run(self, weights):
        scores = 0
        for i in range(20):
            j = 0
            while self.game.gameover == False and j < 150:
                time.sleep(0.2)
                j += 1
                possible_actions = self.get_possible_actions()
                next_action = self.choose_action(possible_actions, weights)
                self.act(next_action)
            scores = self.game.level
            self.gamesplayed += 1
            self.listGameLvl.append(self.game.level)
            self.listClears.append(self.game.line_clears)
            print("Made it to level:",self.game.level)
            print("Total Line Clears:",self.game.line_clears)
            self.game.start_game()

        return -scores
            
    def act(self, action):
        for i in range(action[1]):
            self.game.rotate_piece()
        self.game.move(action[0] - self.game.piece_x)
        self.game.insta_drop()

    def get_possible_actions(self):
        actions = []
        action = (0,0)
        
        for i in range(4):
            piece_x = 0
            piece_y = self.game.piece_y
            
            while piece_x <= self.game.rlim - len(self.game.piece[0]):
                if not check_collision(self.game.board,
                                       self.game.piece,
                                       (piece_x, piece_y)):
                    if action not in actions:
                        actions.append(action)
                piece_x += 1
                action = (action[0]+1, action[1])
                piece_y = self.game.piece_y
            self.game.rotate_piece()
            action = (0, action[1]+1)
        self.game.rotate_piece()
        
        return actions

    def score(self, board, weights):
        current_r = 0
        complete_lines = 0
        heighest = 0
        holes = 0

        #Complete Lines Heuristic
        new_board = board[-2::-1]
        for row in new_board:
            if 0 not in row:
                complete_lines += 1
        current_r += complete_lines * weights[0]

        #Total Height Heuristic
        heights = zeros((len(new_board[0]),), dtype = numpy.int)
        for i, row in enumerate(new_board):
            for j, col in enumerate(row):
                if col != 0:
                    heights[j] = i + 1
        aggregate_height = sum(heights)
        current_r += aggregate_height * weights[1]

        #Holes
        for i, row in enumerate(new_board[:-1]):
            if 0 in row:
                indexes = [t for t, j in enumerate(row) if j == 0]
                for index in indexes:
                    if new_board[i+1][index] != 0:
                        holes += 1
            if all(j == 0 for j in row):
                break

        current_r += holes * weights[2]

        
        return current_r
    
    def rotate_piece(self, piece, piece_x, piece_y, board):
        new_piece = rotate_clockwise(piece)
        if not check_collision(board, new_piece, (piece_x, piece_y)):
            return new_piece
        else:
            return piece

    def pred_insta_drop(self, action):
        new_board = copy.deepcopy(self.game.board)
        new_piece = self.game.piece
        new_piece_x = self.game.piece_x
        new_piece_y = self.game.piece_y
        
        for i in range(action[1]):
            new_piece = self.rotate_piece(new_piece, new_piece_x, new_piece_y, new_board)

        new_piece_x = action[0] - new_piece_x + 1
        if new_piece_x < 0:
            new_piece_x = 0
        if new_piece_x > cols - len(new_piece[0]):
            new_piece_x = cols - len(new_piece[0])

        while not check_collision(new_board,
                           new_piece,
                           (new_piece_x, new_piece_y+1)):
            new_piece_y += 1
            
        new_piece_y += 1
        new_board = join_matrixes(
            new_board,
            new_piece,
            (new_piece_x, new_piece_y))

        return new_board
    
    def choose_action(self, possible_actions, weights):
        best_action = possible_actions[0]
        best_score = self.score(self.pred_insta_drop(best_action), weights)
        
        for action in possible_actions[1:]:
            next_score = self.score(self.pred_insta_drop(action), weights)
            if next_score >= best_score:
                best_score = next_score
                best_action = action
                
        return best_action
    
if __name__ == "__main__":
    random.seed(0)

##    #Initialize agent_host
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
    left_x, right_x = -1, -1+cols+1
    bottom_y, top_y = 68, 68+rows+1
    z_pos = 3
    mission.drawLine( left_x, bottom_y, z_pos, left_x, top_y, z_pos, "obsidian" )
    mission.drawLine( right_x, bottom_y, z_pos, right_x, top_y, z_pos, "obsidian" )
    mission.drawLine( left_x, bottom_y, z_pos, right_x, bottom_y, z_pos, "obsidian" )
    mission.drawLine( left_x, top_y, z_pos, right_x, top_y, z_pos, "obsidian" )
    for i in range(-1,cols):
        mission.drawLine(i, bottom_y, z_pos-1, i, bottom_y+rows, z_pos-1, "quartz_block")
    
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
    
    my_game = TetrisGame(agent_host)
    my_AI = TetrisAI(my_game)
    weights = [ 0.62401513, -0.26825527,  0.22732638]
    print(my_AI.run(weights))
##    weights = [(-1,1),(-1,1),(-1,1)]
##    result = differential_evolution(my_AI.run, weights, maxiter=500)
##    print(result.x, result.fun)
