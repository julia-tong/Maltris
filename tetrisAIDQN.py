import MalmoPython
import os
import sys
import time
import random
import theano
from random import randrange as rand
from collections import deque
from tetris_gameDQN import *
import pickle
import copy
import numpy as np
from numpy import zeros
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam

EPISODES = 10000

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately

rewards_map = {'inc_height': -20, 'clear_line': 100, 'holes': -20, 'top_height':-100}

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

class TetrisAIDQN:
    def __init__(self, game):
        self.game = game
        self.state_size = 60
        self.action_size = 4
        self.memory = deque(maxlen=500000)
        self.gamma = 0.99
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.0001
        self.model = self._build_model()

    def _build_model(self):
        model = Sequential()
        model.add(Dense(256, input_dim=self.state_size, activation='relu'))
        model.add(Dense(256, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse',
                      optimizer=Adam(lr=self.learning_rate))
        return model

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state):
        #choose action epsilon greedy
        a_t = np.zeros([self.action_size])
        rnd = random.random()
        if rnd <= self.epsilon:
            index = random.randrange(self.action_size)
            a_t[index] = 1
        else:
            act_values = self.model.predict(state)
            index = np.argmax(act_values)
            a_t[index] = 1
        return a_t  # returns action

    def replay(self, batch_size):
        actionindex = 0
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * \
                        np.amax(self.model.predict(next_state)[0])
            target_f = self.model.predict(state)
            for index in action:
                if index == 1:
                    actionindex = index

            target_f[0][int(actionindex)] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)

    def run(self, agent_host):
        self.load("./DQN.save")
        done = False
        batch_size = 32

        for e in range(EPISODES):
            self.game.start_game()
            state = self.normalize(self.get_curr_state())
            state = np.reshape(state, [1, self.state_size])
            for time in range(500):
                action = self.act(state)
                next_state, reward, done = self.gameact(action)
                reward = reward if not done else -10
                next_state = np.reshape(next_state, [1, self.state_size])
                self.remember(state, action, reward, next_state, done)
                state = next_state
                if done:
                    print("episode: {}/{}, lvl: {}, e: {:.2}"
                          .format(e, EPISODES, time, self.epsilon))
                    break
            if len(self.memory) > batch_size:
                self.replay(batch_size)
                if e % 10 == 0:
                    self.save("./DQN.save")
                    print("saved model")
                
    def gameact(self, action):
        #one-hot encoded
        if action[1]: #[0100] LEFT
            self.game.move(self.game.piece_x-1)
        elif action[2]: #[0010] RIGHT
            self.game.move(self.game.piece_x+1)
        elif action[3]: # [0001] rotate
            self.game.rotate_piece()
        else:
            pass # [1000] do nothing
        self.game.insta_drop_no_draw() #dont draw for training
        if self.game.gameover:
            reward = 0
        else:
            reward = self.game.line_clears*100
        next_state = self.get_curr_state()
        return next_state, reward, self.game.gameover

    def get_curr_state(self): #get entire board
        # board = self.game.board[-2::-1]
        # return board
        board = copy.deepcopy(self.game.board[:-1])
        new_board = join_matrixes(
                    board,
                    self.game.piece,
                    (self.game.piece_x, self.game.piece_y))
        return new_board
                          
    def normalize(self, state):
        new_state = [[1 if x!= 0 else x for x in row]for row in state]
        return new_state

    
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

    numIter = 1
    n = 1
    my_game = TetrisGame(agent_host)
    my_AI = TetrisAIDQN(my_game)
    print("n=", n)
    for n in range(numIter):
        my_AI.run(agent_host)
