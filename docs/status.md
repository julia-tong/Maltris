---
layout: default
title:  Status
---

<iframe width="640" height="360" src="https://www.youtube.com/embed/wE5FiFmh3Qo" frameborder="0" allowfullscreen></iframe>

## Project summary:

Our project is to create a Tetris AI in Minecraft using Malmo. This also means we will be recreating Tetris itself using the Malmo API. Our main goal is to use a combination of reinforcement learning and neural networks for our Intelligence. We will be focusing on Surival Mode, so our AI is not aiming for the highest score possible, but instead to be able to play the game for as long as possible without reaching game over(Once the blocks go over the ceiling limit).

Since we've created a tetris board, we will take in the current state of the board and the incoming piece as input. Then we will calculate every possible orientation and placement of the incoming piece and score the board. We score the board by taking account into the total height of all the pieces, the number of holes, and the number of complete lines to clear. Increasing the total height and having holes in the board will result in negative reward, whereas having complete lines will have a positive reward. A combination of these 3 factors will determine the score of the board. Our AI will then use reinforcement learning to repeatedly drop pieces in the board to increase the reward for each game.

## Approach:

The main algorithm we're using for reinforcement learning is Q-Learning. Our implementation of updating the q-table is similar to the implementation used in assignment 2, where tau represents the state to update, S represents the states, A represents the actions for state S, R represents the rewards for actions A, and T represents the terminating state. Our agent selects an action that is optimal for each state. Then evaluates the board to retrieve the reward and observes the new state. This will result in the highest long-term reward. In our case, the more lines our AI is able to clear, the higher the reward will be.

    def update_q_table(self, tau, S, A, R, T):
        curr_s, curr_a, curr_r = magic(S.popleft()), A.popleft(), R.popleft()
        next_s = magic(curr_a)
        G = sum([self.gamma ** i * R[i] for i in range(len(S))])
        if tau + self.n < T:
            G += self.gamma ** self.n * self.q_table[magic(S[-1])][magic(A[-1])]
        
        old_q = self.q_table[curr_s][next_s]
        self.q_table[curr_s][next_s] = old_q + self.alpha* (G - old_q)

The state of our game is simply the arrangement of the pieces on our board. Each state is the highest two rows containing at least one block in them. This means we are using a working space window of 2 height. Although this means we will not be capturing as much information, this drasticly lowers the number of possible states to capture. The number of states that we have is the different combinations of the incoming piece on the tetris board. Some pieces such as the O and I pieces will have less states because some rotations will result in the same arrangement of pieces on the board. To avoid extra computations, we only keep track of different/distinct states of the board. In total, this means the number of possible states is 1024, as it is 2 raised to the power of 10. Despite this being so large, the number of possible state transitions is much smaller as you can only transition to certain states from the given state.

The actions of our game involves 2 factors: the rotation/orientation and the placement of the incoming piece. There are 4 rotations for each piece, but some pieces like the O and I pieces may not look different for each rotation. The number of actions that we have is the different number of orientations multiplied by the number of placements across the board for the incoming piece. In order to resolve the different pieces, for the sake of the Q-Table we use the resulting state from said action in our action list.

To calculate the reward for each game, we currently have a reward map, where increasing height of the pieces has a reward of -8, holes have a reward of -5, and clearing/completing a line has a reward of 20. We take the linear combination of these 3 to determine the reward. These numbers were chosen somewhat arbitrarily, and will likely change as we run further tests and experiment.

Our current board is only has a width of 5, as opposed to the standard 10. We also have simplified the pieces coming in, as can be seen in the video. 

## Evaluation:

We first generate a random seed for a predictable game so that each play will be similar through each iteration during training.  Then using a few runs, we evaluate against each in randomized moves, Q-learning, and a Neural Network, and a human player to determine how long in minutes or hours the player will survive.  We may also account for the number of lines cleared.

Two factors we take into consideration for evaluation are: the number of lines that are cleared and the length of one game. In the first few minutes of running the game repeatedly, the number of lines cleared are all 0. Then our AI will start learning that clearing lines result in a higher reward. We printed out the number of lines that were cleared for each game. 

    ('Made it to level:', 28)
    ('Total Line Clears:', 3)
    ('Made it to level:', 16)
    ('Total Line Clears:', 0)
    ('Made it to level:', 17)
    ('Total Line Clears:', 0)
    ('Made it to level:', 13)
    ('Total Line Clears:', 0)
    ('Made it to level:', 17)
    ('Total Line Clears:', 2)

In this case, we can see that one game was able to clear 3 lines and another was able to clear 2. Our AI is improving, but at a pretty slow rate at the moment. 

In the first few games that are run, the length of the one game is shorter than the length of a game after running it for a few minutes. Because the AI slowly learns that clearing lines result in a higher reward, it may take a little longer for the game to finish if it is actually able to place and rotate each piece in a strategic manner. When we run the game with a random generator, the game seems to end almost instantaneously.

Even though the length of each game is strongly correlated to the number of lines that are cleared, which directly determines how well our AI is doing, it's still a good indicator for the success of our AI because our goal is to ultimately keep our AI in "survival mode." The game should keep going for as long as possible.

## Remaining Goals and Challenges:

Some goals for the next few weeks include: simulating our game on a full tetris board (10x20 blocks) with full sized pieces, trying to prolong the length of one game (clearing as many lines as possible), as well as improve our heuristic function.

Currently, our game is simulated on a smaller scale to cut down on computations and to see if our AI is making any progress. We will work to run our AI on a full scale tetris game after we make our advancements. 

Our method for calculating a state could potentially see improvement. As of now, if one side of the board is higher than the rest, the action taken will give little information in the transition, as the working window will see the same state. This might be improved by accounting for the height in the state itself.

The implementation of calculating the height of the board right now is simply taking the height of the tallest column of the board. However, later on we want to change it to calculate the aggregate height of the entire board-- meaning it will sum the height of each column on the board. This will encourage our AI to drop more pieces before reaching the top of the board. The implementation of calculating the number of holes will also need some tweaking because it's not accurate in detecting holes/empty spaces right now. 

Lastly, if there is time remaining, we desire to extend our algorithm into a Neural Network, as it should be able to handle the information given in more complex ways. This is because the relationship between height, states, and holes is difficult to represent in the standard Reinforcement Learning approach, and deep learning may have some insight to the problem.
