import cv2
import numpy as np
from PIL import Image
from skimage.feature import local_binary_pattern

# Load image consistently
<<<<<<< HEAD
image_path = "test2.jpg"
=======
image_path = "test1.jpg"
>>>>>>> 0335502bd6b2501ad8a3919bda6d07779fe3adab
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

<<<<<<< HEAD
# Calculate the complexity score
complexity = edge_density * variance * texture_complexity

# Normalize to a 0-100% scale
# You'll need to determine appropriate min/max values based on your image dataset
# This is a simple approach - adjust based on your specific needs
max_expected_complexity = 1000000  # Set this based on empirical testing of your images
min_expected_complexity = 0

# Normalize to percentage
complexity_percentage = min(100, max(0, (complexity - min_expected_complexity) / 
                          (max_expected_complexity - min_expected_complexity) * 100))

print(f"Overall Complexity Score: {complexity_percentage:.2f}%")
=======
complexity_score = edge_density * variance * texture_complexity
print("Overall Complexity Score:", complexity_score)
>>>>>>> 0335502bd6b2501ad8a3919bda6d07779fe3adab

def classify_complexity(complexity_score):
    # Normalization and classification thresholds
    max_expected_complexity = 1000000  # Empirical threshold
    min_expected_complexity = 0

    # Normalize complexity score to percentage scale
    complexity_percentage = min(100, max(0, (complexity_score - min_expected_complexity) / 
                                         (max_expected_complexity - min_expected_complexity) * 100))
    
    print(f"Normalized Complexity Percentage: {complexity_percentage:.2f}%")

    # Classification
    if complexity_percentage > 70:
        return "High Complexity"
    elif complexity_percentage > 40:
        return "Medium Complexity"
    else:
        return "Low Complexity"

# Example usage
image_path = "test.jpg"  # Replace with your image path
complexity_score = calculate_complexity(image_path)
classification = classify_complexity(complexity_score)

print(f"Image Classification: {classification}")