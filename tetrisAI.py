import MalmoPython
import os
import sys
import time
from random import randrange as rand
import tetris_game
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

def pred_insta_drop(self):
    fake_board = copy.deepcopy(self.board)
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

def rand_rotate_piece(self):
    val = rand(4)
    new_piece = self.piece
    for i in xrange(val):
        new_piece = rotate_clockwise(new_piece)
        if not check_collision(self.board, new_piece, (self.piece_x, self.piece_y)):
            self.piece = new_piece
        else: break

def run(self):
    states, actions, rewards = deque(), deque(), deque()
    present_reward = 0
    self.gameover = False
    # Loop until mission ends:

    num_iter = 1000
    for i in xrange(num_iter):
        #Prepare current actions and states
        curr_state = self.get_curr_state(self, self.board)
        possible_actions = self.AI.choose_action(curr_state)
        curr_action = self.AI.choose_action(curr_state, possible_actions, 0.3)
        states.append(curr_state)
        actions.append(curr_action)
        reward.append(0)

        while not self.gameover:
            curr_reward = self.act(A[-1])
            rewards.append(curr_reward)

            curr_state = self.get_curr_state()
            states.append(curr_state)
            possible_actions = self.get_possible_actions()
            next_action = self.choose_action(curr_state, possible_actions, 0.3)
            actions.append(next_action)

            time.sleep(0.1)
            self.rand_move()
            self.rand_rotate_piece()
            self.insta_drop()

            self.world_state = self.agent_host.getWorldState()
            for error in self.world_state.errors:
                print "Error:",error.text

        self.update_q_table(tau, states, actions, rewards, T)

    print self.score
    print "Mission ended"

    # Mission has ended.

class TetrisAI:
    def __init__(self, alpha=0.3, gamma=1, n=1):
        self.epislon = 0.1
        self.q_table = {}
        self.n, self.alpha, self.gamma = n, alpha, gamma

    def run(self, agent_host, tetris_game):
        states, actions, rewards = deque(), deque(), deque()
        curr_reward = 0
        done_update = False
        while not done_update:
            init_state = self.get_curr_state(tetris_game)
            possible_actions = self.get_possible_actions(agent_host, tetris_game, True)
            init_action = self.choose_action(init_state, possible_actions, self.epsilon)
            states.append(init_state)
            actions.append(init_action)
            rewards.append(0)

            T = sys.maxint
            for t in xrange(sys.maxint):
                time.sleep(0.1)
                if t < T:
                    curr_reward = self.act(agent_host, A[-1])
                    rewards.append(curr_reward)

                    if self.game.gameover == True:
                        game.startgame()

                    curr_state = self.get_curr_state(tetris_game)
                    states.append(curr_state)
                    possible_actions = self.get_possible_actions(agent_host)
                    next_action = self.choose_action(curr_state, possible_actions, self.epsilon)
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
                
    def act(self, agent_host, action):
        return rand(len(possible_states))

    def get_curr_state(self, tetris_game):
        for i, row in enumerate(tetris_game.board[:-1]):
            if 0 not in row:
                if i  == 0:
                    return tetris_game.board[-1:1]
                else:
                    return tetris_game.board[i:i+1]
                
    def get_possible_actions(self, my_game):
        actions = []
        piece = my_game.piece
        piece_x, piece_y = my_game.piece_x, my_game.piece_y
        
        for i in range(4):
            piece_x = 0
            while piece_x <= my_game.cols - len(piece[0]):
                if not tetris_game.check_collision(my_game.board,
                                       piece,
                                       (piece_x, piece_y)):
                    new_state = self.pred_insta_drop(piece, piece_x, piece_y, my_game.board)
                    new_state = new_state[-3:-1] #Retrieves the bottom two rows
                    new_state = [[1 if x!= 0 else x for x in row]for row in state]
                    if new_state not in actions:
                        actions.append(new_state)
                piece_x += 1
                piece_y = original_y
            piece = self.rotate_piece(piece)
        
        return actions

    def rotate_piece(self, piece):
        new_piece = tetris_game.rotate_clockwise(piece)
        if not tetris_game.check_collision(self.board, new_piece, (self.piece_x, self.piece_y)):
            return new_piece
        else:
            return piece
            
    def pred_insta_drop(self, piece, piece_x, piece_y, board):
        new_board = copy.deepcopy(board)

        while not tetris_game.check_collision(new_board,
                           piece,
                           (piece_x, piece_y+1)):
            piece_y += 1
            
        piece_y += 1
        new_board = join_matrixes(
            new_board,
            piece,
            (piece_x, piece_y))

        return new_board
    
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
    left_x, right_x = 0, 10
    bottom_y, top_y = 58, 80
    z_pos = 3
    mission.drawLine( left_x, bottom_y, z_pos, left_x, top_y, z_pos, "obsidian" )
    mission.drawLine( right_x, bottom_y, z_pos, right_x, top_y, z_pos, "obsidian" )
    mission.drawLine( left_x, bottom_y, z_pos, right_x, bottom_y, z_pos, "obsidian" )
    mission.drawLine( left_x, top_y, z_pos, right_x, top_y, 3, "obsidian" )
    
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
    my_game = TetrisGame()
    print("n=", n)
    for i in range(numIter):
        my_AI.run(agent_host)
