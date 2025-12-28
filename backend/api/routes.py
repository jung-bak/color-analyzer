"""
FastAPI routes for color analysis endpoints.
"""
import io
import numpy as np
from PIL import Image
from fastapi import APIRouter, UploadFile, File, HTTPException, Query

# Register HEIC/HEIF support with Pillow
import pillow_heif
pillow_heif.register_heif_opener()
from fastapi.responses import JSONResponse

from backend.models.schemas import (
    AnalysisResult,
    ErrorResponse,
    HealthCheck,
    SeasonsResponse,
    LABValues,
    SeasonDescription,
    SeasonAnalysis,
    ColorZone,
    DebugData,
    DebugMetadata,
    DebugImage,
    MultiRegionAnalysis,
    VarianceConfidence,
    ContrastAnalysis,
    SeasonProbabilities,
)
from backend.services.face_analyzer import face_analyzer
from backend.services.season_classifier import season_classifier
from backend.core.config import settings
from backend.core.palettes import (
    SEASON_PALETTES, 
    get_season_color_zones,
    get_season_color_categories,
    get_season_do_dont_pairs,
    get_season_color_gradients,
)


router = APIRouter()


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint."""
    return HealthCheck(
        status="healthy",
        version=settings.APP_VERSION,
    )


@router.get("/seasons", response_model=SeasonsResponse)
async def get_seasons():
    """Get all season color palettes."""
    return SeasonsResponse(seasons=SEASON_PALETTES)


@router.post("/analyze", response_model=AnalysisResult)
async def analyze_image(
    file: UploadFile = File(...),
    white_balance: bool = Query(True, description="Apply white balance correction"),
    debug: bool = Query(False, description="Enable debug mode to see analysis steps"),
):
    """
    Analyze uploaded image to determine seasonal color palette.
    
    Args:
        file: Uploaded image file (jpg, jpeg, png)
        white_balance: Whether to apply white balance correction
        debug: Whether to return debug visualizations and metadata
    
    Returns:
        Complete color analysis result with optional debug data
    
    Raises:
        HTTPException: If image is invalid or analysis fails
    """
    # Validate file type
    # HEIC files may have empty content_type or application/octet-stream in some browsers
    valid_content_types = ["image/jpeg", "image/png", "image/heic", "image/heif"]
    filename_lower = (file.filename or "").lower()
    is_heic_extension = filename_lower.endswith(".heic") or filename_lower.endswith(".heif")

    is_valid = (
        (file.content_type and file.content_type.startswith("image/")) or
        (is_heic_extension and (not file.content_type or file.content_type == "application/octet-stream"))
    )

    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload an image (jpg, jpeg, png, or heic).",
        )
    
    # Read and validate file size
    try:
        contents = await file.read()
        
        if len(contents) > settings.MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE / 1024 / 1024:.1f}MB.",
            )
        
        # Open image with PIL
        image_pil = Image.open(io.BytesIO(contents))
        
        # Convert to RGB if necessary
        if image_pil.mode != "RGB":
            image_pil = image_pil.convert("RGB")
        
        # Convert to numpy array
        image_np = np.array(image_pil)
        
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to process image: {str(e)}",
        )
    
    # Analyze the image
    try:
        analysis_result = face_analyzer.analyze_image(
            image_np,
            apply_white_balance=white_balance,
            debug=debug,
        )
        
        if not analysis_result["success"]:
            raise HTTPException(
                status_code=400,
                detail=analysis_result["error"],
            )
        
        # Classify season with confidence factors
        classification = season_classifier.classify(
            analysis_result["lab_values"],
            multi_region_analysis=analysis_result.get("multi_region_analysis"),
            variance_confidence=analysis_result.get("variance_confidence"),
            contrast_analysis=analysis_result.get("contrast_analysis"),
        )
        
        # Get color zones for the detected season
        zones = get_season_color_zones(classification["season"])
        
        # Get structured color visualization data
        color_categories = get_season_color_categories(classification["season"])
        do_dont_pairs = get_season_do_dont_pairs(classification["season"])
        color_gradients = get_season_color_gradients(classification["season"])
        
        # Build debug data if debug mode is enabled
        debug_data = None
        if debug and "debug_images" in analysis_result:
            # Add color analysis metadata to debug metadata
            if "debug_metadata" in analysis_result:
                analysis_result["debug_metadata"]["color_analysis"] = {
                    "L_value": classification["analysis"]["lab_values"]["L"],
                    "a_value": classification["analysis"]["lab_values"]["a"],
                    "b_value": classification["analysis"]["lab_values"]["b"],
                    "warm_threshold": classification["analysis"]["thresholds"]["warmth"],
                    "is_warm": classification["analysis"]["is_warm"],
                    "light_threshold": classification["analysis"]["thresholds"]["lightness"],
                    "is_light": classification["analysis"]["is_light"],
                    "season_determined": classification["season"],
                    "confidence": classification["confidence"],
                    "confidence_breakdown": classification.get("confidence_breakdown", {}),
                    "season_probabilities": classification.get("season_probabilities", {}),
                }
            
            debug_data = DebugData(
                images=[DebugImage(**img) for img in analysis_result["debug_images"]],
                metadata=DebugMetadata(**analysis_result.get("debug_metadata", {})),
            )
        
        # Build response
        response = AnalysisResult(
            season=classification["season"],
            full_season_name=classification["full_season_name"],
            confidence=classification["confidence"],
            skin_tone_rgb=analysis_result["rgb_color"],
            lab_values=LABValues(**analysis_result["lab_values"]),
            palette=classification["palette"],
            description=SeasonDescription(**classification["description"]),
            analysis=SeasonAnalysis(**classification["analysis"]),
            white_balance_applied=analysis_result["white_balance_applied"],
            white_balance_method=analysis_result["white_balance_method"],
            white_balance_metadata=analysis_result["white_balance_metadata"],
            color_zones_safe=[ColorZone(**zone) for zone in zones["safe_zones"]],
            color_zones_avoid=[ColorZone(**zone) for zone in zones["avoid_zones"]],
            # Color visualization data
            color_categories=color_categories,
            do_dont_pairs=do_dont_pairs,
            color_gradients=color_gradients,
            # NEW QUICK WIN FIELDS
            season_probabilities=SeasonProbabilities(**classification["season_probabilities"]),
            multi_region_analysis=MultiRegionAnalysis(**analysis_result["multi_region_analysis"]),
            variance_confidence=VarianceConfidence(**analysis_result["variance_confidence"]),
            contrast_analysis=ContrastAnalysis(**analysis_result["contrast_analysis"]),
            debug_data=debug_data,
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}",
        )

