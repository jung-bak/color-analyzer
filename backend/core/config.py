"""
Configuration settings for the Color Analyzer application.
"""
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings."""
    
    # Application
    APP_NAME: str = "Personal Color Analysis"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", 10485760))  # 10MB default
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png"]
    
    # CORS
    ALLOWED_ORIGINS: List[str] = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost:8000,http://127.0.0.1:8000"
    ).split(",")
    
    # MediaPipe Configuration
    FACE_MESH_MAX_FACES: int = 1
    # Refine landmarks enables iris tracking but requires OpenGL/GPU
    # Disable on headless servers (Render, etc.) by setting DISABLE_IRIS_TRACKING=true
    # or RENDER=true environment variable
    FACE_MESH_REFINE_LANDMARKS: bool = not (
        os.getenv("DISABLE_IRIS_TRACKING", "false").lower() == "true" or
        os.getenv("RENDER", "false").lower() == "true"
    )
    FACE_MESH_MIN_DETECTION_CONFIDENCE: float = 0.5
    FACE_MESH_MIN_TRACKING_CONFIDENCE: float = 0.5
    
    SELFIE_SEGMENTATION_MODEL: int = 1  # 0 = general, 1 = landscape (better for portraits)
    
    # Color Analysis Thresholds
    LAB_LIGHTNESS_THRESHOLD: int = 155  # Above = Light, Below = Deep (OpenCV 0-255 scale)
    
    # Warmth threshold now uses (b* - a*) instead of raw b*
    # Positive = more yellow than pink = Warm undertones
    # Negative = more pink than yellow = Cool undertones
    # Threshold of 5 provides good separation based on empirical testing:
    #   Warm skin: indicator typically +10 to +15
    #   Cool skin: indicator typically -5 to +3
    LAB_WARM_COOL_THRESHOLD: int = 5  # (b* - a*) above = Warm, below = Cool
    
    # White Balance Thresholds
    WB_MIN_BACKGROUND_PERCENTAGE: float = 0.10  # 10% of image
    WB_MAX_BACKGROUND_VARIANCE: float = 30.0  # Standard deviation threshold
    
    # Skin Locus Constants (from dermatology research)
    SKIN_LOCUS_SLOPE: float = -1.73
    SKIN_LOCUS_INTERCEPT: float = 1.06
    SKIN_LOCUS_CORRECTION_STRENGTH: float = 2.0
    
    # Image Quality Thresholds
    MIN_PIXEL_INTENSITY: int = 30  # Too dark
    MAX_PIXEL_INTENSITY: int = 225  # Too bright


settings = Settings()

