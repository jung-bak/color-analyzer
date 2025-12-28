"""
Pydantic models for API request and response validation.
"""
from typing import List, Dict, Any, Optional, Tuple
from pydantic import BaseModel, Field


class ColorZone(BaseModel):
    """Color wheel zone definition."""
    start: int = Field(..., description="Starting hue (0-360)")
    end: int = Field(..., description="Ending hue (0-360)")
    name: str = Field(..., description="Color name")
    category: str = Field(..., description="Color category")


class LABValues(BaseModel):
    """CIELAB color space values."""
    L: float = Field(..., description="Lightness (0-255)")
    a: float = Field(..., description="Green-Red axis")
    b: float = Field(..., description="Blue-Yellow axis")


class SeasonAnalysis(BaseModel):
    """Detailed season analysis information."""
    is_light: bool = Field(..., description="Whether the coloring is light")
    is_warm: bool = Field(..., description="Whether the undertone is warm")
    lightness_category: str = Field(..., description="Light or Deep")
    temperature_category: str = Field(..., description="Warm or Cool")
    lightness_distance: float = Field(..., description="Distance from lightness threshold")
    warmth_distance: float = Field(..., description="Distance from warmth threshold")
    lab_values: LABValues = Field(..., description="LAB color space values")
    thresholds: Dict[str, int] = Field(..., description="Classification thresholds")


class SeasonDescription(BaseModel):
    """Season description and styling tips."""
    description: str = Field(..., description="Season description")
    characteristics: str = Field(..., description="Characteristics of this season")
    best_colors: str = Field(..., description="Best colors for this season")
    avoid: str = Field(..., description="Colors to avoid")
    metals: str = Field(..., description="Best metal colors")
    tips: str = Field(..., description="Styling tips")


class DebugImage(BaseModel):
    """Debug image with metadata."""
    step: str = Field(..., description="Processing step identifier")
    title: str = Field(..., description="Image title")
    description: str = Field(..., description="Image description")
    image_base64: str = Field(..., description="Base64-encoded image data")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")


class DebugMetadata(BaseModel):
    """Debug metadata for analysis steps."""
    face_detection: Optional[Dict[str, Any]] = Field(default=None, description="Face detection metadata")
    skin_extraction: Optional[Dict[str, Any]] = Field(default=None, description="Skin extraction metadata")
    white_balance: Optional[Dict[str, Any]] = Field(default=None, description="White balance metadata")
    color_analysis: Optional[Dict[str, Any]] = Field(default=None, description="Color analysis metadata")
    timestamp: Optional[str] = Field(default=None, description="Analysis timestamp")


class DebugData(BaseModel):
    """Complete debug data including images and metadata."""
    images: List[DebugImage] = Field(default_factory=list, description="Debug images from each step")
    metadata: DebugMetadata = Field(..., description="Detailed metadata for each step")


class MultiRegionAnalysis(BaseModel):
    """Multi-region skin sampling analysis."""
    regions_sampled: int = Field(..., description="Number of regions successfully sampled")
    agreement_score: float = Field(..., description="How similar regions are (0-1, higher is better)")
    confidence_boost: float = Field(..., description="Confidence adjustment based on agreement")
    status: str = Field(..., description="Analysis status (good/moderate/poor)")
    L_variance: Optional[float] = Field(default=None, description="Variance of lightness across regions")
    warmth_variance: Optional[float] = Field(default=None, description="Variance of warmth across regions")


class VarianceConfidence(BaseModel):
    """Sample variance confidence analysis."""
    variance: Optional[float] = Field(default=None, description="Average pixel variance in sample")
    confidence_factor: float = Field(..., description="Confidence adjustment based on variance")
    status: str = Field(..., description="Variance quality (excellent/good/acceptable/poor)")


class ContrastAnalysis(BaseModel):
    """Contrast level between eyebrows and skin."""
    contrast_level: Optional[float] = Field(default=None, description="L* difference between eyebrows and skin")
    level_category: Optional[str] = Field(default=None, description="Contrast category (high/medium/low)")
    expected_seasons: Optional[List[str]] = Field(default=None, description="Seasons typically associated with this contrast")
    status: str = Field(..., description="Analysis status")


class SeasonProbabilities(BaseModel):
    """Probability distribution for all seasons."""
    Winter: float = Field(..., description="Probability of Winter season (%)")
    Summer: float = Field(..., description="Probability of Summer season (%)")
    Autumn: float = Field(..., description="Probability of Autumn season (%)")
    Spring: float = Field(..., description="Probability of Spring season (%)")


class ColorItem(BaseModel):
    """A single color with name and hex code."""
    name: str = Field(..., description="Color name")
    hex: str = Field(..., description="Hex color code")


class DoDontPair(BaseModel):
    """A do/don't comparison pair of similar colors."""
    do: ColorItem = Field(..., description="Color that works for this season")
    dont: ColorItem = Field(..., description="Similar color to avoid")


class ColorGradient(BaseModel):
    """A color family gradient showing which range works."""
    family: str = Field(..., description="Color family name (e.g., Reds, Blues)")
    gradient: List[str] = Field(..., description="Hex colors from light to dark")
    best_range: List[int] = Field(..., description="[start_idx, end_idx] of best colors in gradient")
    description: str = Field(..., description="Description of which shades work")


class AnalysisResult(BaseModel):
    """Complete color analysis result."""
    season: str = Field(..., description="Season name (Winter/Summer/Autumn/Spring)")
    full_season_name: str = Field(..., description="Full season name with description")
    confidence: float = Field(..., description="Confidence score (0-100)")
    skin_tone_rgb: Tuple[int, int, int] = Field(..., description="RGB color of extracted skin tone")
    lab_values: LABValues = Field(..., description="LAB color space values")
    palette: List[str] = Field(..., description="Hex color codes for season palette")
    description: SeasonDescription = Field(..., description="Season description and tips")
    analysis: SeasonAnalysis = Field(..., description="Detailed analysis information")
    white_balance_applied: bool = Field(..., description="Whether white balance was applied")
    white_balance_method: str = Field(..., description="White balance method used (background/skin_locus/none)")
    white_balance_metadata: Dict[str, Any] = Field(default_factory=dict, description="White balance metadata")
    color_zones_safe: List[ColorZone] = Field(..., description="Safe color zones on wheel")
    color_zones_avoid: List[ColorZone] = Field(..., description="Colors to avoid")
    # Color visualization data
    color_categories: Dict[str, List[Dict[str, str]]] = Field(..., description="Organized color categories (neutrals, accents)")
    do_dont_pairs: List[Dict] = Field(..., description="Do/Don't comparison pairs")
    color_gradients: List[Dict] = Field(..., description="Color family gradients with best ranges")
    # Probability and analysis fields
    season_probabilities: SeasonProbabilities = Field(..., description="Probability distribution for all seasons")
    multi_region_analysis: MultiRegionAnalysis = Field(..., description="Multi-region skin sampling results")
    variance_confidence: VarianceConfidence = Field(..., description="Sample variance confidence analysis")
    contrast_analysis: ContrastAnalysis = Field(..., description="Contrast level analysis")
    debug_data: Optional[DebugData] = Field(default=None, description="Debug information (only if debug mode enabled)")


class ErrorResponse(BaseModel):
    """Error response."""
    error: str = Field(..., description="Error message")
    details: Optional[str] = Field(None, description="Additional error details")


class HealthCheck(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")


class SeasonsResponse(BaseModel):
    """Response containing all season palettes."""
    seasons: Dict[str, List[str]] = Field(..., description="Dictionary of season names to color palettes")

