import cv2
import numpy as np
from PIL import Image
from skimage.feature import local_binary_pattern

def calculate_complexity(image_path):
    """Calculate image complexity metrics and return overall complexity score."""
    # Load image consistently
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

    # Calculate the complexity score
    complexity_score = edge_density * variance * texture_complexity
    print("Complexity Score:", complexity_score)
    
    return complexity_score

def classify_complexity(complexity_score):
    """Classify image complexity into categories based on normalized score."""
    # Normalization and classification thresholds
    max_expected_complexity = 1000000  # Empirical threshold
    min_expected_complexity = 0

    # Normalize complexity score to percentage scale
    complexity_percentage = min(100, max(0, (complexity_score - min_expected_complexity) / 
                                         (max_expected_complexity - min_expected_complexity) * 100))
    
    print(f"Complexity Percentage: {complexity_percentage:.2f}%")

    # Classification
    if complexity_percentage > 70:
        return "High Complexity", complexity_percentage
    elif complexity_percentage > 40:
        return "Medium Complexity", complexity_percentage
    else:
        return "Low Complexity", complexity_percentage

def process_and_classify_image(image_path):
    """Process an image and return its complexity classification."""
    # Calculate complexity score
    complexity_score = calculate_complexity(image_path)
    
    # Classify the image
    classification, complexity_percentage = classify_complexity(complexity_score)
    
    print(f"Image: {image_path}")
    print(f"Classification: {classification}")
    
    return classification, complexity_percentage

# Example usage
if __name__ == "__main__":
    image_path = "test1.jpg"  # Replace with your image path
    classification, complexity_percentage = process_and_classify_image(image_path)
