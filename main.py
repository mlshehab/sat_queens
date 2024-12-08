import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
from z3 import Solver, Bool, Sum , And, Or, AtMost, sat, Implies, Not # type: ignore
from utils import *


input_image_path = './queens_snapshots/queens_222.png'

# Load the image
image = Image.open(input_image_path)

# Grid size and image dimensions
# TODO: automate the computation of the grid_size

grid_size = 9
image_width, image_height = image.size
cell_width = image_width // grid_size
cell_height = image_height // grid_size


unique_colors = set()
# this will be just a place holder to construct the color matrix later
grid_centers = []

for row in range(grid_size):
    row_centers = []
    for col in range(grid_size):
        # Compute the center of the current cell
        center_x = int((col + 0.5) * cell_width)
        center_y = int((row + 0.5) * cell_height)

        # Get the color at the center
        center_color = image.getpixel((center_x, center_y))
        unique_colors.add(center_color)
        row_centers.append(center_color)

    grid_centers.append(row_centers)

print(f"grid centers are: {grid_centers}")
# Merge similar colors
merged_colors, color_lookup = merge_colors(unique_colors)

color_definitions = {color: f"c{i+1}" for i, color in enumerate(merged_colors)}

color_matrix = []

for row in grid_centers:
    symbolic_row = [color_definitions[color_lookup[color]] for color in row]
    color_matrix.append(symbolic_row)

print("\nColor Matrix:")
for row in color_matrix:
    print(row)

# Define the 10x10 grid of Boolean variables
grid = [[Bool("x_%s_%s"%(i,j)) for j in range(grid_size)] for i in range(grid_size)]

# Z3 Solver
solver = Solver()
solver.reset()
# Constraint 1: Each row must have exactly one cell with value 1
for i in range(grid_size):
    solver.add(ExactlyOne(grid[i]))

# Constraint 2: Each column must have exactly one cell with value 1
for j in range(grid_size):
    solver.add(ExactlyOne([grid[i][j] for i in range(grid_size)]))

# Group cells by color
color_groups = {}
for i in range(grid_size):
    for j in range(grid_size):
        color = color_matrix[i][j]
        if color not in color_groups:
            color_groups[color] = []
        color_groups[color].append(grid[i][j])

# Constraint 3: Among all cells of the same color, exactly one is True
for color, cells in color_groups.items():
    solver.add(ExactlyOne(cells))

# Constraint 4: No neighboring cells (including diagonals) can both be True
for i in range(grid_size):
    for j in range(grid_size):
        # If grid[i][j] is True, all its neighbors must be False
        solver.add(Implies(grid[i][j],And([Not(neighbor) for neighbor in neighbors(i, j,grid_size,grid)]) ))

# Check all possible solutions
while True:

    if solver.check() == sat:
        model = solver.model()
        solution = [
            ['1' if model.evaluate(grid[i][j]) else '0' for j in range(grid_size)]
            for i in range(grid_size)
        ]
        
        # Save the solution into a matrix variable
        matrix = solution

        print("\nSolution saved into matrix:")
        for row in matrix:
            print(row)

        block_clause = []

        for i in range(grid_size):
            for j in range(grid_size):
                # For boolean variables, B[ap][i][j], add the constraint that the current solution
                # is not equal to the previous solution
                block_clause.append(grid[i][j] != model.evaluate(grid[i][j], model_completion=True))

        # Add the blocking clause to the solver
        solver.add(Or(block_clause))
    else:
        print("\nNo more solution exists.")
        break 

input_image = mpimg.imread(input_image_path)

# Set up the plot
fig, ax = plt.subplots(figsize=(8, 8))
ax.imshow(input_image, extent=(0, grid_size, 0, grid_size))  # Align grid with image coordinates
ax.set_xlim(0, grid_size)
ax.set_ylim(0, grid_size)

# Overlay simple circles to represent chess pieces
for i in range(len(matrix)):
    for j in range(len(matrix[i])):
        if matrix[i][j] == '1':
            # Calculate the center of the grid cell
            x_center = j + 0.5
            y_center = len(matrix) - i - 0.5  # Reverse y to match image coordinates
            # Draw a circle as the chess piece
            circle = plt.Circle((x_center, y_center), 0.3, color="red", fill=True)
            ax.add_artist(circle)

# Customize gridlines for better visualization
ax.set_xticks(np.arange(0, grid_size+1, 1))
ax.set_yticks(np.arange(0, grid_size+1, 1))
ax.grid(color='black', linestyle='--', linewidth=0.5)

plt.show()
