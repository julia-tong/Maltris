## Project summary:

Our project is to recreate tetris in Minecraft using Malmo. Our goal is to use a combination of reinforcement learning and neural networks for our AI. The game will be in survival mode, so our AI is not trying to win necessarily, but it will try to keep the game running as long as possible without having the blocks reach the very top. 

Since we've created a tetris board, we will take in the current state of the board and the incoming piece as input. Then we will calculate every possible orientation and placement of the incoming piece and score it. We score the board by taking account into the total height of all the pieces, holes, and if there are any complete lines. Increasing the total height and having holes will result in negative reward, whereas having complete lines will have a positive reward. A combination of these 3 will determine the score of the board. Our AI will then use reinforcement learning to repeatedly drop pieces in the board to increase the reward.

## Approach:

The main algorithm we're using for reinforcement learning is Q-learning.  

## Evaluation:

## Remaining Goals and Challenges:
