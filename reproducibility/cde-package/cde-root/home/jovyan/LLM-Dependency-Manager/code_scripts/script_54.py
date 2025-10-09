#!/usr/bin/env python3
"""
Script 4: Image Processing with OpenCV and PIL
Tests computer vision and image manipulation dependencies
"""

import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
import matplotlib.pyplot as plt

def process_images():
    """Image processing pipeline"""
    print("Starting image processing pipeline...")
    
    # Create synthetic image using numpy
    width, height = 640, 480
    img_array = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
    
    # OpenCV operations
    gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(img_array, (15, 15), 0)
    
    print(f"OpenCV processing complete: Image shape {img_array.shape}")
    
    # PIL operations
    pil_image = Image.fromarray(img_array)
    
    # Apply filters
    filtered = pil_image.filter(ImageFilter.EDGE_ENHANCE)
    
    # Adjust brightness
    enhancer = ImageEnhance.Brightness(pil_image)
    brightened = enhancer.enhance(1.5)
    
    print(f"PIL processing complete: Image size {pil_image.size}")
    
    # Create visualization
    fig, axes = plt.subplots(2, 2, figsize=(10, 10))
    axes[0, 0].imshow(img_array)
    axes[0, 0].set_title('Original')
    axes[0, 1].imshow(gray, cmap='gray')
    axes[0, 1].set_title('Grayscale')
    axes[1, 0].imshow(edges, cmap='gray')
    axes[1, 0].set_title('Edges')
    axes[1, 1].imshow(blurred)
    axes[1, 1].set_title('Blurred')
    
    plt.tight_layout()
    plt.savefig('image_processing_results.png')
    print("Results saved to image_processing_results.png")
    
    return {
        'original_shape': img_array.shape,
        'edges_detected': np.sum(edges > 0),
        'processing_complete': True
    }

if __name__ == "__main__":
    results = process_images()
    print(f"Processing summary: {results}")