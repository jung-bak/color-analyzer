"""
Color processing utilities including white balance correction and color space conversion.
"""
import cv2
import numpy as np
import base64
from typing import Tuple, Optional, Dict, Any, List

from backend.core.config import settings
from backend.core.palettes import SKIN_LANDMARKS

# MediaPipe import - lazy load to avoid initialization errors
_segmenter = None


def get_segmenter():
    """Get or create MediaPipe Selfie Segmentation instance."""
    global _segmenter
    if _segmenter is None:
        import mediapipe as mp
        _segmenter = mp.solutions.selfie_segmentation.SelfieSegmentation(
            model_selection=settings.SELFIE_SEGMENTATION_MODEL
        )
    return _segmenter


class ColorProcessor:
    """Handles color processing and white balance correction."""
    
    def __init__(self):
        """Initialize color processor (segmenter loaded on demand)."""
        pass
    
    def _encode_image_base64(self, image: np.ndarray, max_width: int = 1024) -> str:
        """
        Encode image as base64 JPEG string.
        
        Args:
            image: Input image in RGB format
            max_width: Maximum width for resizing
        
        Returns:
            Base64-encoded JPEG string with data URI prefix
        """
        # Resize if too large
        h, w = image.shape[:2]
        if w > max_width:
            scale = max_width / w
            new_w = max_width
            new_h = int(h * scale)
            image = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        # Convert RGB to BGR for OpenCV
        image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        # Encode as JPEG
        success, buffer = cv2.imencode('.jpg', image_bgr, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not success:
            return ""
        
        # Convert to base64
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/jpeg;base64,{jpg_as_text}"
    
    def apply_white_balance(
        self,
        image: np.ndarray,
        face_landmarks: Optional[Any] = None,
        debug: bool = False
    ):
        """
        Apply intelligent white balance correction with automatic fallback.
        
        Args:
            image: Input image in RGB format
            face_landmarks: MediaPipe face landmarks (optional, for Skin Locus method)
            debug: Whether to return debug visualizations
        
        Returns:
            If debug=False: Tuple of (corrected_image, method_used, metadata)
            If debug=True: Tuple of (corrected_image, method_used, metadata, debug_images)
        """
        debug_images = []
        
        # Try background-based method first
        bg_result = self._try_background_white_balance(image, debug=debug)
        
        if bg_result is not None:
            if debug:
                corrected, metadata, bg_debug_images = bg_result
                debug_images.extend(bg_debug_images)
            else:
                corrected, metadata = bg_result
            
            if debug:
                return corrected, "background", metadata, debug_images
            return corrected, "background", metadata
        
        # Fall back to Skin Locus method
        if face_landmarks is not None:
            skin_result = self._apply_skin_locus_white_balance(image, face_landmarks, debug=debug)
            if skin_result is not None:
                if debug:
                    corrected, metadata, skin_debug_images = skin_result
                    debug_images.extend(skin_debug_images)
                else:
                    corrected, metadata = skin_result
                
                if debug:
                    return corrected, "skin_locus", metadata, debug_images
                return corrected, "skin_locus", metadata
        
        # If both methods fail, return original image
        if debug:
            return image, "none", {"reason": "No suitable white balance method available"}, []
        return image, "none", {"reason": "No suitable white balance method available"}
    
    def _try_background_white_balance(
        self,
        image: np.ndarray,
        debug: bool = False
    ):
        """
        Attempt background-based white balance correction.
        
        Args:
            image: Input image in RGB format
            debug: Whether to return debug images
        
        Returns:
            If debug=False: Tuple of (corrected_image, metadata) or None if unsuitable
            If debug=True: Tuple of (corrected_image, metadata, debug_images) or None if unsuitable
        """
        # Segment person from background
        segmenter = get_segmenter()
        results = segmenter.process(image)
        
        if results.segmentation_mask is None:
            return None
        
        # Create background mask (inverted segmentation mask)
        background_mask = (results.segmentation_mask < 0.1).astype(np.uint8)
        
        # Calculate background percentage
        bg_percentage = np.sum(background_mask) / background_mask.size
        
        # Check if background is sufficient
        if bg_percentage < settings.WB_MIN_BACKGROUND_PERCENTAGE:
            return None
        
        # Extract background pixels
        bg_pixels = image[background_mask == 1]
        
        if len(bg_pixels) == 0:
            return None
        
        # Calculate background color variance
        bg_variance = np.std(bg_pixels, axis=0).mean()
        
        # Check if background is neutral enough
        if bg_variance > settings.WB_MAX_BACKGROUND_VARIANCE:
            return None
        
        # Calculate average RGB of background
        avg_rgb = np.mean(bg_pixels, axis=0)
        
        # Avoid division by zero
        if np.any(avg_rgb < 1):
            return None
        
        # Calculate white balance gains
        # Use the average of the background RGB as the target to preserve brightness
        # This corrects color cast while maintaining the original luminance
        avg_gray = np.mean(avg_rgb)
        gains = avg_gray / avg_rgb
        
        # Clip gains to reasonable range to avoid extreme corrections
        gains = np.clip(gains, 0.5, 2.0)
        
        # Apply gains to entire image
        corrected = image.astype(np.float32) * gains
        corrected = np.clip(corrected, 0, 255).astype(np.uint8)
        
        metadata = {
            "background_percentage": float(bg_percentage * 100),
            "background_variance": float(bg_variance),
            "average_background_rgb": avg_rgb.tolist(),
            "average_background_gray": float(avg_gray),
            "gains": gains.tolist(),
            "gains_applied": "Clipped to [0.5, 2.0] range to prevent extreme corrections",
        }
        
        # Generate debug images if requested
        if debug:
            debug_images = []
            
            # Visualize background mask
            mask_viz = np.zeros_like(image)
            mask_viz[background_mask == 1] = [0, 255, 0]  # Green for background
            mask_viz[background_mask == 0] = [255, 0, 0]  # Red for person
            
            # Blend mask with original image
            blended = cv2.addWeighted(image, 0.6, mask_viz, 0.4, 0)
            
            debug_images.append({
                "step": "background_mask",
                "title": "Background Segmentation",
                "description": f"Green: Background pixels ({bg_percentage*100:.1f}% of image). Avg RGB: [{avg_rgb[0]:.1f}, {avg_rgb[1]:.1f}, {avg_rgb[2]:.1f}]. Gains: [{gains[0]:.3f}, {gains[1]:.3f}, {gains[2]:.3f}]",
                "image_base64": self._encode_image_base64(blended),
                "metadata": metadata
            })
            
            return corrected, metadata, debug_images
        
        return corrected, metadata
    
    def _apply_skin_locus_white_balance(
        self,
        image: np.ndarray,
        face_landmarks: Any,
        debug: bool = False
    ):
        """
        Apply Skin Locus-based white balance correction.
        
        Uses the fact that human skin tones cluster in a specific area
        of the chromaticity diagram regardless of ethnicity.
        
        Args:
            image: Input image in RGB format
            face_landmarks: MediaPipe face landmarks
        
        Returns:
            Tuple of (corrected_image, metadata) or None if failed
        """
        h, w = image.shape[:2]
        
        # Create skin mask from face landmarks
        skin_mask = self._create_skin_mask(image, face_landmarks, SKIN_LANDMARKS)
        
        # Extract skin pixels
        skin_pixels = image[skin_mask == 1]
        
        if len(skin_pixels) < 100:  # Need sufficient skin pixels
            return None
        
        # Calculate average skin color
        avg_skin_rgb = np.mean(skin_pixels, axis=0)
        
        # Convert to chromaticity coordinates
        sum_rgb = np.sum(avg_skin_rgb)
        if sum_rgb < 1:
            return None
        
        r_chrom = avg_skin_rgb[0] / sum_rgb
        g_chrom = avg_skin_rgb[1] / sum_rgb
        
        # Skin Locus projection
        # Empirical skin locus line: g ≈ -1.73*r + 1.06
        expected_g = settings.SKIN_LOCUS_SLOPE * r_chrom + settings.SKIN_LOCUS_INTERCEPT
        g_offset = expected_g - g_chrom
        
        # Calculate color temperature correction
        # Positive g_offset means skin is too red/warm, need cooling
        # Negative g_offset means skin is too blue/cool, need warming
        correction_factor = 1.0 + (g_offset * settings.SKIN_LOCUS_CORRECTION_STRENGTH)
        
        # Clip correction factor to prevent extreme shifts
        correction_factor = np.clip(correction_factor, 0.5, 2.0)
        
        # Create temperature shift array [R_scale, G_scale, B_scale]
        # If need cooling (g_offset > 0): reduce red, increase blue
        # If need warming (g_offset < 0): increase red, reduce blue
        temp_shift = np.array([
            1.0 / correction_factor,  # Red
            1.0,                       # Green (unchanged)
            correction_factor          # Blue
        ])
        
        # Apply correction to entire image
        corrected = image.astype(np.float32) * temp_shift
        corrected = np.clip(corrected, 0, 255).astype(np.uint8)
        
        metadata = {
            "average_skin_rgb": avg_skin_rgb.tolist(),
            "r_chromaticity": float(r_chrom),
            "g_chromaticity": float(g_chrom),
            "expected_g": float(expected_g),
            "g_offset": float(g_offset),
            "correction_factor": float(correction_factor),
            "temperature_shift": temp_shift.tolist(),
            "skin_pixel_count": len(skin_pixels),
        }
        
        # Generate debug images if requested
        if debug:
            debug_images = []
            
            # Visualize skin mask
            mask_viz = np.zeros_like(image)
            mask_viz[skin_mask == 1] = [255, 200, 150]  # Skin-tone color
            mask_viz[skin_mask == 0] = [100, 100, 100]  # Gray for non-skin
            
            # Blend mask with original image
            blended = cv2.addWeighted(image, 0.6, mask_viz, 0.4, 0)
            
            debug_images.append({
                "step": "skin_locus_mask",
                "title": "Skin Locus Mask",
                "description": f"Skin-colored overlay shows {len(skin_pixels):,} pixels used for Skin Locus white balance calculation.",
                "image_base64": self._encode_image_base64(blended),
                "metadata": metadata
            })
            
            return corrected, metadata, debug_images
        
        return corrected, metadata
    
    def _create_skin_mask(
        self,
        image: np.ndarray,
        face_landmarks: Any,
        skin_indices: list
    ) -> np.ndarray:
        """
        Create a mask for skin regions based on face landmarks.
        
        Args:
            image: Input image
            face_landmarks: MediaPipe face landmarks
            skin_indices: List of landmark indices to include
        
        Returns:
            Binary mask (1 = skin, 0 = not skin)
        """
        h, w = image.shape[:2]
        mask = np.zeros((h, w), dtype=np.uint8)
        
        # Extract landmark points
        points = []
        for idx in skin_indices:
            if idx < len(face_landmarks.landmark):
                landmark = face_landmarks.landmark[idx]
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                points.append((x, y))
        
        if len(points) < 3:
            return mask
        
        # Create convex hull for skin region
        points_array = np.array(points, dtype=np.int32)
        hull = cv2.convexHull(points_array)
        cv2.fillConvexPoly(mask, hull, 1)
        
        return mask
    
    def rgb_to_lab(self, rgb_color: Tuple[float, float, float]) -> Dict[str, float]:
        """
        Convert RGB color to CIELAB color space.
        
        Args:
            rgb_color: Tuple of (R, G, B) values (0-255)
        
        Returns:
            Dictionary with 'L', 'a', 'b' values
        """
        # Create a 1x1 pixel image
        rgb_pixel = np.uint8([[rgb_color]])
        
        # Convert to LAB
        lab_pixel = cv2.cvtColor(rgb_pixel, cv2.COLOR_RGB2LAB)[0][0]
        
        return {
            'L': float(lab_pixel[0]),
            'a': float(lab_pixel[1]),
            'b': float(lab_pixel[2]),
        }
    
    def check_image_quality(self, image: np.ndarray) -> Tuple[bool, Optional[str]]:
        """
        Check if image quality is suitable for analysis.
        
        Args:
            image: Input image in RGB format
        
        Returns:
            Tuple of (is_good, warning_message)
        """
        # Calculate average pixel intensity
        avg_intensity = np.mean(image)
        
        if avg_intensity < settings.MIN_PIXEL_INTENSITY:
            return False, "Photo is too dark. Please use better lighting."
        
        if avg_intensity > settings.MAX_PIXEL_INTENSITY:
            return False, "Photo is too bright. Please avoid overexposure."
        
        return True, None
    
    def __del__(self):
        """Cleanup resources."""
        global _segmenter
        if _segmenter is not None:
            try:
                _segmenter.close()
            except:
                pass


# Create a singleton instance
color_processor = ColorProcessor()

