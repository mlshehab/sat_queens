import cv2
import numpy as np

# Load the image
image_path = './queens_snapshots/queens_223.png'
image = cv2.imread(image_path)

# Convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply adaptive thresholding to detect gridlines
thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 15, 10)

# Find contours
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Filter out small contours (to ignore noise and focus on grid cells)
cell_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > 50]

# Draw contours (optional, for visualization)
output = image.copy()
cv2.drawContours(output, cell_contours, -1, (0, 255, 0), 2)

# Count the cells
cell_count = len(cell_contours)
print(f'Number of grid cells: {cell_count}')

# Save the output image (optional)
cv2.imwrite('output_grid_cells.png', output)

# Display the output image (optional)
cv2.imshow('Grid Cells', output)
cv2.waitKey(0)
cv2.destroyAllWindows()
