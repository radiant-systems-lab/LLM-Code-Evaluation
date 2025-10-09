# Image Processing and Computer Vision
import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import matplotlib.pyplot as plt
from skimage import filters, measure, morphology
import imageio

def opencv_operations(image_path):
    """OpenCV image processing"""
    img = cv2.imread(image_path)
    if img is None:
        # Create dummy image if file doesn't exist
        img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (15, 15), 0)
    
    # Edge detection
    edges = cv2.Canny(blurred, 50, 150)
    
    # Find contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    return len(contours), edges

def pillow_operations():
    """PIL/Pillow image processing"""
    # Create a sample image
    img = Image.new('RGB', (200, 200), color='red')
    
    # Apply filters
    blurred = img.filter(ImageFilter.BLUR)
    enhanced = ImageEnhance.Brightness(blurred).enhance(1.5)
    
    # Convert and save
    enhanced = enhanced.convert('L')  # Convert to grayscale
    return enhanced

def scikit_image_operations():
    """Scikit-image processing"""
    # Generate sample image
    image = np.random.random((100, 100))
    
    # Apply filters
    gaussian = filters.gaussian(image, sigma=1)
    sobel = filters.sobel(gaussian)
    
    # Morphological operations
    binary = sobel > 0.1
    cleaned = morphology.remove_small_objects(binary, min_size=50)
    
    # Label connected components
    labeled = measure.label(cleaned)
    properties = measure.regionprops(labeled)
    
    return len(properties), labeled

def create_visualization():
    """Create matplotlib visualization"""
    fig, axes = plt.subplots(2, 2, figsize=(10, 10))
    
    # Sample data
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    
    # Plot 1: Line plot
    axes[0, 0].plot(x, y1, 'b-', label='sin(x)')
    axes[0, 0].plot(x, y2, 'r--', label='cos(x)')
    axes[0, 0].legend()
    axes[0, 0].set_title('Trigonometric Functions')
    
    # Plot 2: Scatter plot
    axes[0, 1].scatter(np.random.randn(50), np.random.randn(50), alpha=0.6)
    axes[0, 1].set_title('Random Scatter')
    
    # Plot 3: Histogram
    data = np.random.normal(0, 1, 1000)
    axes[1, 0].hist(data, bins=30, alpha=0.7)
    axes[1, 0].set_title('Normal Distribution')
    
    # Plot 4: Image
    image_data = np.random.random((50, 50))
    axes[1, 1].imshow(image_data, cmap='viridis')
    axes[1, 1].set_title('Random Image')
    
    plt.tight_layout()
    plt.savefig('/tmp/visualization.png')
    plt.close()

if __name__ == "__main__":
    print("Running image processing operations...")
    
    # OpenCV operations
    contour_count, edges = opencv_operations('dummy_image.jpg')
    print(f"OpenCV: Found {contour_count} contours")
    
    # PIL operations
    processed_img = pillow_operations()
    print(f"PIL: Processed image size: {processed_img.size}")
    
    # Scikit-image operations
    region_count, labeled_img = scikit_image_operations()
    print(f"Scikit-image: Found {region_count} regions")
    
    # Create visualization
    create_visualization()
    print("Visualization saved")