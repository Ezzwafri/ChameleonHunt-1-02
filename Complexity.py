import cv2
import numpy as np
from PIL import Image
from skimage.feature import local_binary_pattern

# Load image consistently
image_path = "test1.jpg"
# For edge detection
cv_image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
# For variance calculation
pil_image = Image.open(image_path)
pil_array = np.array(pil_image)
# For texture analysis
skimage_gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

# Apply Canny Edge Detection
edges = cv2.Canny(cv_image, 100, 200)

# Calculate Edge Density
edge_density = np.sum(edges) / (cv_image.shape[0] * cv_image.shape[1])
print("Edge Density:", edge_density)

# Compute variance
variance = np.var(pil_array)
print("Color Variance:", variance)

# Compute LBP texture descriptor
lbp = local_binary_pattern(skimage_gray, P=8, R=1, method='uniform')

# Calculate entropy as texture complexity measure
texture_complexity = np.mean(lbp)
print("Texture Complexity:", texture_complexity)

complexity_score = edge_density * variance * texture_complexity
print("Overall Complexity Score:", complexity_score)
