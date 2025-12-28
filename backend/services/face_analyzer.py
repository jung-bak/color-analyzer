"""
Face analysis using MediaPipe Face Mesh for landmark detection and skin tone extraction.
"""
import cv2
import numpy as np
from datetime import datetime
from typing import Tuple, Optional, Dict, Any, List

from backend.core.config import settings
from backend.core.palettes import (
    CHEEK_LANDMARKS,
    FOREHEAD_LANDMARKS,
    NOSE_BRIDGE_LANDMARKS,
    CHIN_LANDMARKS,
    LEFT_EYEBROW_LANDMARKS,
    RIGHT_EYEBROW_LANDMARKS,
)
from backend.services.color_processor import color_processor
from backend.services.visualization import visualization_service

# MediaPipe import - lazy load
_face_mesh = None


def get_face_mesh():
    """Get or create MediaPipe Face Mesh instance."""
    global _face_mesh
    if _face_mesh is None:
        import mediapipe as mp
        _face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=settings.FACE_MESH_MAX_FACES,
            refine_landmarks=settings.FACE_MESH_REFINE_LANDMARKS,
            min_detection_confidence=settings.FACE_MESH_MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=settings.FACE_MESH_MIN_TRACKING_CONFIDENCE,
        )
    return _face_mesh


class FaceAnalyzer:
    """Handles face detection and skin tone extraction."""
    
    def __init__(self):
        """Initialize face analyzer (face mesh loaded on demand)."""
        pass
    
    def analyze_image(
        self,
        image: np.ndarray,
        apply_white_balance: bool = True,
        debug: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze image to extract skin tone and facial features.
        
        Args:
            image: Input image in RGB format (numpy array)
            apply_white_balance: Whether to apply white balance correction
            debug: Whether to generate debug visualizations
        
        Returns:
            Dictionary containing analysis results or error information
        """
        # Initialize debug data collection
        debug_images = []
        debug_metadata = {
            "face_detection": {},
            "skin_extraction": {},
            "white_balance": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Debug: Store original image
        if debug:
            debug_images.append({
                "step": "original",
                "title": "Original Image",
                "description": "Uploaded image before any processing",
                "image_base64": visualization_service.encode_image_base64(image),
                "metadata": {"dimensions": f"{image.shape[1]}x{image.shape[0]}"}
            })
        
        # Check image quality
        quality_ok, warning = color_processor.check_image_quality(image)
        if not quality_ok:
            return {
                "success": False,
                "error": warning,
            }
        
        # Detect face landmarks
        face_mesh = get_face_mesh()
        results = face_mesh.process(image)
        
        if not results.multi_face_landmarks:
            return {
                "success": False,
                "error": "No face detected. Please ensure your face is clearly visible and well-lit.",
            }
        
        # Check for multiple faces
        if len(results.multi_face_landmarks) > 1:
            return {
                "success": False,
                "error": "Multiple faces detected. Please use a photo with only one person.",
            }
        
        face_landmarks = results.multi_face_landmarks[0]
        
        # Debug: Draw face landmarks
        if debug:
            landmarks_image = visualization_service.draw_face_landmarks(image, face_landmarks)
            debug_images.append({
                "step": "face_mesh",
                "title": "Face Mesh Detection",
                "description": f"468 facial landmarks detected. Green dots highlight cheek region ({len(CHEEK_LANDMARKS)} landmarks).",
                "image_base64": visualization_service.encode_image_base64(landmarks_image),
                "metadata": {
                    "total_landmarks": len(face_landmarks.landmark),
                    "cheek_landmarks": CHEEK_LANDMARKS
                }
            })
            debug_metadata["face_detection"] = {
                "landmarks_detected": len(face_landmarks.landmark),
                "cheek_landmark_count": len(CHEEK_LANDMARKS)
            }
        
        # Apply white balance if requested
        processed_image = image.copy()
        wb_method = "none"
        wb_metadata = {}
        wb_debug_data = None
        
        if apply_white_balance:
            if debug:
                processed_image, wb_method, wb_metadata, wb_debug_data = color_processor.apply_white_balance(
                    image, face_landmarks, debug=True
                )
            else:
                processed_image, wb_method, wb_metadata = color_processor.apply_white_balance(
                    image, face_landmarks, debug=False
                )
        
        # Debug: White balance comparison
        if debug and apply_white_balance:
            comparison_image = visualization_service.create_comparison_image(
                image, processed_image, "Before WB", "After WB"
            )
            debug_images.append({
                "step": "white_balance",
                "title": "White Balance Correction",
                "description": f"Method: {wb_method}. Side-by-side comparison showing color correction effect.",
                "image_base64": visualization_service.encode_image_base64(comparison_image),
                "metadata": wb_metadata
            })
            debug_metadata["white_balance"] = {
                "method": wb_method,
                **wb_metadata
            }
            
            # Add WB-specific debug images if available
            if wb_debug_data:
                debug_images.extend(wb_debug_data)
        
        # Extract skin tone from cheek region (before WB for comparison)
        skin_tone_result_before = None
        if debug:
            skin_tone_result_before = self._extract_skin_tone(image, face_landmarks, debug=False)
        
        # Extract skin tone from cheek region (after WB)
        skin_tone_result = self._extract_skin_tone(processed_image, face_landmarks, debug=debug)
        
        if not skin_tone_result["success"]:
            return skin_tone_result
        
        # Debug: Visualize skin mask
        if debug:
            h, w = processed_image.shape[:2]
            cheek_mask = np.zeros((h, w), dtype=np.uint8)
            points = []
            for idx in CHEEK_LANDMARKS:
                if idx < len(face_landmarks.landmark):
                    landmark = face_landmarks.landmark[idx]
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    points.append((x, y))
            
            if len(points) >= 3:
                points_array = np.array(points, dtype=np.int32)
                hull = cv2.convexHull(points_array)
                cv2.fillConvexPoly(cheek_mask, hull, 255)
                
                # Create visualization with mask overlay
                mask_viz = visualization_service.visualize_mask(processed_image, cheek_mask, color=(0, 255, 0), alpha=0.4)
                
                # Calculate statistics
                cheek_pixels = processed_image[cheek_mask == 255]
                pixel_count = len(cheek_pixels)
                coverage_pct = (pixel_count / (h * w)) * 100
                
                avg_rgb_before = tuple(int(c) for c in skin_tone_result_before["rgb_color"]) if skin_tone_result_before and skin_tone_result_before["success"] else None
                avg_rgb_after = skin_tone_result["rgb_color"]
                
                debug_images.append({
                    "step": "cheek_mask",
                    "title": "Skin Extraction Mask",
                    "description": f"Green overlay shows the {pixel_count:,} pixels ({coverage_pct:.2f}% of image) used for color analysis.",
                    "image_base64": visualization_service.encode_image_base64(mask_viz),
                    "metadata": {
                        "landmark_indices": CHEEK_LANDMARKS,
                        "pixel_count": pixel_count,
                        "coverage_percentage": round(coverage_pct, 2),
                        "avg_rgb_before_wb": avg_rgb_before,
                        "avg_rgb_after_wb": avg_rgb_after
                    }
                })
                debug_metadata["skin_extraction"] = {
                    "cheek_landmarks": CHEEK_LANDMARKS,
                    "pixel_count": pixel_count,
                    "coverage_percentage": round(coverage_pct, 2),
                    "avg_rgb_before_wb": avg_rgb_before,
                    "avg_rgb_after_wb": avg_rgb_after
                }
        
        # Convert skin tone to LAB color space
        rgb_color = skin_tone_result["rgb_color"]
        lab_values = color_processor.rgb_to_lab(rgb_color)
        
        # QUICK WIN #1: Multi-region sampling for confidence
        multi_region_result = self._extract_multi_region_skin_tone(processed_image, face_landmarks)
        
        # QUICK WIN #2: Sample variance confidence
        variance_confidence = self._calculate_sample_variance_confidence(
            processed_image, face_landmarks
        )
        
        # QUICK WIN #3: Contrast level analysis
        contrast_result = self._analyze_contrast_level(processed_image, face_landmarks)
        
        # Add debug visualizations for quick wins
        if debug:
            # Debug: Multi-region sampling visualization
            if multi_region_result.get("region_colors"):
                multi_region_viz = visualization_service.visualize_multi_regions(
                    processed_image, face_landmarks, multi_region_result
                )
                if multi_region_viz is not None:
                    debug_images.append({
                        "step": "multi_region",
                        "title": "Multi-Region Sampling",
                        "description": f"Sampled {multi_region_result['regions_sampled']} regions. Agreement: {multi_region_result['agreement_score']*100:.1f}%. Status: {multi_region_result['status']}",
                        "image_base64": visualization_service.encode_image_base64(multi_region_viz),
                        "metadata": multi_region_result
                    })
            
            # Debug: Variance visualization (show the sample region with variance info)
            if variance_confidence.get("status") != "failed":
                debug_images.append({
                    "step": "variance_analysis",
                    "title": "Sample Quality Analysis",
                    "description": f"Pixel variance: {variance_confidence['variance']:.1f}. Quality: {variance_confidence['status']}. Confidence: {variance_confidence['confidence_factor']:+.1f}%",
                    "image_base64": visualization_service.encode_image_base64(processed_image),  # Could add viz overlay
                    "metadata": variance_confidence
                })
            
            # Debug: Contrast visualization
            if contrast_result.get("status") == "success":
                contrast_viz = visualization_service.visualize_contrast(processed_image, face_landmarks, contrast_result)
                if contrast_viz is not None:
                    debug_images.append({
                        "step": "contrast_analysis",
                        "title": "Contrast Level Analysis",
                        "description": f"Contrast: {contrast_result['contrast_level']:.1f} ({contrast_result['level_category']}). Expected: {', '.join(contrast_result['expected_seasons'])}",
                        "image_base64": visualization_service.encode_image_base64(contrast_viz),
                        "metadata": contrast_result
                    })
        
        result = {
            "success": True,
            "rgb_color": rgb_color,
            "lab_values": lab_values,
            "white_balance_applied": apply_white_balance,
            "white_balance_method": wb_method,
            "white_balance_metadata": wb_metadata,
            "face_landmarks": face_landmarks,
            # New confidence factors
            "multi_region_analysis": multi_region_result,
            "variance_confidence": variance_confidence,
            "contrast_analysis": contrast_result,
        }
        
        # Add debug data if enabled
        if debug:
            result["debug_images"] = debug_images
            result["debug_metadata"] = debug_metadata
        
        return result
    
    def _extract_skin_tone(
        self,
        image: np.ndarray,
        face_landmarks: Any,
        debug: bool = False
    ) -> Dict[str, Any]:
        """
        Extract average skin tone from the cheek region.
        
        Args:
            image: Input image in RGB format
            face_landmarks: MediaPipe face landmarks
            debug: Whether to include debug information
        
        Returns:
            Dictionary with extraction results
        """
        h, w = image.shape[:2]
        
        # Create mask for cheek region
        cheek_mask = np.zeros((h, w), dtype=np.uint8)
        
        # Extract cheek landmark points
        points = []
        for idx in CHEEK_LANDMARKS:
            if idx < len(face_landmarks.landmark):
                landmark = face_landmarks.landmark[idx]
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                points.append((x, y))
        
        if len(points) < 3:
            return {
                "success": False,
                "error": "Could not extract cheek region. Please try a clearer photo.",
            }
        
        # Create convex polygon for cheek region
        points_array = np.array(points, dtype=np.int32)
        hull = cv2.convexHull(points_array)
        cv2.fillConvexPoly(cheek_mask, hull, 255)
        
        # Extract pixels within the cheek region
        cheek_pixels = image[cheek_mask == 255]
        
        if len(cheek_pixels) == 0:
            return {
                "success": False,
                "error": "Could not extract skin tone. Please ensure face is clearly visible.",
            }
        
        # Calculate average color
        mean_color = np.mean(cheek_pixels, axis=0)
        rgb_color = tuple(int(c) for c in mean_color)
        
        return {
            "success": True,
            "rgb_color": rgb_color,
        }
    
    def _extract_region_color(
        self,
        image: np.ndarray,
        face_landmarks: Any,
        landmark_indices: List[int],
        region_name: str = "region"
    ) -> Optional[Tuple[int, int, int]]:
        """
        Extract average color from a specific facial region.
        
        Args:
            image: Input image in RGB format
            face_landmarks: MediaPipe face landmarks
            landmark_indices: List of landmark indices for the region
            region_name: Name of the region (for error messages)
        
        Returns:
            RGB tuple or None if extraction failed
        """
        h, w = image.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        
        # Extract landmark points
        points = []
        for idx in landmark_indices:
            if idx < len(face_landmarks.landmark):
                landmark = face_landmarks.landmark[idx]
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                points.append((x, y))
        
        if len(points) < 3:
            return None
        
        # Create convex polygon
        points_array = np.array(points, dtype=np.int32)
        hull = cv2.convexHull(points_array)
        cv2.fillConvexPoly(mask, hull, 255)
        
        # Extract pixels
        pixels = image[mask == 255]
        
        if len(pixels) == 0:
            return None
        
        # Calculate average color
        mean_color = np.mean(pixels, axis=0)
        return tuple(int(c) for c in mean_color)
    
    def _extract_multi_region_skin_tone(
        self,
        image: np.ndarray,
        face_landmarks: Any
    ) -> Dict[str, Any]:
        """
        QUICK WIN #1: Extract skin tone from multiple facial regions for robustness.
        
        Compares cheek, forehead, nose bridge, and chin to detect:
        - Uneven lighting (high variance between regions)
        - Makeup/shadows (regions disagree significantly)
        
        Returns:
            Dictionary with region colors, agreement score, and confidence
        """
        regions = {
            "cheeks": CHEEK_LANDMARKS,
            "forehead": FOREHEAD_LANDMARKS,
            "nose_bridge": NOSE_BRIDGE_LANDMARKS,
            "chin": CHIN_LANDMARKS,
        }
        
        region_colors = {}
        region_lab_values = {}
        
        for region_name, landmarks in regions.items():
            rgb = self._extract_region_color(image, face_landmarks, landmarks, region_name)
            if rgb is not None:
                region_colors[region_name] = rgb
                region_lab_values[region_name] = color_processor.rgb_to_lab(rgb)
        
        # Calculate agreement (how similar are the regions?)
        if len(region_lab_values) < 2:
            return {
                "regions_sampled": len(region_colors),
                "agreement_score": 0.0,
                "confidence_boost": 0.0,
                "status": "insufficient_regions",
            }
        
        # Calculate variance of L* values across regions (should be similar)
        L_values = [lab["L"] for lab in region_lab_values.values()]
        L_variance = np.std(L_values)
        
        # Calculate variance of warmth indicators across regions
        warmth_indicators = []
        for lab in region_lab_values.values():
            a_norm = lab["a"] - 128
            b_norm = lab["b"] - 128
            warmth_indicators.append(b_norm - a_norm)
        warmth_variance = np.std(warmth_indicators)
        
        # Agreement score: lower variance = higher agreement
        # Good agreement: L_variance < 10, warmth_variance < 5
        L_agreement = 1.0 - min(L_variance / 20.0, 1.0)
        warmth_agreement = 1.0 - min(warmth_variance / 10.0, 1.0)
        agreement_score = (L_agreement + warmth_agreement) / 2.0
        
        # Confidence boost: high agreement = more confident
        confidence_boost = agreement_score * 10.0  # Up to +10% confidence
        
        return {
            "regions_sampled": len(region_colors),
            "region_colors": region_colors,
            "L_variance": float(L_variance),
            "warmth_variance": float(warmth_variance),
            "agreement_score": float(agreement_score),
            "confidence_boost": float(confidence_boost),
            "status": "good" if agreement_score > 0.7 else ("moderate" if agreement_score > 0.5 else "poor"),
        }
    
    def _calculate_sample_variance_confidence(
        self,
        image: np.ndarray,
        face_landmarks: Any
    ) -> Dict[str, Any]:
        """
        QUICK WIN #2: Calculate confidence based on pixel variance within sampled region.
        
        High variance indicates:
        - Shadows or uneven lighting
        - Makeup not blended well
        - Mixed skin tones in sample
        
        Returns:
            Dictionary with variance metrics and confidence factor
        """
        h, w = image.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        
        # Sample cheek region
        points = []
        for idx in CHEEK_LANDMARKS:
            if idx < len(face_landmarks.landmark):
                landmark = face_landmarks.landmark[idx]
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                points.append((x, y))
        
        if len(points) < 3:
            return {"variance": None, "confidence_factor": 0.0, "status": "failed"}
        
        points_array = np.array(points, dtype=np.int32)
        hull = cv2.convexHull(points_array)
        cv2.fillConvexPoly(mask, hull, 255)
        
        pixels = image[mask == 255]
        
        if len(pixels) == 0:
            return {"variance": None, "confidence_factor": 0.0, "status": "failed"}
        
        # Calculate per-channel standard deviation
        std_dev = np.std(pixels, axis=0)
        avg_variance = float(np.mean(std_dev))
        
        # Good samples: variance < 15
        # Acceptable: 15-25
        # Poor: > 25
        if avg_variance < 15:
            confidence_factor = 5.0  # +5% confidence
            status = "excellent"
        elif avg_variance < 25:
            confidence_factor = 2.0  # +2% confidence
            status = "good"
        elif avg_variance < 35:
            confidence_factor = 0.0  # No bonus
            status = "acceptable"
        else:
            confidence_factor = -5.0  # -5% confidence (high variance!)
            status = "poor"
        
        return {
            "variance": avg_variance,
            "confidence_factor": confidence_factor,
            "status": status,
        }
    
    def _analyze_contrast_level(
        self,
        image: np.ndarray,
        face_landmarks: Any
    ) -> Dict[str, Any]:
        """
        QUICK WIN #3: Analyze contrast between eyebrows and skin.
        
        Contrast level helps validate season classification:
        - Winter: HIGH contrast (>35 L* difference)
        - Summer: LOW contrast (<20 L* difference)
        - Autumn/Spring: MEDIUM contrast (20-35 L* difference)
        
        Returns:
            Dictionary with contrast metrics and expected season correlation
        """
        # Extract eyebrow color (average of left and right)
        left_eyebrow_rgb = self._extract_region_color(
            image, face_landmarks, LEFT_EYEBROW_LANDMARKS, "left_eyebrow"
        )
        right_eyebrow_rgb = self._extract_region_color(
            image, face_landmarks, RIGHT_EYEBROW_LANDMARKS, "right_eyebrow"
        )
        
        if left_eyebrow_rgb is None and right_eyebrow_rgb is None:
            return {
                "contrast_level": None,
                "confidence_adjustment": 0.0,
                "status": "failed",
            }
        
        # Average eyebrow colors
        eyebrow_colors = [c for c in [left_eyebrow_rgb, right_eyebrow_rgb] if c is not None]
        avg_eyebrow_rgb = tuple(int(np.mean([c[i] for c in eyebrow_colors])) for i in range(3))
        
        # Get skin color from cheeks
        skin_rgb = self._extract_region_color(image, face_landmarks, CHEEK_LANDMARKS, "cheeks")
        
        if skin_rgb is None:
            return {
                "contrast_level": None,
                "confidence_adjustment": 0.0,
                "status": "failed",
            }
        
        # Convert to LAB
        eyebrow_lab = color_processor.rgb_to_lab(avg_eyebrow_rgb)
        skin_lab = color_processor.rgb_to_lab(skin_rgb)
        
        # Calculate contrast (difference in L* values)
        contrast = abs(eyebrow_lab["L"] - skin_lab["L"])
        
        # Categorize contrast level
        if contrast > 35:
            level = "high"
            expected_seasons = ["Winter", "Spring"]
        elif contrast < 20:
            level = "low"
            expected_seasons = ["Summer", "Autumn"]
        else:
            level = "medium"
            expected_seasons = ["All"]  # Medium contrast can be any season
        
        return {
            "contrast_level": float(contrast),
            "level_category": level,
            "expected_seasons": expected_seasons,
            "eyebrow_L": float(eyebrow_lab["L"]),
            "skin_L": float(skin_lab["L"]),
            "confidence_adjustment": 0.0,  # Will be calculated in classifier based on agreement
            "status": "success",
        }
    
    def detect_face_count(self, image: np.ndarray) -> int:
        """
        Detect the number of faces in an image.
        
        Args:
            image: Input image in RGB format
        
        Returns:
            Number of faces detected
        """
        face_mesh = get_face_mesh()
        results = face_mesh.process(image)
        
        if not results.multi_face_landmarks:
            return 0
        
        return len(results.multi_face_landmarks)

    def __del__(self):
        """Cleanup resources."""
        global _face_mesh
        if _face_mesh is not None:
            try:
                _face_mesh.close()
            except:
                pass


# Create a singleton instance
face_analyzer = FaceAnalyzer()

