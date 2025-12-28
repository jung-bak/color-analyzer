"""
Seasonal color palettes and face landmark indices.
"""
from typing import Dict, List

# Seasonal Color Palettes (Hex codes)
SEASON_PALETTES: Dict[str, List[str]] = {
    "Winter": [
        "#000000",  # True Black
        "#FFFFFF",  # Pure White
        "#C6062F",  # True Red
        "#123087",  # Royal Blue
        "#066B44",  # Emerald Green
        "#8B008B",  # Magenta
        "#2F4F4F",  # Dark Slate Gray
        "#FF1493",  # Deep Pink
    ],
    "Summer": [
        "#728CA6",  # Soft Blue
        "#99A2C1",  # Periwinkle
        "#CDA5B4",  # Dusty Rose
        "#F4F4F4",  # Soft White
        "#B2B2B2",  # Soft Gray
        "#8B9D83",  # Sage Green
        "#D8BFD8",  # Lavender
        "#B0C4DE",  # Light Steel Blue
    ],
    "Autumn": [
        "#6E4C3D",  # Coffee Brown
        "#D17B0F",  # Burnt Orange
        "#4F591E",  # Olive Green
        "#A82618",  # Rust Red
        "#E6CCA0",  # Warm Beige
        "#8B4513",  # Saddle Brown
        "#CD853F",  # Peru (Tan)
        "#556B2F",  # Dark Olive Green
    ],
    "Spring": [
        "#FF7F50",  # Coral
        "#FADA5E",  # Warm Yellow
        "#40E0D0",  # Turquoise
        "#FA8072",  # Salmon (warm pink)
        "#F5F5DC",  # Warm Cream
        "#98FB98",  # Pale Green
        "#FFB6C1",  # Light Pink
        "#FFA500",  # Orange
    ],
}

# Season Descriptions and Styling Tips
SEASON_DESCRIPTIONS: Dict[str, Dict[str, str]] = {
    "Winter": {
        "description": "Cool and Deep - High contrast with cool undertones",
        "characteristics": "Your skin has blue or pink undertones with a deeper, more intense coloring. You have high contrast between your hair, eyes, and skin.",
        "best_colors": "True, vibrant colors with blue undertones. Black, pure white, jewel tones.",
        "avoid": "Warm, muted colors like orange, gold, and earth tones.",
        "metals": "Silver, platinum, white gold",
        "tips": "Wear bold, clear colors close to your face. High contrast looks suit you best.",
    },
    "Summer": {
        "description": "Cool and Light - Soft contrast with cool undertones",
        "characteristics": "Your skin has blue or pink undertones with lighter, softer coloring. You have low to medium contrast.",
        "best_colors": "Soft, muted colors with blue undertones. Pastels, dusty shades, soft neutrals.",
        "avoid": "Warm colors like orange and gold. Bright, harsh colors.",
        "metals": "Silver, rose gold, pewter",
        "tips": "Soft, blended colors work best. Tone-on-tone and monochromatic looks are flattering.",
    },
    "Autumn": {
        "description": "Warm and Deep - Rich, warm undertones with depth",
        "characteristics": "Your skin has golden, peachy, or yellow undertones with deeper coloring. You may have warm-toned hair and eyes.",
        "best_colors": "Rich, warm earth tones. Browns, oranges, warm greens, gold.",
        "avoid": "Cool colors like icy blue, pure black, and bright white.",
        "metals": "Gold, copper, bronze, brass",
        "tips": "Layer warm, rich colors. Earthy, natural combinations work beautifully.",
    },
    "Spring": {
        "description": "Warm and Light - Bright, warm undertones with clarity",
        "characteristics": "Your skin has golden, peachy undertones with lighter coloring. You have a fresh, warm appearance.",
        "best_colors": "Clear, warm colors. Coral, peach, warm yellow, turquoise, warm pastels.",
        "avoid": "Cool, dark colors like black, navy, and cool grays.",
        "metals": "Gold, rose gold, yellow gold",
        "tips": "Bright, clear colors enhance your natural warmth. Avoid heavy, dark shades.",
    },
}

# MediaPipe Face Mesh Landmark Indices
# Face Mesh has 468 landmarks total

# Cheek region for skin tone extraction (primary analysis area)
CHEEK_LANDMARKS: List[int] = [
    116, 117, 118, 123, 147, 187, 205,  # Left cheek
    345, 346, 347, 352, 376, 411, 425,  # Right cheek
]

# Skin regions for white balance (Skin Locus method)
SKIN_LANDMARKS: List[int] = [
    # Forehead
    10, 67, 69, 104, 108, 151, 337, 299,
    # Left cheek
    116, 117, 118, 123, 147, 187, 205,
    # Right cheek
    345, 346, 347, 352, 376, 411, 425,
    # Nose bridge
    6, 197, 195, 5,
]

# Multi-region landmarks for robust skin tone extraction
FOREHEAD_LANDMARKS: List[int] = [
    10, 67, 69, 104, 108, 151, 337, 299,  # Center forehead
]

NOSE_BRIDGE_LANDMARKS: List[int] = [
    6, 197, 195, 5, 168, 122, 351,  # Nose bridge (not nose tip)
]

CHIN_LANDMARKS: List[int] = [
    152, 175, 199, 200, 428, 422, 400, 377,  # Chin area
]

# Eyebrow regions for contrast analysis
LEFT_EYEBROW_LANDMARKS: List[int] = [
    70, 63, 105, 66, 107, 55, 65, 52, 53, 46,
]

RIGHT_EYEBROW_LANDMARKS: List[int] = [
    300, 293, 334, 296, 336, 285, 295, 282, 283, 276,
]

# Landmarks to EXCLUDE from skin mask (eyes, lips, eyebrows)
EXCLUDE_LANDMARKS: List[int] = [
    # Left eye
    33, 7, 163, 144, 145, 153, 154, 155, 133,
    # Right eye
    263, 249, 390, 373, 374, 380, 381, 382, 362,
    # Left eyebrow
    70, 63, 105, 66, 107, 55, 65, 52, 53, 46,
    # Right eyebrow
    300, 293, 334, 296, 336, 285, 295, 282, 283, 276,
    # Lips (outer)
    61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291,
    # Lips (inner)
    78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308,
]


def get_season_full_name(season: str) -> str:
    """Convert short season name to full descriptive name."""
    season_map = {
        "Winter": "Winter (Cool & Deep)",
        "Summer": "Summer (Cool & Light)",
        "Autumn": "Autumn (Warm & Deep)",
        "Spring": "Spring (Warm & Light)",
    }
    return season_map.get(season, season)


def get_season_palette(season: str) -> List[str]:
    """Get color palette for a season."""
    return SEASON_PALETTES.get(season, [])


def get_season_description(season: str) -> Dict[str, str]:
    """Get description and styling tips for a season."""
    return SEASON_DESCRIPTIONS.get(season, {})


# Color wheel zones (in HSL hue degrees 0-360)
SEASON_COLOR_ZONES: Dict[str, Dict[str, List[Dict[str, any]]]] = {
    "Winter": {
        "safe_zones": [
            {"start": 0, "end": 15, "name": "True Red", "category": "Jewel Tones"},
            {"start": 150, "end": 170, "name": "Emerald Green", "category": "Jewel Tones"},
            {"start": 180, "end": 270, "name": "Blue-Purple", "category": "Cool Tones"},
            {"start": 340, "end": 360, "name": "Blue-Based Red", "category": "Jewel Tones"},
        ],
        "avoid_zones": [
            {"start": 30, "end": 90, "name": "Orange-Yellow", "category": "Warm Earth Tones"},
        ]
    },
    "Summer": {
        "safe_zones": [
            {"start": 100, "end": 150, "name": "Sage Green", "category": "Soft Pastels"},
            {"start": 180, "end": 240, "name": "Soft Blue", "category": "Cool Pastels"},
            {"start": 300, "end": 330, "name": "Lavender", "category": "Cool Pastels"},
            {"start": 320, "end": 350, "name": "Soft Pink", "category": "Cool Pastels"},
        ],
        "avoid_zones": [
            {"start": 0, "end": 60, "name": "Bright Warm", "category": "Warm Tones"},
        ]
    },
    "Autumn": {
        "safe_zones": [
            {"start": 0, "end": 45, "name": "Warm Red-Orange", "category": "Earth Tones"},
            {"start": 45, "end": 120, "name": "Olive-Yellow", "category": "Warm Earth Tones"},
            {"start": 165, "end": 180, "name": "Warm Teal", "category": "Earth Tones"},
        ],
        "avoid_zones": [
            {"start": 180, "end": 240, "name": "Cool Blue", "category": "Icy Colors"},
        ]
    },
    "Spring": {
        "safe_zones": [
            {"start": 0, "end": 90, "name": "Coral-Yellow", "category": "Warm Brights"},
            {"start": 165, "end": 190, "name": "Warm Aqua", "category": "Clear Brights"},
        ],
        "avoid_zones": [
            {"start": 240, "end": 300, "name": "Deep Blue-Purple", "category": "Dark Colors"},
        ]
    }
}


def get_season_color_zones(season: str) -> Dict[str, List[Dict]]:
    """Get color wheel zones for a season."""
    return SEASON_COLOR_ZONES.get(season, {"safe_zones": [], "avoid_zones": []})


# Structured color categories for palette cards
SEASON_COLOR_CATEGORIES: Dict[str, Dict[str, List[Dict[str, str]]]] = {
    "Winter": {
        "neutrals": [
            {"name": "True Black", "hex": "#000000"},
            {"name": "Pure White", "hex": "#FFFFFF"},
            {"name": "Charcoal", "hex": "#36454F"},
            {"name": "Navy", "hex": "#000080"},
        ],
        "accents": [
            {"name": "True Red", "hex": "#C6062F"},
            {"name": "Royal Blue", "hex": "#4169E1"},
            {"name": "Emerald", "hex": "#50C878"},
            {"name": "Magenta", "hex": "#FF0090"},
            {"name": "Deep Purple", "hex": "#673AB7"},
            {"name": "Icy Pink", "hex": "#F8BBD9"},
        ],
        "avoid": [
            {"name": "Orange", "hex": "#FF8C00"},
            {"name": "Mustard", "hex": "#FFDB58"},
            {"name": "Olive", "hex": "#808000"},
            {"name": "Cream", "hex": "#FFFDD0"},
            {"name": "Rust", "hex": "#B7410E"},
            {"name": "Warm Brown", "hex": "#8B4513"},
        ],
    },
    "Summer": {
        "neutrals": [
            {"name": "Soft White", "hex": "#F5F5F5"},
            {"name": "Dove Gray", "hex": "#708090"},
            {"name": "Cocoa", "hex": "#8B7D7B"},
            {"name": "Soft Navy", "hex": "#3D4F6F"},
        ],
        "accents": [
            {"name": "Dusty Rose", "hex": "#C9A9A6"},
            {"name": "Lavender", "hex": "#B57EDC"},
            {"name": "Powder Blue", "hex": "#B0E0E6"},
            {"name": "Sage Green", "hex": "#9CAF88"},
            {"name": "Mauve", "hex": "#E0B0FF"},
            {"name": "Periwinkle", "hex": "#8E82FE"},
        ],
        "avoid": [
            {"name": "Bright Orange", "hex": "#FF4500"},
            {"name": "True Black", "hex": "#000000"},
            {"name": "Pure White", "hex": "#FFFFFF"},
            {"name": "Bright Yellow", "hex": "#FFFF00"},
            {"name": "Kelly Green", "hex": "#4CBB17"},
            {"name": "Hot Pink", "hex": "#FF1493"},
        ],
    },
    "Autumn": {
        "neutrals": [
            {"name": "Cream", "hex": "#FFFDD0"},
            {"name": "Camel", "hex": "#C19A6B"},
            {"name": "Chocolate", "hex": "#7B3F00"},
            {"name": "Olive", "hex": "#556B2F"},
        ],
        "accents": [
            {"name": "Burnt Orange", "hex": "#CC5500"},
            {"name": "Rust", "hex": "#B7410E"},
            {"name": "Mustard", "hex": "#FFDB58"},
            {"name": "Terracotta", "hex": "#E2725B"},
            {"name": "Teal", "hex": "#008080"},
            {"name": "Forest Green", "hex": "#228B22"},
        ],
        "avoid": [
            {"name": "Icy Blue", "hex": "#A5F2F3"},
            {"name": "Pure White", "hex": "#FFFFFF"},
            {"name": "True Black", "hex": "#000000"},
            {"name": "Fuchsia", "hex": "#FF00FF"},
            {"name": "Lavender", "hex": "#E6E6FA"},
            {"name": "Cool Pink", "hex": "#FFB6C1"},
        ],
    },
    "Spring": {
        "neutrals": [
            {"name": "Warm White", "hex": "#FAF9F6"},
            {"name": "Camel", "hex": "#C19A6B"},
            {"name": "Warm Gray", "hex": "#8B8589"},
            {"name": "Light Navy", "hex": "#3B5998"},
        ],
        "accents": [
            {"name": "Coral", "hex": "#FF7F50"},
            {"name": "Peach", "hex": "#FFCBA4"},
            {"name": "Turquoise", "hex": "#40E0D0"},
            {"name": "Bright Yellow", "hex": "#FFD700"},
            {"name": "Warm Pink", "hex": "#FF69B4"},
            {"name": "Apple Green", "hex": "#8DB600"},
        ],
        "avoid": [
            {"name": "True Black", "hex": "#000000"},
            {"name": "Navy", "hex": "#000080"},
            {"name": "Burgundy", "hex": "#800020"},
            {"name": "Dark Brown", "hex": "#3D2314"},
            {"name": "Dusty Rose", "hex": "#C9A9A6"},
            {"name": "Charcoal", "hex": "#36454F"},
        ],
    },
}

# Do/Don't comparison pairs - similar colors, one works, one doesn't
SEASON_DO_DONT_PAIRS: Dict[str, List[Dict[str, Dict[str, str]]]] = {
    "Winter": [
        {"do": {"name": "True Red", "hex": "#C6062F"}, "dont": {"name": "Tomato Red", "hex": "#FF6347"}},
        {"do": {"name": "Icy Pink", "hex": "#F8BBD9"}, "dont": {"name": "Peach", "hex": "#FFCBA4"}},
        {"do": {"name": "Pure White", "hex": "#FFFFFF"}, "dont": {"name": "Cream", "hex": "#FFFDD0"}},
        {"do": {"name": "Royal Blue", "hex": "#4169E1"}, "dont": {"name": "Teal", "hex": "#008080"}},
        {"do": {"name": "Emerald", "hex": "#50C878"}, "dont": {"name": "Olive", "hex": "#808000"}},
        {"do": {"name": "True Black", "hex": "#000000"}, "dont": {"name": "Brown", "hex": "#8B4513"}},
    ],
    "Summer": [
        {"do": {"name": "Dusty Rose", "hex": "#C9A9A6"}, "dont": {"name": "Coral", "hex": "#FF7F50"}},
        {"do": {"name": "Powder Blue", "hex": "#B0E0E6"}, "dont": {"name": "Bright Blue", "hex": "#0096FF"}},
        {"do": {"name": "Soft White", "hex": "#F5F5F5"}, "dont": {"name": "Stark White", "hex": "#FFFFFF"}},
        {"do": {"name": "Lavender", "hex": "#B57EDC"}, "dont": {"name": "Bright Purple", "hex": "#8B00FF"}},
        {"do": {"name": "Sage Green", "hex": "#9CAF88"}, "dont": {"name": "Kelly Green", "hex": "#4CBB17"}},
        {"do": {"name": "Dove Gray", "hex": "#708090"}, "dont": {"name": "True Black", "hex": "#000000"}},
    ],
    "Autumn": [
        {"do": {"name": "Burnt Orange", "hex": "#CC5500"}, "dont": {"name": "Bright Orange", "hex": "#FF4500"}},
        {"do": {"name": "Cream", "hex": "#FFFDD0"}, "dont": {"name": "Pure White", "hex": "#FFFFFF"}},
        {"do": {"name": "Teal", "hex": "#008080"}, "dont": {"name": "Icy Blue", "hex": "#A5F2F3"}},
        {"do": {"name": "Rust", "hex": "#B7410E"}, "dont": {"name": "True Red", "hex": "#C6062F"}},
        {"do": {"name": "Olive", "hex": "#556B2F"}, "dont": {"name": "Emerald", "hex": "#50C878"}},
        {"do": {"name": "Chocolate", "hex": "#7B3F00"}, "dont": {"name": "Black", "hex": "#000000"}},
    ],
    "Spring": [
        {"do": {"name": "Coral", "hex": "#FF7F50"}, "dont": {"name": "Burgundy", "hex": "#800020"}},
        {"do": {"name": "Warm White", "hex": "#FAF9F6"}, "dont": {"name": "Pure White", "hex": "#FFFFFF"}},
        {"do": {"name": "Turquoise", "hex": "#40E0D0"}, "dont": {"name": "Navy", "hex": "#000080"}},
        {"do": {"name": "Peach", "hex": "#FFCBA4"}, "dont": {"name": "Dusty Rose", "hex": "#C9A9A6"}},
        {"do": {"name": "Apple Green", "hex": "#8DB600"}, "dont": {"name": "Forest Green", "hex": "#228B22"}},
        {"do": {"name": "Bright Yellow", "hex": "#FFD700"}, "dont": {"name": "Mustard", "hex": "#FFDB58"}},
    ],
}

# Color family gradients - showing which part of each color family works
# Format: {"family": "name", "gradient": [hex colors from light to dark], "best_range": [start_idx, end_idx]}
# Expanded to 10 colors per gradient for better visualization
SEASON_COLOR_GRADIENTS: Dict[str, List[Dict]] = {
    "Winter": [
        {"family": "Reds & Pinks", "gradient": ["#FFF0F5", "#FFE4E1", "#FFB6C1", "#FF69B4", "#FF1493", "#DC143C", "#C6062F", "#B22222", "#8B0000", "#4A0000"], "best_range": [4, 8], "description": "Deep, blue-based reds and cool pinks"},
        {"family": "Blues", "gradient": ["#F0F8FF", "#E6F3FF", "#B0E0E6", "#87CEEB", "#4169E1", "#0000CD", "#0000AA", "#000080", "#00005F", "#000040"], "best_range": [4, 8], "description": "True blues from royal to navy"},
        {"family": "Greens", "gradient": ["#F0FFF0", "#C8F7C8", "#98FB98", "#50C878", "#3CB371", "#228B22", "#1E7B1E", "#006400", "#004D00", "#003300"], "best_range": [3, 7], "description": "Emerald and jewel greens"},
        {"family": "Purples", "gradient": ["#F8F4FF", "#E6E6FA", "#DDA0DD", "#DA70D6", "#9932CC", "#8B008B", "#673AB7", "#4B0082", "#380062", "#2A004D"], "best_range": [4, 8], "description": "Deep, vivid purples and magentas"},
        {"family": "Neutrals", "gradient": ["#FFFFFF", "#F5F5F5", "#E0E0E0", "#BDBDBD", "#9E9E9E", "#757575", "#616161", "#424242", "#212121", "#000000"], "best_range": [0, 1, 7, 9], "description": "Pure white, charcoal, and true black"},
    ],
    "Summer": [
        {"family": "Pinks & Roses", "gradient": ["#FFF0F5", "#FFE4EC", "#FFD1DC", "#F4C2C2", "#DDA0A0", "#C9A9A6", "#B89B9B", "#A08080", "#8B7070", "#705858"], "best_range": [1, 6], "description": "Soft, dusty pinks and muted roses"},
        {"family": "Blues", "gradient": ["#F0F8FF", "#E8F4F8", "#D6EAF8", "#B0E0E6", "#A8D8EA", "#87CEEB", "#6BB3D9", "#5B9BD5", "#4A88C5", "#3D4F6F"], "best_range": [1, 7], "description": "Soft, muted blues and powder blues"},
        {"family": "Greens", "gradient": ["#F0FFF0", "#E8F5E8", "#D4E8D4", "#C1D9C1", "#A8CCA8", "#9CAF88", "#8DA07A", "#6B8E6B", "#5A7A5A", "#4A6741"], "best_range": [2, 7], "description": "Sage, seafoam and muted greens"},
        {"family": "Purples & Lavenders", "gradient": ["#FAF5FF", "#F3E8FF", "#E8D5F0", "#E0B0FF", "#D4A5E8", "#B57EDC", "#A76BC8", "#9370DB", "#8060C8", "#7B68A0"], "best_range": [1, 7], "description": "Soft lavenders and dusty purples"},
        {"family": "Neutrals", "gradient": ["#FAFAFA", "#F5F5F5", "#EEEEEE", "#E0E0E0", "#C0C0C0", "#A0A0A0", "#808080", "#708090", "#606060", "#4A4A4A"], "best_range": [1, 7], "description": "Soft white to dove gray (avoid stark white/black)"},
    ],
    "Autumn": [
        {"family": "Reds & Rusts", "gradient": ["#FFEEDD", "#FFDAB9", "#F4A460", "#E2725B", "#CD5C5C", "#C04000", "#B7410E", "#A52A2A", "#8B0000", "#5C0000"], "best_range": [2, 8], "description": "Warm rusty reds, terracotta, and brick"},
        {"family": "Oranges & Golds", "gradient": ["#FFF8DC", "#FFEFD5", "#FFD700", "#FFC000", "#E6A800", "#CC8400", "#B8860B", "#996600", "#8B4513", "#6B3000"], "best_range": [1, 8], "description": "Warm golds, mustard, and burnt orange"},
        {"family": "Greens", "gradient": ["#F5F5DC", "#E8E4C9", "#C5C35E", "#9ACD32", "#7CB342", "#6B8E23", "#5D7D1E", "#556B2F", "#4A5F29", "#3D4B2F"], "best_range": [3, 8], "description": "Olive, moss, and forest greens"},
        {"family": "Teals", "gradient": ["#E0FFFF", "#B2DFDB", "#80CBC4", "#4DB6AC", "#26A69A", "#009688", "#00897B", "#00796B", "#006666", "#004D4D"], "best_range": [3, 8], "description": "Warm teals and deep aqua (avoid icy)"},
        {"family": "Browns", "gradient": ["#FFF8DC", "#F5DEB3", "#DEB887", "#D2B48C", "#C19A6B", "#A0826D", "#8B7355", "#7B5B3A", "#5D4037", "#3E2723"], "best_range": [2, 9], "description": "Camel, tan, chocolate, and espresso"},
    ],
    "Spring": [
        {"family": "Corals & Peaches", "gradient": ["#FFF5EE", "#FFECE0", "#FFE4D0", "#FFCBA4", "#FFB088", "#FF9070", "#FF7F50", "#FF6B45", "#FF6347", "#E55B3C"], "best_range": [2, 7], "description": "Warm corals, peaches, and salmon"},
        {"family": "Yellows", "gradient": ["#FFFEF0", "#FFFACD", "#FFF68F", "#FFEC4A", "#FFE135", "#FFD700", "#FFC125", "#FFB90F", "#FFA500", "#FF8C00"], "best_range": [1, 8], "description": "Warm sunny yellows and golden tones"},
        {"family": "Greens", "gradient": ["#F0FFF0", "#E0FFE0", "#C0FFC0", "#98FB98", "#80E080", "#66CD00", "#5DBB63", "#50C850", "#32CD32", "#228B22"], "best_range": [2, 7], "description": "Bright, clear greens and apple green"},
        {"family": "Aquas & Turquoise", "gradient": ["#F0FFFF", "#E0FFFF", "#AFEEEE", "#7FFFD4", "#66CDAA", "#40E0D0", "#20C2B0", "#00CED1", "#00B5B8", "#00A3A3"], "best_range": [2, 7], "description": "Clear aqua and warm turquoise"},
        {"family": "Warm Pinks", "gradient": ["#FFF0F5", "#FFEBEE", "#FFD6E0", "#FFB6C1", "#FFA0B0", "#FF8DA1", "#FF69B4", "#FF5588", "#FF4081", "#F50057"], "best_range": [2, 6], "description": "Warm pinks (avoid cool/blue-based)"},
    ],
}


def get_season_color_categories(season: str) -> Dict[str, List[Dict[str, str]]]:
    """Get organized color categories for palette cards."""
    return SEASON_COLOR_CATEGORIES.get(season, {"neutrals": [], "accents": []})


def get_season_do_dont_pairs(season: str) -> List[Dict]:
    """Get do/don't comparison pairs for a season."""
    return SEASON_DO_DONT_PAIRS.get(season, [])


def get_season_color_gradients(season: str) -> List[Dict]:
    """Get color family gradients for a season."""
    return SEASON_COLOR_GRADIENTS.get(season, [])

