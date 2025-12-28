"""
Visualization service for debug image generation.
Handles all image annotation, overlay, and comparison functionality.
"""
import cv2
import numpy as np
import base64
from typing import Tuple, Optional, Dict, Any

from backend.core.palettes import (
    CHEEK_LANDMARKS,
    FOREHEAD_LANDMARKS,
    NOSE_BRIDGE_LANDMARKS,
    CHIN_LANDMARKS,
    LEFT_EYEBROW_LANDMARKS,
    RIGHT_EYEBROW_LANDMARKS,
)


class VisualizationService:
    """Handles debug visualization and image annotation."""

    def encode_image_base64(self, image: np.ndarray, max_width: int = 1024) -> str:
        """
        Encode image as base64 JPEG string.

        Args:
            image: Input image in RGB format
            max_width: Maximum width for resizing (to keep response size manageable)

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

    def draw_face_landmarks(self, image: np.ndarray, face_landmarks: Any) -> np.ndarray:
        """
        Draw all face mesh landmarks on image.

        Args:
            image: Input image in RGB format
            face_landmarks: MediaPipe face landmarks

        Returns:
            Image with landmarks drawn
        """
        # Create a copy to draw on
        annotated_image = image.copy()
        h, w = image.shape[:2]

        # Draw all landmarks
        for idx, landmark in enumerate(face_landmarks.landmark):
            x = int(landmark.x * w)
            y = int(landmark.y * h)

            # Draw landmark point
            color = (0, 255, 0) if idx in CHEEK_LANDMARKS else (100, 100, 255)
            cv2.circle(annotated_image, (x, y), 2, color, -1)

            # Optionally label cheek landmarks
            if idx in CHEEK_LANDMARKS:
                cv2.putText(annotated_image, str(idx), (x + 3, y - 3),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 255, 0), 1)

        return annotated_image

    def visualize_mask(
        self,
        image: np.ndarray,
        mask: np.ndarray,
        color: Tuple[int, int, int] = (0, 255, 0),
        alpha: float = 0.5
    ) -> np.ndarray:
        """
        Create colored overlay showing masked regions.

        Args:
            image: Input image in RGB format
            mask: Binary mask (255 = masked region, 0 = background)
            color: RGB color for overlay
            alpha: Transparency (0-1)

        Returns:
            Image with colored overlay
        """
        overlay = image.copy()

        # Create colored mask
        colored_mask = np.zeros_like(image)
        colored_mask[mask == 255] = color

        # Blend with original image
        result = cv2.addWeighted(overlay, 1 - alpha, colored_mask, alpha, 0)

        # Draw outline
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(result, contours, -1, color, 2)

        return result

    def create_comparison_image(
        self,
        image1: np.ndarray,
        image2: np.ndarray,
        label1: str = "Before",
        label2: str = "After"
    ) -> np.ndarray:
        """
        Create side-by-side comparison image.

        Args:
            image1: First image
            image2: Second image
            label1: Label for first image
            label2: Label for second image

        Returns:
            Combined comparison image
        """
        # Ensure both images have same height
        h1, w1 = image1.shape[:2]
        h2, w2 = image2.shape[:2]

        if h1 != h2:
            # Resize to match heights
            target_h = min(h1, h2)
            image1 = cv2.resize(image1, (int(w1 * target_h / h1), target_h))
            image2 = cv2.resize(image2, (int(w2 * target_h / h2), target_h))

        # Add labels
        labeled1 = image1.copy()
        labeled2 = image2.copy()

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.0
        thickness = 2
        color = (255, 255, 255)
        outline_color = (0, 0, 0)

        # Add label to first image
        x1, y1 = 10, 40
        cv2.putText(labeled1, label1, (x1, y1), font, font_scale, outline_color, thickness + 2)
        cv2.putText(labeled1, label1, (x1, y1), font, font_scale, color, thickness)

        # Add label to second image
        x2, y2 = 10, 40
        cv2.putText(labeled2, label2, (x2, y2), font, font_scale, outline_color, thickness + 2)
        cv2.putText(labeled2, label2, (x2, y2), font, font_scale, color, thickness)

        # Concatenate horizontally
        comparison = np.hstack([labeled1, labeled2])

        return comparison

    def visualize_multi_regions(
        self,
        image: np.ndarray,
        face_landmarks: Any,
        multi_region_result: Dict[str, Any]
    ) -> Optional[np.ndarray]:
        """
        Create visualization showing all sampled regions with color labels.

        Args:
            image: Input image in RGB format
            face_landmarks: MediaPipe face landmarks
            multi_region_result: Results from multi-region analysis

        Returns:
            Annotated image or None
        """
        if "region_colors" not in multi_region_result:
            return None

        viz = image.copy()
        h, w = image.shape[:2]

        region_landmarks = {
            "cheeks": CHEEK_LANDMARKS,
            "forehead": FOREHEAD_LANDMARKS,
            "nose_bridge": NOSE_BRIDGE_LANDMARKS,
            "chin": CHIN_LANDMARKS,
        }

        colors = {
            "cheeks": (255, 100, 100),      # Red
            "forehead": (100, 255, 100),    # Green
            "nose_bridge": (100, 100, 255), # Blue
            "chin": (255, 255, 100),        # Yellow
        }

        # Draw each region
        for region_name, landmarks in region_landmarks.items():
            if region_name in multi_region_result["region_colors"]:
                # Create mask for this region
                mask = np.zeros((h, w), dtype=np.uint8)
                points = []
                for idx in landmarks:
                    if idx < len(face_landmarks.landmark):
                        landmark = face_landmarks.landmark[idx]
                        x = int(landmark.x * w)
                        y = int(landmark.y * h)
                        points.append((x, y))

                if len(points) >= 3:
                    points_array = np.array(points, dtype=np.int32)
                    hull = cv2.convexHull(points_array)
                    cv2.fillConvexPoly(mask, hull, 255)

                    # Draw colored overlay
                    overlay = np.zeros_like(viz)
                    overlay[mask == 255] = colors[region_name]
                    viz = cv2.addWeighted(viz, 0.7, overlay, 0.3, 0)

                    # Draw outline
                    cv2.drawContours(viz, [hull], 0, colors[region_name], 2)

                    # Add label with RGB value
                    rgb = multi_region_result["region_colors"][region_name]
                    centroid = np.mean(points, axis=0).astype(int)
                    label = f"{region_name[:4]}: {rgb}"
                    cv2.putText(viz, label, tuple(centroid),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 2)
                    cv2.putText(viz, label, tuple(centroid),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.4, colors[region_name], 1)

        return viz

    def visualize_contrast(
        self,
        image: np.ndarray,
        face_landmarks: Any,
        contrast_result: Dict[str, Any]
    ) -> Optional[np.ndarray]:
        """
        Create visualization showing eyebrow and skin regions with contrast info.

        Args:
            image: Input image in RGB format
            face_landmarks: MediaPipe face landmarks
            contrast_result: Results from contrast analysis

        Returns:
            Annotated image or None
        """
        viz = image.copy()
        h, w = image.shape[:2]

        # Draw eyebrow regions (blue)
        for eyebrow_landmarks in [LEFT_EYEBROW_LANDMARKS, RIGHT_EYEBROW_LANDMARKS]:
            mask = np.zeros((h, w), dtype=np.uint8)
            points = []
            for idx in eyebrow_landmarks:
                if idx < len(face_landmarks.landmark):
                    landmark = face_landmarks.landmark[idx]
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    points.append((x, y))

            if len(points) >= 3:
                points_array = np.array(points, dtype=np.int32)
                hull = cv2.convexHull(points_array)
                overlay = np.zeros_like(viz)
                cv2.fillConvexPoly(mask, hull, 255)
                overlay[mask == 255] = (100, 100, 255)  # Blue
                viz = cv2.addWeighted(viz, 0.7, overlay, 0.3, 0)
                cv2.drawContours(viz, [hull], 0, (100, 100, 255), 2)

        # Draw cheek region (green)
        mask = np.zeros((h, w), dtype=np.uint8)
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
            overlay = np.zeros_like(viz)
            cv2.fillConvexPoly(mask, hull, 255)
            overlay[mask == 255] = (100, 255, 100)  # Green
            viz = cv2.addWeighted(viz, 0.7, overlay, 0.3, 0)
            cv2.drawContours(viz, [hull], 0, (100, 255, 100), 2)

        # Add text annotation
        contrast_level = contrast_result.get("contrast_level", 0)
        level_category = contrast_result.get("level_category", "unknown")
        text = f"Contrast: {contrast_level:.1f} ({level_category})"

        # Position text at top center
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
        text_x = (w - text_size[0]) // 2
        text_y = 40

        # Draw text with outline
        cv2.putText(viz, text, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 4)
        cv2.putText(viz, text, (text_x, text_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        return viz


# Create a singleton instance
visualization_service = VisualizationService()
