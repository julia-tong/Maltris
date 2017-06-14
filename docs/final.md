---
layout: default
title:  Final Report
---

## Video

<iframe width="640" height="360" src="https://www.youtube.com/embed/tsxv0VUbHe8?rel=0" frameborder="0" allowfullscreen></iframe>

## Project Summary

Our project is to create a Tetris AI in Minecraft using Malmo. This also means we will be recreating Tetris itself using the Malmo API. Our main goal is to use a combination of reinforcement learning and genetic algorithm for our Intelligence. We will be focusing on Surival Mode, so our AI is not aiming for the highest score possible, but instead to be able to play the game for as long as possible without reaching game over. (The game is over once the blocks go over the ceiling limit).

Since we've created a tetris board, we will take in the current state of the board and the incoming piece as input. Then we will calculate every possible orientation and placement of the incoming piece and score the board. We score the board by taking account into the total height of all the pieces, the number of holes, and the number of complete lines to clear. Increasing the total height and the number of holes in the board will result in negative rewards, whereas having complete lines will have a positive reward. A combination of these 3 factors will determine the score of the board. Our AI will then use reinforcement learning to repeatedly drop pieces in the board to increase the reward for each game.

## Approaches

Our baseline that we're comparing our AI to is simply generating a random orientation and placement for the incoming piece. Some advantages of this approach is that it takes less time and calculations to generate the next action. However, there are many disadvantages because it results in poor decisions (it doesn't really know how to make a "good" decision in this case) and it doesn't improve over time. Ultimately, it is not sufficient to complete our goal.

Our first approach for our AI is to use Q-Learning. Our implementation of updating the q-table is similar to the implementation used in assignment 2, where tau represents the state to update, S represents the states, A represents the actions for state S, R represents the rewards for actions A, and T represents the terminating state. Our agent selects an action that is optimal for each state. Then evaluates the board to retrieve the reward and observes the new state. This will result in the highest long-term reward. In our case, the more lines our AI is able to clear, the higher the reward will be.

    def update_q_table(self, tau, S, A, R, T):
        curr_s, curr_a, curr_r = magic(S.popleft()), A.popleft(), R.popleft()
        next_s = magic(curr_a)
        G = sum([self.gamma ** i * R[i] for i in range(len(S))])
        if tau + self.n < T:
            G += self.gamma ** self.n * self.q_table[magic(S[-1])][magic(A[-1])]
        
        old_q = self.q_table[curr_s][next_s]
        self.q_table[curr_s][next_s] = old_q + self.alpha* (G - old_q)

The state of our game is simply the arrangement of the pieces on our board. Each state is the highest two rows containing at least one block in them. This means we are using a working space window of 2 height. Although this means we will not be capturing as much information, this drasticly lowers the number of possible states to capture. 

Our state space is the different combinations of the incoming piece on the tetris board. Some pieces such as the O and I pieces will have less states because some rotations will result in the same arrangement of pieces on the board. To avoid extra computations, we only keep track of different/distinct states of the board. In total, this means that our state space is 1024. We arrive at the number 1024 because we're working with the top 2 rows that are 5 columns wide. Thus, our state space is 2^10 = 1024. Despite this being so large, the number of possible state transitions is much smaller as you can only transition to certain states from the given state.

The actions of our game involves 2 factors: the rotation/orientation and the placement of the incoming piece. There are 4 rotations for each piece, but some pieces like the O and I pieces may not look different for each rotation. The number of actions that we have is the different number of orientations multiplied by the number of placements across the board for the incoming piece. In order to resolve the different pieces, for the sake of the Q-Table we use the resulting state from said action in our action list.

To calculate the reward for each game, we currently have a reward map, where increasing the height of the pieces has a reward of -20, holes have a reward of -20, and clearing/completing a line has a reward of 50. We take the linear combination of these 3 to determine the reward. These numbers were chosen somewhat arbitrarily, but they have changed over the course of the project. We came to the conclusion that this is a pretty good proportion of negative rewards vs. positive rewards. Before, our negative rewards were given too much weight, so having a positive reward wouldn't really make a huge impact on the score.

Comparing our AI to our baseline, our AI certainly has more calculations (to determine the score of the board and decide which action to take) and requires more data (such as the q-table). However, the results from using Q-Learning are much better than our baseline because we can observe our AI clearing more lines from the board over time and it actually shows improvement, which is ultimately what we're trying to achieve.

## Evaluation

Two factors we take into consideration for evaluation are: the number of lines that are cleared and the level of one game (the number of pieces dropped in the board). In the first few minutes of running the game repeatedly, the number of lines cleared are all 0. Then our AI will start learning that clearing lines result in a higher reward.

We compared our AI to our baseline that used randomzied moves. These are the results we observed:

**Q-Learning (9350 games played)**

    ('Made it to level:', 15)
    ('Total Line Clears:', 0)
    ('Made it to level:', 19)
    ('Total Line Clears:', 3)
    ('Made it to level:', 19)
    ('Total Line Clears:', 2)
    ('Made it to level:', 19)
    ('Total Line Clears:', 2)
    ('Made it to level:', 15)
    ('Total Line Clears:', 0)
    ('Best attempt, gamesplayed: ', 9350, ' avglvls: ', 15.845347593582888, ' avgclears: ', 0.75133689839572193)
    
**Q-Learning (9450 games played)**

    ('Made it to level:', 19)
    ('Total Line Clears:', 1)
    ('Made it to level:', 13)
    ('Total Line Clears:', 0)
    ('Made it to level:', 19)
    ('Total Line Clears:', 3)
    ('Made it to level:', 15)
    ('Total Line Clears:', 0)
    ('Made it to level:', 13)
    ('Total Line Clears:', 0)
    ('Best attempt, gamesplayed: ', 9450, ' avglvls: ', 15.857142857142858, ' avgclears: ', 0.75534391534391532)
    
We can observe here that just after 100 games are played using Q-Learning, our average levels have increased by 0.01179 blocks and our average number of lines cleared have increased by 0.004 lines. This indicates that our AI is slowly improving over time.

**Random (5090 games played)**

    ('Made it to level:', 13)
    ('Total Line Clears:', 0)
    ('Made it to level:', 11)
    ('Total Line Clears:', 0)
    ('Made it to level:', 16)
    ('Total Line Clears:', 1)
    ('Made it to level:', 14)
    ('Total Line Clears:', 0)
    ('Made it to level:', 13)
    ('Total Line Clears:', 1)
    ('Best attempt, gamesplayed: ', 5090, ' avglvls: ', 14.703732809430255, ' avgclears: ', 0.39233791748526525)

**Random (5190 games played)**

    ('Made it to level:', 19)
    ('Total Line Clears:', 2)
    ('Made it to level:', 18)
    ('Total Line Clears:', 2)
    ('Made it to level:', 9)
    ('Total Line Clears:', 0)
    ('Made it to level:', 8)
    ('Total Line Clears:', 0)
    ('Made it to level:', 16)
    ('Total Line Clears:', 0)
    ('Best attempt, gamesplayed: ', 5190, ' avglvls: ', 14.702504816955685, ' avgclears: ', 0.39113680154142583)

When running 100 games with randomized moves, our average levels have actually decreased by 0.0012 blocks and our average number of lines cleared have increased by 0.0012 lines. This serves as a baseline for us since there is clearly no improvement when have pieces randomly placed, whereas our AI with Q-Learning actually shows improvement in average levels and average number of lines cleared over time.

In the first few games that are run, the length of the one game is shorter than the length of a game after running it for a few minutes. Because the AI slowly learns that clearing lines result in a higher reward, it may take a little longer for the game to finish if it is actually able to place and rotate each piece in a strategic manner. When we run the game with a randomized moves, the game seems to end almost instantaneously.

Even though the length of each game is strongly correlated to the number of lines that are cleared, which directly determines how well our AI is doing, it's still a good indicator for the success of our AI because our goal is to ultimately keep our AI in "survival mode." The game should keep going for as long as possible.

Below are some details on the data collected through training the Q-Learning algorithms.  The following models were tested by the state's input of the top one to three rows of the tetris board.

![](https://github.com/julia-tong/Maltris/blob/master/plotgraphdata/bestavgLvlPlot.png?raw=true "Maltris")
The graph above shows the average game levels played over the training period of 3 Q-learning models and the baseline random evaluation. The result is that as state space increases, it takes longer to train and slower to reach an optimal solution. As a note, the second (shortest) line in each type of model is the optimized heuristic.

![](https://github.com/julia-tong/Maltris/blob/master/plotgraphdata/bestavgClearsPlot.png?raw=true "Maltris")
Similarly the graph above shows the average cleared lines over the training period of 3 Q-learning models and the baseline random evaluation.  As a note, the second (shortest) line in each type of model is the optimized heuristic.

![](https://github.com/julia-tong/Maltris/blob/master/plotgraphdata/histlvls.png?raw=true "Maltris")
This figure shows the frequency of the game counts in the three Q-learning algorithm models.

![](https://github.com/julia-tong/Maltris/blob/master/plotgraphdata/histclears.png?raw=true "Maltris")
This figure shows the frequency of the lines cleared in the three Q-learning algorithm models.


## References

[https://github.com/Microsoft/malmo](https://github.com/Microsoft/malmo)

[https://gist.github.com/silvasur/565419](https://gist.github.com/silvasur/565419)

[http://cs231n.stanford.edu/reports/2016/pdfs/121_Report.pdf](http://cs231n.stanford.edu/reports/2016/pdfs/121_Report.pdf)

[http://www.math.tau.ac.il/~mansour/rl-course/student_proj/livnat/tetris.html](http://www.math.tau.ac.il/~mansour/rl-course/student_proj/livnat/tetris.html)

[https://www.elen.ucl.ac.be/Proceedings/esann/esannpdf/es2008-118.pdf](https://www.elen.ucl.ac.be/Proceedings/esann/esannpdf/es2008-118.pdf)
