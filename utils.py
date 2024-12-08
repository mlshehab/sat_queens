from z3 import Solver, Bool, Sum , And, Or, AtMost, sat, Implies, Not# type: ignore

# heuristic difference between two colors
def color_difference(color1, color2):
    return sum(abs(c1 - c2) for c1, c2 in zip(color1, color2))

# merge similar colors based on the heuristic distance above

# Function to merge similar colors
def merge_colors(colors, threshold=10):
    merged_colors = []
    color_lookup = {}
    
    for color in colors:
        # Check if the color is close to any already merged color
        for merged_color in merged_colors:
            if color_difference(color, merged_color) < threshold:
                color_lookup[color] = merged_color
                break
        else:
            # If no close color is found, add it as a new merged color
            merged_colors.append(color)
            color_lookup[color] = color

    return merged_colors, color_lookup


def ExactlyOne(vars):
    """Ensure exactly one of the variables in the list is True."""
    # At least one must be True
    at_least_one = Or(vars)
    # At most one must be True
    at_most_one = AtMost(*vars, 1)
    # Both conditions must be satisfied
    return And(at_least_one, at_most_one)

def neighbors(i, j, grid_size,grid):
    """Get the list of neighbors (including diagonals) for cell (i, j)."""
    directions = [
        (-1, -1), (-1, 0), (-1, 1),  # Top-left, Top, Top-right
        (0, -1),          (0, 1),   # Left, Right
        (1, -1), (1, 0), (1, 1)     # Bottom-left, Bottom, Bottom-right
    ]
    neighbors_list = []
    for di, dj in directions:
        ni, nj = i + di, j + dj
        if 0 <= ni < grid_size and 0 <= nj < grid_size:  # Ensure neighbor is within bounds
            neighbors_list.append(grid[ni][nj])
    return neighbors_list