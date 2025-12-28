"""
Season classification based on CIELAB color space analysis.
"""
import numpy as np
from typing import Dict, Any, Tuple, Optional

from backend.core.config import settings
from backend.core.palettes import (
    get_season_full_name,
    get_season_palette,
    get_season_description,
)


class SeasonClassifier:
    """Classifies skin tone into seasonal color categories."""
    
    def classify(
        self, 
        lab_values: Dict[str, float],
        multi_region_analysis: Optional[Dict[str, Any]] = None,
        variance_confidence: Optional[Dict[str, Any]] = None,
        contrast_analysis: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Classify season based on LAB color values with enhanced confidence calculation.
        
        Uses improved warm/cool detection based on the relationship between
        a* (pink-green) and b* (yellow-blue) axes. Warm undertones have
        relatively more yellow (b*) than pink (a*), while cool undertones
        have relatively more pink than yellow.
        
        Args:
            lab_values: Dictionary with 'L', 'a', 'b' values (OpenCV 0-255 scale)
            multi_region_analysis: Optional multi-region sampling results
            variance_confidence: Optional sample variance analysis
            contrast_analysis: Optional contrast level analysis
        
        Returns:
            Dictionary with season, confidence, and detailed analysis
        """
        L = lab_values['L']
        a = lab_values['a']
        b = lab_values['b']
        
        # Convert from OpenCV scale (0-255) to standard LAB
        # a and b: subtract 128 to get signed values (-128 to +127)
        a_normalized = a - 128  # Positive = more red/pink, Negative = more green
        b_normalized = b - 128  # Positive = more yellow, Negative = more blue
        
        # Calculate warmth indicator (b* - a*)
        # Positive = more yellow than pink = WARM
        # Negative/low = more pink than yellow = COOL
        warmth_indicator = b_normalized - a_normalized
        
        # Calculate probability distribution for all seasons FIRST
        # This ensures the classified season matches the highest probability
        season_probabilities = self._calculate_season_probabilities(L, warmth_indicator)
        
        # Classify season based on HIGHEST PROBABILITY (not thresholds)
        # This ensures consistency between displayed season and breakdown percentages
        season = max(season_probabilities, key=season_probabilities.get)
        
        # Derive is_light and is_warm from the selected season for display
        is_light = season in ("Summer", "Spring")
        is_warm = season in ("Autumn", "Spring")
        
        # Calculate BASE confidence from the probability of the top season
        # Higher probability = higher confidence
        top_probability = season_probabilities[season]
        base_confidence = min(50.0 + (top_probability - 25.0), 95.0)  # Scale from prob
        
        # ENHANCED: Apply confidence adjustments from all analyses
        confidence_adjustments = {
            "base_confidence": round(base_confidence, 1),
            "multi_region_boost": 0.0,
            "variance_adjustment": 0.0,
            "contrast_validation": 0.0,
        }
        
        # Apply multi-region confidence boost
        if multi_region_analysis and multi_region_analysis.get("status") != "insufficient_regions":
            confidence_adjustments["multi_region_boost"] = multi_region_analysis.get("confidence_boost", 0.0)
        
        # Apply variance confidence adjustment
        if variance_confidence:
            confidence_adjustments["variance_adjustment"] = variance_confidence.get("confidence_factor", 0.0)
        
        # Apply contrast validation (check if contrast matches expected for this season)
        if contrast_analysis and contrast_analysis.get("status") == "success":
            expected_seasons = contrast_analysis.get("expected_seasons", [])
            if expected_seasons and expected_seasons != ["All"]:
                # Bonus if contrast matches the classified season
                if season in expected_seasons:
                    confidence_adjustments["contrast_validation"] = 3.0
                else:
                    # Small penalty if contrast doesn't match (could be lighting)
                    confidence_adjustments["contrast_validation"] = -2.0
        
        # Calculate final confidence (cap at 99%, min at 30%)
        final_confidence = base_confidence + sum([
            confidence_adjustments["multi_region_boost"],
            confidence_adjustments["variance_adjustment"],
            confidence_adjustments["contrast_validation"],
        ])
        final_confidence = max(30.0, min(99.0, final_confidence))
        
        # Get season information
        full_season_name = get_season_full_name(season)
        palette = get_season_palette(season)
        description = get_season_description(season)
        
        # Calculate distances from thresholds
        lightness_distance = abs(L - settings.LAB_LIGHTNESS_THRESHOLD)
        warmth_distance = abs(warmth_indicator - settings.LAB_WARM_COOL_THRESHOLD)
        
        return {
            "season": season,
            "full_season_name": full_season_name,
            "confidence": round(final_confidence, 1),
            "confidence_breakdown": confidence_adjustments,  # NEW: Show how confidence was calculated
            "palette": palette,
            "description": description,
            "season_probabilities": season_probabilities,  # NEW: Probability for each season
            "analysis": {
                "is_light": is_light,
                "is_warm": is_warm,
                "lightness_category": "Light" if is_light else "Deep",
                "temperature_category": "Warm" if is_warm else "Cool",
                "lightness_distance": float(lightness_distance),
                "warmth_distance": float(warmth_distance),
                "warmth_indicator": float(warmth_indicator),  # b* - a* (positive = warm)
                "lab_values": {
                    "L": float(L),
                    "a": float(a),
                    "b": float(b),
                },
                "thresholds": {
                    "lightness": settings.LAB_LIGHTNESS_THRESHOLD,
                    "warmth": settings.LAB_WARM_COOL_THRESHOLD,
                },
            },
        }
    
    def _calculate_confidence(self, L: float, warmth_indicator: float) -> float:
        """
        Calculate confidence score based on distance from thresholds.
        
        The further away from the decision boundaries, the higher the confidence.
        
        Args:
            L: Lightness value (0-255 OpenCV scale)
            warmth_indicator: b* - a* value (positive = warm, negative = cool)
        
        Returns:
            Confidence score (0-100)
        """
        # Calculate distances from thresholds
        lightness_distance = abs(L - settings.LAB_LIGHTNESS_THRESHOLD)
        warmth_distance = abs(warmth_indicator - settings.LAB_WARM_COOL_THRESHOLD)
        
        # Normalize distances
        # For lightness: max meaningful distance is ~50 units
        # For warmth indicator: max meaningful distance is ~20 units (b*-a* range is smaller)
        normalized_lightness = min(lightness_distance / 50.0, 1.0)
        normalized_warmth = min(warmth_distance / 20.0, 1.0)
        
        # Average the two normalized distances
        avg_distance = (normalized_lightness + normalized_warmth) / 2.0
        
        # Convert to confidence percentage (50% base + 50% from distance)
        # Even borderline cases get at least 50% confidence
        confidence = 50.0 + (avg_distance * 50.0)
        
        return round(confidence, 1)
    
    def _calculate_season_probabilities(
        self, 
        L: float, 
        warmth_indicator: float
    ) -> Dict[str, float]:
        """
        Calculate probability distribution for all four seasons.
        
        Instead of binary classification, this shows how likely each season is
        based on Euclidean distance from the "ideal center" of each season.
        
        Uses a softmax function with negative distances (closer = higher prob).
        
        Args:
            L: Lightness value (0-255 OpenCV scale)
            warmth_indicator: b* - a* value (warm/cool indicator)
        
        Returns:
            Dictionary with probability for each season (sums to 100%)
        """
        # Define "ideal centers" for each season
        # L ranges from ~120 (deep) to ~200 (light) for typical skin
        # Warmth indicator ranges from ~-15 (very cool) to ~+20 (very warm)
        season_centers = {
            "Winter": {"L": 130, "warmth": -8},   # Cool & Deep
            "Summer": {"L": 175, "warmth": -5},   # Cool & Light  
            "Autumn": {"L": 135, "warmth": 12},   # Warm & Deep
            "Spring": {"L": 175, "warmth": 10},   # Warm & Light
        }
        
        # Calculate weighted Euclidean distance from current values to each season center
        # Weight L and warmth differently since they have different scales
        distances = {}
        for season, center in season_centers.items():
            # L difference: typical range ~80 units between light/deep
            L_diff = (L - center["L"]) / 40.0  # Normalize by half-range
            # Warmth difference: typical range ~25 units between warm/cool
            warmth_diff = (warmth_indicator - center["warmth"]) / 12.0
            
            distance = np.sqrt(L_diff**2 + warmth_diff**2)
            distances[season] = distance
        
        # Convert distances to probabilities using softmax with negative distances
        # This ensures closer seasons get exponentially higher probability
        # Temperature controls how peaked the distribution is
        temperature = 0.5  # Lower = more peaked (dominant season stands out more)
        
        # Apply softmax: exp(-distance/temperature)
        exp_scores = {}
        for season, dist in distances.items():
            exp_scores[season] = np.exp(-dist / temperature)
        
        # Normalize to sum to 100%
        total = sum(exp_scores.values())
        if total == 0:
            # Fallback: equal probabilities
            return {"Winter": 25.0, "Summer": 25.0, "Autumn": 25.0, "Spring": 25.0}
        
        probabilities = {season: (score / total) * 100.0 for season, score in exp_scores.items()}
        
        # Round to 1 decimal place
        probabilities = {season: round(prob, 1) for season, prob in probabilities.items()}
        
        return probabilities
    
    def get_complementary_season(self, season: str) -> str:
        """
        Get the complementary (opposite) season.
        
        Args:
            season: Season name
        
        Returns:
            Complementary season name
        """
        complementary_map = {
            "Winter": "Summer",
            "Summer": "Winter",
            "Autumn": "Spring",
            "Spring": "Autumn",
        }
        return complementary_map.get(season, season)
    
    def get_adjacent_seasons(self, season: str) -> Tuple[str, str]:
        """
        Get the two adjacent seasons (sharing one characteristic).
        
        Args:
            season: Season name
        
        Returns:
            Tuple of two adjacent season names
        """
        adjacent_map = {
            "Winter": ("Summer", "Autumn"),  # Cool, Deep
            "Summer": ("Winter", "Spring"),  # Cool, Light
            "Autumn": ("Winter", "Spring"),  # Warm, Deep
            "Spring": ("Summer", "Autumn"),  # Warm, Light
        }
        return adjacent_map.get(season, ("", ""))


# Create a singleton instance
season_classifier = SeasonClassifier()

