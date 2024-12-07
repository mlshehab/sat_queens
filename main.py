import numpy as np 
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image
from z3 import Solver, Bool, Sum , And, Or, AtMost, sat, Implies, Not# type: ignore

# Function to compute the difference between two colors
def color_difference(color1, color2):
    return sum(abs(c1 - c2) for c1, c2 in zip(color1, color2))

# Function to merge similar colors
def merge_colors(colors, threshold=10):
    merged_colors = []
    color_map = {}
    
    for color in colors:
        # Check if the color is close to any already merged color
        for merged_color in merged_colors:
            if color_difference(color, merged_color) < threshold:
                color_map[color] = merged_color
                break
        else:
            # If no close color is found, add it as a new merged color
            merged_colors.append(color)
            color_map[color] = color

    return merged_colors, color_map


input_image_path = './queens_snapshots/queens_220.png'

# Load the image
image = Image.open(input_image_path)

# Grid size and image dimensions
grid_size = 10
image_width, image_height = image.size
cell_width = image_width // grid_size
cell_height = image_height // grid_size

# Extract colors from the centers of grid cells
unique_colors = set()
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

# Merge similar colors
merged_colors, color_map = merge_colors(unique_colors)

# Map merged colors to symbolic names dynamically (c1 to cN)
color_definitions = {color: f"c{i+1}" for i, color in enumerate(merged_colors)}

# Generate the 10x10 symbolic matrix
color_matrix = []

for row in grid_centers:
    symbolic_row = [color_definitions[color_map[color]] for color in row]
    color_matrix.append(symbolic_row)

# Print the dynamically created color definitions and the matrix
# print("Color Definitions (Merged):")
# for color, symbol in color_definitions.items():
#     print(f"{symbol}: {color}")

# print("\nColor Matrix:")
# for row in color_matrix:
#     print(row)


def ExactlyOne(vars):
    """Ensure exactly one of the variables in the list is True."""
    # At least one must be True
    at_least_one = Or(vars)
    # At most one must be True
    at_most_one = AtMost(*vars, 1)
    # Both conditions must be satisfied
    return And(at_least_one, at_most_one)

# Define the 10x10 grid of Boolean variables
grid = [[Bool("x_%s_%s"%(i,j)) for j in range(10)] for i in range(10)]
# print(f"grid is {grid}")
# Z3 Solver
solver = Solver()
solver.reset()
# Constraint 1: Each row must have exactly one cell with value 1
for i in range(10):
    solver.add(ExactlyOne(grid[i]))

# Constraint 2: Each column must have exactly one cell with value 1
for j in range(10):
    solver.add(ExactlyOne([grid[i][j] for i in range(10)]))

# Example color definitions and grid matrix (replace this with your actual color data)
# Assuming color_matrix contains color symbols like ['c1', 'c2', ..., 'c10'] as rows of strings


# # Group cells by color
color_groups = {}
for i in range(10):
    for j in range(10):
        color = color_matrix[i][j]
        if color not in color_groups:
            color_groups[color] = []
        color_groups[color].append(grid[i][j])

# Constraint 3: Among all cells of the same color, exactly one is True
for color, cells in color_groups.items():
    solver.add(ExactlyOne(cells))


# Constraint 4: No neighboring cells (including diagonals) can both be True
def neighbors(i, j):
    """Get the list of neighbors (including diagonals) for cell (i, j)."""
    directions = [
        (-1, -1), (-1, 0), (-1, 1),  # Top-left, Top, Top-right
        (0, -1),          (0, 1),   # Left, Right
        (1, -1), (1, 0), (1, 1)     # Bottom-left, Bottom, Bottom-right
    ]
    neighbors_list = []
    for di, dj in directions:
        ni, nj = i + di, j + dj
        if 0 <= ni < 10 and 0 <= nj < 10:  # Ensure neighbor is within bounds
            neighbors_list.append(grid[ni][nj])
    return neighbors_list

# Add constraints for all cells
for i in range(10):
    for j in range(10):
        # If grid[i][j] is True, all its neighbors must be False
        solver.add(Or(Not(grid[i][j]), And([Not(neighbor) for neighbor in neighbors(i, j)])))


while True:

    if solver.check() == sat:
        model = solver.model()
        solution = [
            ['1' if model.evaluate(grid[i][j]) else '0' for j in range(10)]
            for i in range(10)
        ]
        
        # Save the solution into a matrix variable
        matrix = solution

        print("Solution saved into matrix:")
        for row in matrix:
            print(row)

        block_clause = []

        for i in range(10):
            for j in range(10):
                # For boolean variables, B[ap][i][j], add the constraint that the current solution
                # is not equal to the previous solution
                block_clause.append(grid[i][j] != model.evaluate(grid[i][j], model_completion=True))

        # Add the blocking clause to the solver
        solver.add(Or(block_clause))
    else:
        print("No more solution exists.")
        break 

input_image = mpimg.imread(input_image_path)

# Set up the plot
fig, ax = plt.subplots(figsize=(8, 8))
ax.imshow(input_image, extent=(0, 10, 0, 10))  # Align grid with image coordinates
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)

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
ax.set_xticks(np.arange(0, 11, 1))
ax.set_yticks(np.arange(0, 11, 1))
ax.grid(color='black', linestyle='--', linewidth=0.5)

plt.show()
