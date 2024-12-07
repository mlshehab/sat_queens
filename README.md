# Description

This is a fun project that solves [queens game](https://www.linkedin.com/games/queens/) from linkedin using the Theorem Prover ```z3```. 

The game is a 10 by 10 grid, and the goal is place queens over the grid such that:

1. Each color region has exactly one queen.
2. Each row has exactly one queen. 
3. Each column has exactly one queen.
4. No two queens can be neighbors. 

For example, this is the visualization of the solution of Queens 220:

![queens 220 solution](./md_images/queens_220_solved.png)


# Methodology

The code takes in as input an snapshot of the empty board. For our running example, it is the figure ```./queens_snapshots/queens_220.png```,  shown below.

![queens 220 empty](./md_images/queens_220_plain.png)
