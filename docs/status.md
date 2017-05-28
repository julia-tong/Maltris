---
layout: default
title:  Status
---

## Project summary:

Our project is to recreate tetris in Minecraft using Malmo. Our goal is to use a combination of reinforcement learning and neural networks for our AI. The game will be in survival mode, so our AI is not trying to win necessarily, but it will try to keep the game running as long as possible until the blocks reach the very top. 

Since we've created a tetris board, we will take in the current state of the board and the incoming piece as input. Then we will calculate every possible orientation and placement of the incoming piece and score the board. We score the board by taking account into the total height of all the pieces, the number of holes, and the number of complete lines to clear. Increasing the total height and having holes in the board will result in negative reward, whereas having complete lines will have a positive reward. A combination of these 3 factors will determine the score of the board. Our AI will then use reinforcement learning to repeatedly drop pieces in the board to increase the reward for each game.

## Approach:

The main algorithm we're using for reinforcement learning is SARSA.

!!! ADD MORE INFO ABOUT OUR SARSA ALGORITHM HERE !!!

The state of our game is simply the arrangement of the pieces on our board. The number of states that we have is the different combinations of the incoming piece on the tetris board. Some pieces such as the O and I pieces will have less states because some rotations will result in the same arrangement of pieces on the board. To avoid extra computations, we only keep track of different/distinct states of the board.

The actions of our game involves 2 facts: the rotation/orientation and the placement of the incoming piece. There are 4 rotations for each piece, but some pieces like the O and I pieces may not look different for each rotation. The number of actions that we have is the different number of orientations times the number of placements across the board for the incoming piece.

To calculate the reward for each game, we currently have a reward map, where increasing height of the pieces has a reward of -8, holes have a reward of -5, and clearing/completing a line has a reward of 20. We take the linear combination of these 3 to determine the reward.

## Evaluation:

We first generate a random seed for a predictable game so that each play will be similar through each iteration during training.  Then using a few runs, we evaluate against each in randomized moves, Q-learning, and a Neural Network, and a human player to determine how long in minutes or hours the player will survive.  We may also account for the number of lines cleared.

## Remaining Goals and Challenges:
