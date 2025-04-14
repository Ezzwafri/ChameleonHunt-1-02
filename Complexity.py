import cv2
import numpy as np

# Load image
image_1 = cv2.imread("test1.jpeg", cv2.IMREAD_GRAYSCALE)

# Apply Canny Edge Detection
edges = cv2.Canny(image, 100, 200)

# Calculate Edge Density
edge_density = np.sum(edges) / (image.shape[0] * image.shape[1])
print("Edge Density:", edge_density)

from PIL import Image
import numpy as np

# Load image
image_1 = Image.open("test1.jpeg")
image_array = np.array(image)

# Compute variance
variance = np.var(image_array)
print("Color Variance:", variance)

from skimage.feature import local_binary_pattern
from skimage import io
import numpy as np

# Load image in grayscale
image_1 = io.imread("test1.jpeg", as_gray=True)

# Compute LBP texture descriptor
lbp = local_binary_pattern(image, P=8, R=1, method='uniform')

# Calculate entropy as texture complexity measure
texture_complexity = np.mean(lbp)
print("Texture Complexity:", texture_complexity)

complexity_score = edge_density * variance * texture_complexity
print("Overall Complexity Score:", complexity_score)