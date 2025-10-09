# Computer Vision and Image Recognition
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from skimage import filters, segmentation, measure, morphology
from skimage.feature import hog, local_binary_pattern, corner_harris, corner_peaks
from skimage.transform import hough_line, hough_circle, radon
import tensorflow as tf
from tensorflow.keras.applications import VGG16, ResNet50
from tensorflow.keras.preprocessing import image
import torch
import torchvision.transforms as transforms
import face_recognition
import dlib
import mediapipe as mp

def image_preprocessing():
    """Advanced image preprocessing techniques"""
    try:
        # Create synthetic test images
        height, width = 512, 512
        
        # Generate geometric test image
        test_image = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add shapes for testing
        cv2.rectangle(test_image, (50, 50), (150, 150), (255, 0, 0), -1)  # Red rectangle
        cv2.circle(test_image, (300, 100), 50, (0, 255, 0), -1)  # Green circle
        cv2.ellipse(test_image, (400, 300), (60, 40), 45, 0, 360, (0, 0, 255), -1)  # Blue ellipse
        
        # Add noise and texture
        noise = np.random.randint(0, 50, (height, width, 3), dtype=np.uint8)
        test_image = cv2.add(test_image, noise)
        
        # Convert to grayscale for some operations
        gray_image = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
        
        # Noise reduction
        # Gaussian blur
        gaussian_blur = cv2.GaussianBlur(test_image, (15, 15), 0)
        
        # Bilateral filter (edge-preserving)
        bilateral = cv2.bilateralFilter(test_image, 9, 75, 75)
        
        # Non-local means denoising
        denoised = cv2.fastNlMeansDenoisingColored(test_image, None, 10, 10, 7, 21)
        
        # Edge detection
        # Canny edge detection
        edges_canny = cv2.Canny(gray_image, 50, 150)
        
        # Sobel edge detection
        sobelx = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=5)
        sobely = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=5)
        sobel_combined = np.sqrt(sobelx**2 + sobely**2)
        
        # Laplacian edge detection
        laplacian = cv2.Laplacian(gray_image, cv2.CV_64F)
        
        # Morphological operations
        kernel = np.ones((5, 5), np.uint8)
        
        # Erosion and dilation
        erosion = cv2.erode(gray_image, kernel, iterations=1)
        dilation = cv2.dilate(gray_image, kernel, iterations=1)
        
        # Opening and closing
        opening = cv2.morphologyEx(gray_image, cv2.MORPH_OPEN, kernel)
        closing = cv2.morphologyEx(gray_image, cv2.MORPH_CLOSE, kernel)
        
        # Gradient
        gradient = cv2.morphologyEx(gray_image, cv2.MORPH_GRADIENT, kernel)
        
        # Histogram operations
        # Histogram equalization
        equalized = cv2.equalizeHist(gray_image)
        
        # CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        clahe_result = clahe.apply(gray_image)
        
        # Geometric transformations
        rows, cols = gray_image.shape
        
        # Rotation
        rotation_matrix = cv2.getRotationMatrix2D((cols/2, rows/2), 30, 1)
        rotated = cv2.warpAffine(gray_image, rotation_matrix, (cols, rows))
        
        # Perspective transformation
        pts1 = np.float32([[50, 50], [200, 50], [50, 200], [200, 200]])
        pts2 = np.float32([[10, 100], [200, 50], [100, 250], [300, 200]])
        perspective_matrix = cv2.getPerspectiveTransform(pts1, pts2)
        perspective = cv2.warpPerspective(gray_image, perspective_matrix, (cols, rows))
        
        # Feature extraction metrics
        # Calculate image statistics
        mean_intensity = np.mean(gray_image)
        std_intensity = np.std(gray_image)
        
        # Edge density
        edge_density = np.sum(edges_canny > 0) / (edges_canny.shape[0] * edges_canny.shape[1])
        
        # Texture analysis using LBP
        radius = 3
        n_points = 8 * radius
        lbp = local_binary_pattern(gray_image, n_points, radius, method='uniform')
        lbp_histogram = np.histogram(lbp, bins=n_points + 2)[0]
        
        return {
            'image_shape': test_image.shape,
            'mean_intensity': mean_intensity,
            'std_intensity': std_intensity,
            'edge_density': edge_density,
            'lbp_features': len(lbp_histogram),
            'preprocessing_operations': 12,
            'edge_detection_methods': 3,
            'morphological_operations': 5,
            'geometric_transformations': 3,
            'noise_reduction_methods': 3
        }
        
    except Exception as e:
        return {'error': str(e)}

def object_detection_recognition():
    """Object detection and recognition algorithms"""
    try:
        # Create test image with objects
        height, width = 400, 600
        test_image = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add various objects
        objects_added = 0
        
        # Rectangles (buildings/cars)
        for i in range(3):
            x, y = np.random.randint(50, width-100), np.random.randint(50, height-100)
            w, h = np.random.randint(40, 80), np.random.randint(30, 60)
            color = tuple(np.random.randint(100, 255, 3).tolist())
            cv2.rectangle(test_image, (x, y), (x+w, y+h), color, -1)
            objects_added += 1
        
        # Circles (balls/wheels)
        for i in range(2):
            center = (np.random.randint(50, width-50), np.random.randint(50, height-50))
            radius = np.random.randint(20, 40)
            color = tuple(np.random.randint(100, 255, 3).tolist())
            cv2.circle(test_image, center, radius, color, -1)
            objects_added += 1
        
        # Convert to grayscale for some detection algorithms
        gray_image = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
        
        # Template matching
        # Create simple templates
        template_size = 30
        square_template = np.ones((template_size, template_size), dtype=np.uint8) * 200
        circle_template = np.zeros((template_size, template_size), dtype=np.uint8)
        cv2.circle(circle_template, (template_size//2, template_size//2), template_size//3, 200, -1)
        
        # Match templates
        square_match = cv2.matchTemplate(gray_image, square_template, cv2.TM_CCOEFF_NORMED)
        circle_match = cv2.matchTemplate(gray_image, circle_template, cv2.TM_CCOEFF_NORMED)
        
        # Find matches above threshold
        threshold = 0.3
        square_locations = np.where(square_match >= threshold)
        circle_locations = np.where(circle_match >= threshold)
        
        square_matches = len(square_locations[0])
        circle_matches = len(circle_locations[0])
        
        # Contour detection
        # Apply threshold for contour detection
        _, binary = cv2.threshold(gray_image, 50, 255, cv2.THRESH_BINARY)
        contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Analyze contours
        contour_features = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Filter small contours
                perimeter = cv2.arcLength(contour, True)
                # Approximate contour to polygon
                epsilon = 0.02 * perimeter
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # Calculate shape features
                aspect_ratio = 0
                extent = 0
                solidity = 0
                
                if len(approx) >= 4:  # Quadrilateral or more complex
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = float(w) / h
                    rect_area = w * h
                    extent = float(area) / rect_area
                    
                    hull = cv2.convexHull(contour)
                    hull_area = cv2.contourArea(hull)
                    if hull_area > 0:
                        solidity = float(area) / hull_area
                
                contour_features.append({
                    'area': area,
                    'perimeter': perimeter,
                    'vertices': len(approx),
                    'aspect_ratio': aspect_ratio,
                    'extent': extent,
                    'solidity': solidity
                })
        
        # Hough transforms for shape detection
        # Hough line transform
        edges = cv2.Canny(gray_image, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        line_count = len(lines) if lines is not None else 0
        
        # Hough circle transform
        circles = cv2.HoughCircles(gray_image, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
                                  param1=50, param2=30, minRadius=10, maxRadius=100)
        circle_count = len(circles[0]) if circles is not None else 0
        
        # Corner detection
        # Harris corner detection
        corners_harris = cv2.cornerHarris(gray_image, 2, 3, 0.04)
        corners_harris = cv2.dilate(corners_harris, None)
        harris_corners = np.sum(corners_harris > 0.01 * corners_harris.max())
        
        # Shi-Tomasi corner detection
        corners_goodFeatures = cv2.goodFeaturesToTrack(gray_image, maxCorners=100, 
                                                      qualityLevel=0.01, minDistance=10)
        good_features_count = len(corners_goodFeatures) if corners_goodFeatures is not None else 0
        
        # SIFT feature detection
        try:
            sift = cv2.SIFT_create()
            keypoints_sift, descriptors_sift = sift.detectAndCompute(gray_image, None)
            sift_features = len(keypoints_sift)
        except:
            sift_features = 0
        
        # ORB feature detection
        orb = cv2.ORB_create()
        keypoints_orb, descriptors_orb = orb.detectAndCompute(gray_image, None)
        orb_features = len(keypoints_orb)
        
        # Connected component analysis
        num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, connectivity=8)
        
        # Filter components by size
        significant_components = 0
        for i in range(1, num_labels):  # Skip background
            area = stats[i, cv2.CC_STAT_AREA]
            if area > 100:
                significant_components += 1
        
        return {
            'objects_in_scene': objects_added,
            'template_square_matches': square_matches,
            'template_circle_matches': circle_matches,
            'contours_detected': len(contours),
            'significant_contours': len(contour_features),
            'hough_lines': line_count,
            'hough_circles': circle_count,
            'harris_corners': harris_corners,
            'good_features_corners': good_features_count,
            'sift_keypoints': sift_features,
            'orb_keypoints': orb_features,
            'connected_components': significant_components,
            'detection_algorithms': 8
        }
        
    except Exception as e:
        return {'error': str(e)}

def image_segmentation():
    """Advanced image segmentation techniques"""
    try:
        # Create complex test image for segmentation
        height, width = 300, 400
        test_image = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Create regions with different characteristics
        # Sky region (blue gradient)
        for y in range(100):
            intensity = int(150 + (y * 105) / 100)
            test_image[y, :, 2] = intensity  # Blue channel
        
        # Ground region (brown/green)
        test_image[200:, :, 0] = 50  # Blue
        test_image[200:, :, 1] = 100  # Green
        test_image[200:, :, 2] = 25   # Red
        
        # Objects in middle region
        cv2.rectangle(test_image, (50, 120), (150, 180), (255, 255, 255), -1)  # White building
        cv2.circle(test_image, (300, 140), 30, (255, 255, 0), -1)  # Yellow sun
        cv2.rectangle(test_image, (200, 160), (250, 190), (139, 69, 19), -1)  # Brown tree trunk
        
        # Add texture and noise
        noise = np.random.randint(-20, 20, test_image.shape, dtype=np.int16)
        test_image = np.clip(test_image.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        gray_image = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
        
        # Threshold-based segmentation
        # Otsu's thresholding
        threshold_otsu, binary_otsu = cv2.threshold(gray_image, 0, 255, 
                                                   cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Adaptive thresholding
        adaptive_thresh = cv2.adaptiveThreshold(gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                               cv2.THRESH_BINARY, 11, 2)
        
        # K-means clustering segmentation
        def kmeans_segmentation(image, k=4):
            data = image.reshape((-1, 3))
            data = np.float32(data)
            
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Convert back to uint8 and reshape
            centers = np.uint8(centers)
            segmented = centers[labels.flatten()]
            segmented = segmented.reshape(image.shape)
            
            return segmented, len(np.unique(labels))
        
        kmeans_result, num_clusters = kmeans_segmentation(test_image, k=5)
        
        # Region growing segmentation
        def region_growing(image, seed_point, threshold=10):
            h, w = image.shape
            segmented = np.zeros_like(image)
            visited = np.zeros((h, w), dtype=bool)
            
            # Stack for region growing
            stack = [seed_point]
            seed_value = image[seed_point]
            region_size = 0
            
            while stack:
                x, y = stack.pop()
                if visited[x, y]:
                    continue
                    
                if abs(int(image[x, y]) - int(seed_value)) <= threshold:
                    segmented[x, y] = 255
                    visited[x, y] = True
                    region_size += 1
                    
                    # Add 8-connected neighbors
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < h and 0 <= ny < w and not visited[nx, ny]:
                                stack.append((nx, ny))
            
            return segmented, region_size
        
        # Apply region growing from multiple seed points
        seed_points = [(50, 50), (150, 150), (250, 250)]
        region_results = []
        
        for seed in seed_points:
            if seed[0] < gray_image.shape[0] and seed[1] < gray_image.shape[1]:
                region, size = region_growing(gray_image, seed, threshold=15)
                region_results.append(size)
        
        # Watershed segmentation
        def watershed_segmentation(image):
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            
            # Noise removal
            kernel = np.ones((3, 3), np.uint8)
            opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
            
            # Sure background area
            sure_bg = cv2.dilate(opening, kernel, iterations=3)
            
            # Sure foreground area
            dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
            _, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
            
            # Unknown region
            sure_fg = np.uint8(sure_fg)
            unknown = cv2.subtract(sure_bg, sure_fg)
            
            # Marker labelling
            _, markers = cv2.connectedComponents(sure_fg)
            
            # Add 1 to all labels so that sure background is not 0, but 1
            markers = markers + 1
            
            # Mark the region of unknown with zero
            markers[unknown == 255] = 0
            
            # Apply watershed
            markers = cv2.watershed(image, markers)
            
            # Count regions
            unique_markers = len(np.unique(markers))
            
            return markers, unique_markers
        
        watershed_markers, watershed_regions = watershed_segmentation(test_image)
        
        # Edge-based segmentation using Canny edges
        edges = cv2.Canny(gray_image, 50, 150)
        
        # Find contours from edges
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Create segmentation mask from contours
        contour_mask = np.zeros_like(gray_image)
        cv2.drawContours(contour_mask, contours, -1, 255, thickness=cv2.FILLED)
        
        # Mean shift segmentation (simplified)
        def mean_shift_segmentation(image, spatial_radius=10, color_radius=20):
            # Convert to appropriate format
            data = cv2.pyrMeanShiftFiltering(image, spatial_radius, color_radius)
            
            # Convert to Lab color space for better segmentation
            lab_image = cv2.cvtColor(data, cv2.COLOR_BGR2LAB)
            
            # Apply K-means to segmented result
            segmented, clusters = kmeans_segmentation(lab_image, k=6)
            
            return segmented, clusters
        
        meanshift_result, meanshift_clusters = mean_shift_segmentation(test_image)
        
        # Calculate segmentation quality metrics
        def calculate_segmentation_metrics(original, segmented):
            # Convert to grayscale if needed
            if len(segmented.shape) == 3:
                segmented_gray = cv2.cvtColor(segmented, cv2.COLOR_BGR2GRAY)
            else:
                segmented_gray = segmented
                
            # Number of segments
            unique_values = len(np.unique(segmented_gray))
            
            # Average segment size
            total_pixels = segmented_gray.shape[0] * segmented_gray.shape[1]
            avg_segment_size = total_pixels / unique_values if unique_values > 0 else 0
            
            return unique_values, avg_segment_size
        
        otsu_segments, otsu_avg_size = calculate_segmentation_metrics(test_image, binary_otsu)
        kmeans_segments, kmeans_avg_size = calculate_segmentation_metrics(test_image, kmeans_result)
        
        return {
            'image_dimensions': (height, width),
            'otsu_threshold': threshold_otsu,
            'otsu_segments': otsu_segments,
            'kmeans_clusters': num_clusters,
            'region_growing_seeds': len(seed_points),
            'region_growing_sizes': region_results,
            'watershed_regions': watershed_regions,
            'contour_segments': len(contours),
            'meanshift_clusters': meanshift_clusters,
            'segmentation_methods': 7,
            'avg_kmeans_segment_size': kmeans_avg_size,
            'total_edge_pixels': np.sum(edges > 0)
        }
        
    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    print("Computer vision and image recognition...")
    
    # Image preprocessing
    preprocess_result = image_preprocessing()
    if 'error' not in preprocess_result:
        print(f"Preprocessing: {preprocess_result['preprocessing_operations']} ops, edge density: {preprocess_result['edge_density']:.4f}")
    
    # Object detection
    detection_result = object_detection_recognition()
    if 'error' not in detection_result:
        print(f"Detection: {detection_result['objects_in_scene']} objects, {detection_result['sift_keypoints']} SIFT features")
    
    # Image segmentation
    segmentation_result = image_segmentation()
    if 'error' not in segmentation_result:
        print(f"Segmentation: {segmentation_result['segmentation_methods']} methods, {segmentation_result['watershed_regions']} watershed regions")