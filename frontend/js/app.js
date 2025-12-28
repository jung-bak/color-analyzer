// Color Analysis Frontend JavaScript

// DOM Elements
const uploadArea = document.getElementById("uploadArea");
const fileInput = document.getElementById("fileInput");
const whiteBalanceToggle = document.getElementById("whiteBalanceToggle");
const loading = document.getElementById("loading");
const errorMessage = document.getElementById("errorMessage");
const errorText = document.getElementById("errorText");
const resultsSection = document.getElementById("resultsSection");
const uploadedImage = document.getElementById("uploadedImage");
const debugSection = document.getElementById("debugSection");

// Check for debug mode in URL (?debug=true or ?debug=1)
function isDebugMode() {
  const urlParams = new URLSearchParams(window.location.search);
  const debugParam = urlParams.get("debug");
  return debugParam === "true" || debugParam === "1";
}

// State
let selectedFile = null;
let currentResult = null; // Store the current analysis result

// Event Listeners
uploadArea.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", handleFileSelect);

// Drag and drop
uploadArea.addEventListener("dragover", (e) => {
  e.preventDefault();
  uploadArea.classList.add("drag-over");
});

uploadArea.addEventListener("dragleave", () => {
  uploadArea.classList.remove("drag-over");
});

uploadArea.addEventListener("drop", (e) => {
  e.preventDefault();
  uploadArea.classList.remove("drag-over");

  const files = e.dataTransfer.files;
  if (files.length > 0) {
    handleFile(files[0]);
  }
});

// Handle File Selection
function handleFileSelect(event) {
  const file = event.target.files[0];
  if (file) {
    handleFile(file);
  }
}

function handleFile(file) {
  // Validate file type
  // Note: HEIC files may have empty or "application/octet-stream" type in some browsers
  const validTypes = ["image/jpeg", "image/jpg", "image/png", "image/heic", "image/heif"];
  const validExtensions = [".jpg", ".jpeg", ".png", ".heic", ".heif"];
  const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf("."));

  const isValidType = validTypes.includes(file.type) ||
                      validExtensions.includes(fileExtension) ||
                      (file.type === "" && validExtensions.includes(fileExtension));

  if (!isValidType) {
    showError("Invalid file type. Please upload a JPG, JPEG, PNG, or HEIC image.");
    return;
  }

  // Validate file size (10MB)
  const maxSize = 10 * 1024 * 1024;
  if (file.size > maxSize) {
    showError("File too large. Maximum size is 10MB.");
    return;
  }

  selectedFile = file;

  // Check if HEIC file (preview not supported in most browsers)
  const isHeic = fileExtension === ".heic" || fileExtension === ".heif";

  if (isHeic) {
    // Show placeholder - server will process the HEIC file
    uploadedImage.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300' viewBox='0 0 300 300'%3E%3Crect fill='%23f3f4f6' width='300' height='300'/%3E%3Ctext x='150' y='140' text-anchor='middle' fill='%236b7280' font-family='system-ui' font-size='16'%3EHEIC Image%3C/text%3E%3Ctext x='150' y='165' text-anchor='middle' fill='%239ca3af' font-family='system-ui' font-size='12'%3EProcessing on server...%3C/text%3E%3C/svg%3E";
  } else {
    const reader = new FileReader();
    reader.onload = (e) => {
      uploadedImage.src = e.target.result;
    };
    reader.readAsDataURL(file);
  }

  // Upload and analyze (server handles HEIC conversion via pillow-heif)
  uploadAndAnalyze(file);
}

// Upload and Analyze Image
async function uploadAndAnalyze(file) {
  // Hide previous results and errors
  hideError();
  hideResults();

  // Show loading
  showLoading();

  try {
    // Prepare form data
    const formData = new FormData();
    formData.append("file", file);

    // Get white balance preference
    const applyWhiteBalance = whiteBalanceToggle.checked;

    // Get debug mode from URL parameter
    const debugMode = isDebugMode();

    // Make API request
    const response = await fetch(
      `/api/analyze?white_balance=${applyWhiteBalance}&debug=${debugMode}`,
      {
        method: "POST",
        body: formData,
      },
    );

    hideLoading();

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Analysis failed");
    }

    const result = await response.json();
    displayResults(result);
  } catch (error) {
    hideLoading();
    showError(
      error.message || "An error occurred during analysis. Please try again.",
    );
  }
}

// Display Results
function displayResults(result) {
  // Store result for later use
  currentResult = result;

  // Update image preview if server provided one (useful for HEIC files)
  if (result.image_preview) {
    uploadedImage.src = result.image_preview;
  }

  // Show results section
  resultsSection.style.display = "block";
  resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });

  // Season Name
  document.getElementById("seasonName").textContent = result.full_season_name;
  document.getElementById("seasonDescription").textContent =
    result.description.description;

  // Season Probability Breakdown
  if (result.season_probabilities) {
    displaySeasonProbabilities(result.season_probabilities, result.season);
  }

  // White Balance Method
  const wbMethodText = {
    background: "Background-Based Method",
    skin_locus: "Skin Tone Method",
    none: "No White Balance Applied",
  };
  document.getElementById("wbMethod").textContent =
    wbMethodText[result.white_balance_method] || result.white_balance_method;

  // Skin Tone
  const [r, g, b] = result.skin_tone_rgb;
  const skinToneRgb = `rgb(${r}, ${g}, ${b})`;
  document.getElementById("skinToneSwatch").style.backgroundColor = skinToneRgb;
  document.getElementById("skinToneRgb").textContent =
    `RGB: (${r}, ${g}, ${b})`;

  // Render new color visualizations
  renderDrapingSimulation(skinToneRgb, result.color_categories);
  renderPaletteCards(result.color_categories);
  renderDoDontGrid(result.do_dont_pairs);
  renderGradientBars(result.color_gradients);

  // Recommendations
  const recommendationsContainer = document.getElementById(
    "recommendationsContent",
  );
  recommendationsContainer.innerHTML = `
        <div class="recommendation-item">
            <strong>Characteristics:</strong> ${result.description.characteristics}
        </div>
        <div class="recommendation-item">
            <strong>Best Colors:</strong> ${result.description.best_colors}
        </div>
        <div class="recommendation-item">
            <strong>Avoid:</strong> ${result.description.avoid}
        </div>
        <div class="recommendation-item">
            <strong>Best Metals:</strong> ${result.description.metals}
        </div>
        <div class="recommendation-item">
            <strong>Tips:</strong> ${result.description.tips}
        </div>
    `;

  // Technical Details
  const detailsContainer = document.getElementById("detailsContent");
  const analysis = result.analysis;

  detailsContainer.innerHTML = `
        <div class="detail-item">
            <span class="detail-label">Classification:</span>
            <span class="detail-value">${analysis.temperature_category} + ${analysis.lightness_category}</span>
        </div>
        <div class="detail-item">
            <span class="detail-label">L* (Lightness):</span>
            <span class="detail-value">${analysis.lab_values.L.toFixed(2)} (threshold: ${analysis.thresholds.lightness})</span>
        </div>
        <div class="detail-item">
            <span class="detail-label">a* (Green-Red):</span>
            <span class="detail-value">${analysis.lab_values.a.toFixed(2)}</span>
        </div>
        <div class="detail-item">
            <span class="detail-label">b* (Blue-Yellow):</span>
            <span class="detail-value">${analysis.lab_values.b.toFixed(2)} (threshold: ${analysis.thresholds.warmth})</span>
        </div>
        <div class="detail-item">
            <span class="detail-label">Lightness Distance:</span>
            <span class="detail-value">${analysis.lightness_distance.toFixed(2)}</span>
        </div>
        <div class="detail-item">
            <span class="detail-label">Warmth Distance:</span>
            <span class="detail-value">${analysis.warmth_distance.toFixed(2)}</span>
        </div>
    `;

  // Add white balance metadata if available
  if (
    result.white_balance_metadata &&
    Object.keys(result.white_balance_metadata).length > 0
  ) {
    const wbMetadata = result.white_balance_metadata;

    if (
      result.white_balance_method === "background" &&
      wbMetadata.background_percentage
    ) {
      detailsContainer.innerHTML += `
                <div class="detail-item">
                    <span class="detail-label">Background Percentage:</span>
                    <span class="detail-value">${wbMetadata.background_percentage.toFixed(1)}%</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Background Variance:</span>
                    <span class="detail-value">${wbMetadata.background_variance.toFixed(2)}</span>
                </div>
            `;
    }

    if (
      result.white_balance_method === "skin_locus" &&
      wbMetadata.g_offset !== undefined
    ) {
      detailsContainer.innerHTML += `
                <div class="detail-item">
                    <span class="detail-label">Chromaticity Offset:</span>
                    <span class="detail-value">${wbMetadata.g_offset.toFixed(4)}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Correction Factor:</span>
                    <span class="detail-value">${wbMetadata.correction_factor.toFixed(4)}</span>
                </div>
            `;
    }
  }

  // Display debug data if available
  if (result.debug_data) {
    displayDebugData(result.debug_data);
  } else {
    // Hide debug section if no debug data
    debugSection.style.display = "none";
  }
}

// Display Debug Data
function displayDebugData(debugData) {
  // Show debug section
  debugSection.style.display = "block";

  // Display debug images
  const debugImagesGrid = document.getElementById("debugImagesGrid");
  debugImagesGrid.innerHTML = "";

  if (debugData.images && debugData.images.length > 0) {
    debugData.images.forEach((imageData) => {
      const card = document.createElement("div");
      card.className = "debug-image-card";

      const img = document.createElement("img");
      img.src = imageData.image_base64;
      img.alt = imageData.title;
      img.loading = "lazy";

      // Add click to zoom
      img.addEventListener("click", () =>
        showDebugImageModal(imageData.image_base64, imageData.title),
      );

      const info = document.createElement("div");
      info.className = "debug-image-info";

      const title = document.createElement("div");
      title.className = "debug-image-title";
      title.textContent = imageData.title;

      const description = document.createElement("div");
      description.className = "debug-image-description";
      description.textContent = imageData.description;

      info.appendChild(title);
      info.appendChild(description);

      card.appendChild(img);
      card.appendChild(info);

      debugImagesGrid.appendChild(card);
    });
  }

  // Display debug metadata
  if (debugData.metadata) {
    const metadata = debugData.metadata;

    // Face Detection Metadata
    if (metadata.face_detection) {
      const faceDetectionCard = document.getElementById(
        "debugMetaFaceDetection",
      );
      const faceDetectionContent = document.getElementById(
        "debugMetaFaceDetectionContent",
      );
      faceDetectionCard.style.display = "block";
      faceDetectionContent.innerHTML = formatMetadata(metadata.face_detection);
    }

    // Skin Extraction Metadata
    if (metadata.skin_extraction) {
      const skinExtractionCard = document.getElementById(
        "debugMetaSkinExtraction",
      );
      const skinExtractionContent = document.getElementById(
        "debugMetaSkinExtractionContent",
      );
      skinExtractionCard.style.display = "block";
      skinExtractionContent.innerHTML = formatMetadata(
        metadata.skin_extraction,
      );
    }

    // White Balance Metadata
    if (metadata.white_balance) {
      const whiteBalanceCard = document.getElementById("debugMetaWhiteBalance");
      const whiteBalanceContent = document.getElementById(
        "debugMetaWhiteBalanceContent",
      );
      whiteBalanceCard.style.display = "block";
      whiteBalanceContent.innerHTML = formatMetadata(metadata.white_balance);
    }

    // Color Analysis Metadata
    if (metadata.color_analysis) {
      const colorAnalysisCard = document.getElementById(
        "debugMetaColorAnalysis",
      );
      const colorAnalysisContent = document.getElementById(
        "debugMetaColorAnalysisContent",
      );
      colorAnalysisCard.style.display = "block";
      colorAnalysisContent.innerHTML = formatColorAnalysisMetadata(
        metadata.color_analysis,
      );
    }
  }
}

// Display Season Probability Breakdown
function displaySeasonProbabilities(probabilities, currentSeason) {
  const probabilityBarsContainer = document.getElementById("probabilityBars");
  probabilityBarsContainer.innerHTML = "";

  // Convert to array and sort by probability (highest first)
  const probabilitiesArray = Object.entries(probabilities)
    .map(([season, percentage]) => ({
      season,
      percentage,
    }))
    .sort((a, b) => b.percentage - a.percentage);

  // Create bar for each season
  probabilitiesArray.forEach(({ season, percentage }) => {
    const barItem = document.createElement("div");
    barItem.className = "probability-bar-item";

    const label = document.createElement("div");
    label.className = `season-label ${season.toLowerCase()}`;
    label.textContent = season;

    const track = document.createElement("div");
    track.className = "probability-bar-track";

    const fill = document.createElement("div");
    fill.className = `probability-bar-fill ${season.toLowerCase()}`;
    fill.style.width = `${percentage}%`;

    // Only show percentage inside bar if it's wide enough
    if (percentage > 15) {
      fill.textContent = `${percentage.toFixed(1)}%`;
    }

    track.appendChild(fill);

    const percentageLabel = document.createElement("div");
    percentageLabel.className = "probability-percentage";
    percentageLabel.textContent = `${percentage.toFixed(1)}%`;

    barItem.appendChild(label);
    barItem.appendChild(track);
    barItem.appendChild(percentageLabel);

    probabilityBarsContainer.appendChild(barItem);
  });
}

// Format metadata as HTML
function formatMetadata(metadata) {
  let html = "";
  for (const [key, value] of Object.entries(metadata)) {
    html += `
            <div class="debug-meta-item">
                <span class="debug-meta-key">${formatKey(key)}:</span>
                <span class="debug-meta-value">${formatValue(value)}</span>
            </div>
        `;
  }
  return html;
}

// Format color analysis metadata with decision indicators
function formatColorAnalysisMetadata(metadata) {
  let html = "";

  // LAB values
  html += `
        <div class="debug-meta-item">
            <span class="debug-meta-key">L* (Lightness):</span>
            <span class="debug-meta-value">${metadata.L_value?.toFixed(2) || "N/A"}</span>
        </div>
        <div class="debug-meta-item">
            <span class="debug-meta-key">a* (Green-Red):</span>
            <span class="debug-meta-value">${metadata.a_value?.toFixed(2) || "N/A"}</span>
        </div>
        <div class="debug-meta-item">
            <span class="debug-meta-key">b* (Blue-Yellow):</span>
            <span class="debug-meta-value">${metadata.b_value?.toFixed(2) || "N/A"}</span>
        </div>
    `;

  // Decisions with indicators
  if (metadata.warm_threshold !== undefined) {
    const warmDecision = metadata.is_warm ? "Warm" : "Cool";
    const warmClass = metadata.is_warm ? "warning" : "pass";
    html += `
            <div class="debug-meta-item">
                <span class="debug-meta-key">Warm Threshold:</span>
                <span class="debug-meta-value">${metadata.warm_threshold}</span>
            </div>
            <div class="debug-meta-item">
                <span class="debug-meta-key">Undertone:</span>
                <span class="debug-decision ${warmClass}">${warmDecision}</span>
            </div>
        `;
  }

  if (metadata.light_threshold !== undefined) {
    const lightDecision = metadata.is_light ? "Light" : "Deep";
    const lightClass = metadata.is_light ? "pass" : "warning";
    html += `
            <div class="debug-meta-item">
                <span class="debug-meta-key">Light Threshold:</span>
                <span class="debug-meta-value">${metadata.light_threshold}</span>
            </div>
            <div class="debug-meta-item">
                <span class="debug-meta-key">Depth:</span>
                <span class="debug-decision ${lightClass}">${lightDecision}</span>
            </div>
        `;
  }

  // Final season
  if (metadata.season_determined) {
    html += `
            <div class="debug-meta-item">
                <span class="debug-meta-key">Season:</span>
                <span class="debug-decision pass">${metadata.season_determined}</span>
            </div>
            <div class="debug-meta-item">
                <span class="debug-meta-key">Confidence:</span>
                <span class="debug-meta-value">${metadata.confidence?.toFixed(1)}%</span>
            </div>
        `;
  }

  return html;
}

// Format key for display
function formatKey(key) {
  return key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
}

// Format value for display
function formatValue(value) {
  if (Array.isArray(value)) {
    if (value.length <= 3) {
      return `[${value.map((v) => (typeof v === "number" ? v.toFixed(2) : v)).join(", ")}]`;
    }
    return `[${value.length} items]`;
  }
  if (typeof value === "number") {
    return value.toFixed(2);
  }
  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }
  return String(value);
}

// Show debug image modal
function showDebugImageModal(imageSrc, title) {
  // Create modal if it doesn't exist
  let modal = document.getElementById("debugImageModal");
  if (!modal) {
    modal = document.createElement("div");
    modal.id = "debugImageModal";
    modal.className = "debug-image-modal";
    modal.innerHTML = '<img alt="Debug Image">';
    document.body.appendChild(modal);

    modal.addEventListener("click", () => {
      modal.classList.remove("show");
    });
  }

  const img = modal.querySelector("img");
  img.src = imageSrc;
  img.alt = title;
  modal.classList.add("show");
}

// Utility Functions
function showLoading() {
  loading.style.display = "block";
}

function hideLoading() {
  loading.style.display = "none";
}

function showError(message) {
  errorText.textContent = message;
  errorMessage.style.display = "flex";
}

function hideError() {
  errorMessage.style.display = "none";
}

function hideResults() {
  resultsSection.style.display = "none";
}

// Check if device is mobile/touch device
function isMobileDevice() {
  return (
    "ontouchstart" in window ||
    navigator.maxTouchPoints > 0 ||
    window.innerWidth <= 768
  );
}

function copyToClipboard(text) {
  // Disable copy on mobile devices to improve UX
  if (isMobileDevice()) {
    return;
  }

  navigator.clipboard
    .writeText(text)
    .then(() => {
      // Show temporary feedback
      const notification = document.createElement("div");
      notification.textContent = `Copied ${text}!`;
      notification.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #10b981;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;
      document.body.appendChild(notification);

      setTimeout(() => {
        notification.style.animation = "slideOut 0.3s ease";
        setTimeout(() => notification.remove(), 300);
      }, 2000);
    })
    .catch((err) => {
      console.error("Failed to copy:", err);
    });
}

// Color Wheel Functions
// ============================================
// NEW COLOR VISUALIZATION FUNCTIONS
// ============================================

// 1. DRAPING SIMULATION - Show colors next to skin tone
function renderDrapingSimulation(skinToneRgb, colorCategories) {
  // Set up the large skin swatch
  const largeSkin = document.getElementById("drapingLargeSkin");
  largeSkin.style.backgroundColor = skinToneRgb;

  // Set up the color preview area
  const largeColor = document.getElementById("drapingLargeColor");
  const colorName = document.getElementById("drapingColorName");

  // Get both grids
  const recommendedGrid = document.getElementById("drapingColorGrid");
  const avoidGrid = document.getElementById("drapingAvoidGrid");
  recommendedGrid.innerHTML = "";
  avoidGrid.innerHTML = "";

  // Prepare color arrays
  const recommendedColors = [
    ...(colorCategories.neutrals || []),
    ...(colorCategories.accents || []),
  ];
  const avoidColors = colorCategories.avoid || [];

  let selectedOption = null;

  // Helper function to create a color option element
  function createColorOption(color, isAvoid = false) {
    const option = document.createElement("div");
    option.className = "draping-color-option" + (isAvoid ? " avoid-option" : "");
    option.style.backgroundColor = color.hex;
    option.innerHTML = `<span>${color.name}</span>`;
    option.title = `${color.name} - ${color.hex}`;

    // Hover to preview
    option.addEventListener("mouseenter", () => {
      largeColor.style.backgroundColor = color.hex;
      largeColor.classList.toggle("avoid-preview", isAvoid);
      colorName.textContent = isAvoid ? `${color.name} (Avoid)` : color.name;
    });

    // Click to select
    option.addEventListener("click", () => {
      // Update selection styling
      if (selectedOption) {
        selectedOption.classList.remove("selected");
      }
      option.classList.add("selected");
      selectedOption = option;

      // Update preview
      largeColor.style.backgroundColor = color.hex;
      largeColor.classList.toggle("avoid-preview", isAvoid);
      colorName.textContent = isAvoid ? `${color.name} (Avoid)` : color.name;
    });

    return option;
  }

  // Populate recommended colors grid
  recommendedColors.forEach((color, index) => {
    const option = createColorOption(color, false);
    recommendedGrid.appendChild(option);

    // Select the first color by default
    if (index === 0) {
      largeColor.style.backgroundColor = color.hex;
      largeColor.classList.remove("avoid-preview");
      colorName.textContent = color.name;
      option.classList.add("selected");
      selectedOption = option;
    }
  });

  // Populate avoid colors grid
  avoidColors.forEach((color) => {
    const option = createColorOption(color, true);
    avoidGrid.appendChild(option);
  });
}

// 2. PALETTE CARDS - Organized by category
function renderPaletteCards(colorCategories) {
  // Neutrals
  const neutralsContainer = document.getElementById("neutralsSwatches");
  neutralsContainer.innerHTML = "";

  const neutrals = colorCategories.neutrals || [];
  neutrals.forEach((color) => {
    const item = createPaletteSwatchItem(color);
    neutralsContainer.appendChild(item);
  });

  // Accents
  const accentsContainer = document.getElementById("accentsSwatches");
  accentsContainer.innerHTML = "";

  const accents = colorCategories.accents || [];
  accents.forEach((color) => {
    const item = createPaletteSwatchItem(color);
    accentsContainer.appendChild(item);
  });

  // Avoid
  const avoidContainer = document.getElementById("avoidSwatches");
  avoidContainer.innerHTML = "";

  const avoid = colorCategories.avoid || [];
  avoid.forEach((color) => {
    const item = createPaletteSwatchItem(color, true);
    avoidContainer.appendChild(item);
  });
}

function createPaletteSwatchItem(color, isAvoid = false) {
  const item = document.createElement("div");
  item.className = "palette-swatch-item";
  item.innerHTML = `
        <div class="palette-mini-swatch" style="background-color: ${color.hex}"></div>
        <div class="palette-color-info">
            <span class="palette-color-name">${color.name}</span>
            <span class="palette-color-hex">${color.hex}</span>
        </div>
    `;
  item.title = isAvoid ? `Avoid: ${color.name}` : color.name;
  return item;
}

// 3. DO/DON'T COMPARISON GRID
function renderDoDontGrid(pairs) {
  const container = document.getElementById("dodontGrid");
  container.innerHTML = "";

  pairs.forEach((pair) => {
    const pairDiv = document.createElement("div");
    pairDiv.className = "dodont-pair";

    // DO side
    const doItem = document.createElement("div");
    doItem.className = "dodont-item do-item";
    doItem.innerHTML = `
            <div class="dodont-swatch" style="background-color: ${pair.do.hex}"></div>
            <div class="dodont-info">
                <span class="dodont-label">✓ Wear This</span>
                <span class="dodont-name">${pair.do.name}</span>
                <span class="dodont-hex">${pair.do.hex}</span>
            </div>
        `;

    // VS divider
    const vsDiv = document.createElement("div");
    vsDiv.className = "dodont-vs";
    vsDiv.textContent = "VS";

    // DON'T side
    const dontItem = document.createElement("div");
    dontItem.className = "dodont-item dont-item";
    dontItem.innerHTML = `
            <div class="dodont-swatch" style="background-color: ${pair.dont.hex}"></div>
            <div class="dodont-info">
                <span class="dodont-label">✗ Avoid This</span>
                <span class="dodont-name">${pair.dont.name}</span>
                <span class="dodont-hex">${pair.dont.hex}</span>
            </div>
        `;

    pairDiv.appendChild(doItem);
    pairDiv.appendChild(vsDiv);
    pairDiv.appendChild(dontItem);
    container.appendChild(pairDiv);
  });
}

// 4. GRADIENT BARS - Show range within color families
function renderGradientBars(gradients) {
  const container = document.getElementById("gradientBars");
  container.innerHTML = "";

  gradients.forEach((gradient) => {
    const barItem = document.createElement("div");
    barItem.className = "gradient-bar-item";

    // Header
    const header = document.createElement("div");
    header.className = "gradient-bar-header";
    header.innerHTML = `
            <span class="gradient-family">${gradient.family}</span>
            <span class="gradient-description">${gradient.description}</span>
        `;
    barItem.appendChild(header);

    // Wrapper for positioning
    const wrapper = document.createElement("div");
    wrapper.className = "gradient-bar-wrapper";

    // Track with segments
    const track = document.createElement("div");
    track.className = "gradient-bar-track";

    // Handle multiple ranges (e.g., [0, 1, 7, 9] = range 0-1 AND range 7-9)
    const ranges = [];
    const bestRange = gradient.best_range;
    if (bestRange.length === 4) {
      // Two separate ranges
      ranges.push([bestRange[0], bestRange[1]]);
      ranges.push([bestRange[2], bestRange[3]]);
    } else {
      // Single range
      ranges.push([bestRange[0], bestRange[1]]);
    }

    const totalSegments = gradient.gradient.length;

    // Check if index is in any of the ranges
    const isInRange = (index) => {
      return ranges.some(([start, end]) => index >= start && index <= end);
    };

    gradient.gradient.forEach((hex, index) => {
      const segment = document.createElement("div");
      segment.className = "gradient-segment";
      segment.style.backgroundColor = hex;

      // Mark if in any of the "best ranges"
      if (isInRange(index)) {
        segment.classList.add("in-range");
      } else {
        segment.classList.add("out-of-range");
      }

      segment.title = hex;

      track.appendChild(segment);
    });

    wrapper.appendChild(track);

    // Add highlight boxes for each range
    const segmentWidth = 100 / totalSegments;

    ranges.forEach((range, rangeIndex) => {
      const [rangeStart, rangeEnd] = range;
      const highlightLeft = rangeStart * segmentWidth;
      const highlightWidth = (rangeEnd - rangeStart + 1) * segmentWidth;

      // Add range highlight box
      const highlight = document.createElement("div");
      highlight.className = "gradient-range-highlight";
      highlight.style.left = `${highlightLeft}%`;
      highlight.style.width = `${highlightWidth}%`;

      // Add "YOUR RANGE" label (only on first range, or custom label for multiple)
      const label = document.createElement("div");
      label.className = "gradient-range-label";
      if (ranges.length > 1) {
        label.textContent = rangeIndex === 0 ? "✓ LIGHT" : "✓ DARK";
      } else {
        label.textContent = "✓ YOUR RANGE";
      }
      highlight.appendChild(label);

      // Add start marker
      const startMarker = document.createElement("div");
      startMarker.className = "gradient-range-start";
      highlight.appendChild(startMarker);

      // Add end marker
      const endMarker = document.createElement("div");
      endMarker.className = "gradient-range-end";
      highlight.appendChild(endMarker);

      wrapper.appendChild(highlight);
    });

    barItem.appendChild(wrapper);
    container.appendChild(barItem);
  });
}

// ============================================
// LEGACY COLOR WHEEL CODE (kept for reference but not used)
// ============================================

// Season-specific color characteristics
const SEASON_COLOR_SETTINGS = {
  Winter: { saturation: 85, lightness: 45 }, // High saturation, deeper - jewel tones
  Summer: { saturation: 45, lightness: 70 }, // Low saturation, lighter - soft pastels
  Autumn: { saturation: 70, lightness: 40 }, // Medium-high saturation, deeper - earth tones
  Spring: { saturation: 80, lightness: 55 }, // High saturation, medium - clear brights
};

function drawColorWheel(safeZones, avoidZones, season) {
  const colorSettings =
    SEASON_COLOR_SETTINGS[season] || SEASON_COLOR_SETTINGS.Winter;

  // Draw safe colors wheel
  drawSafeColorsWheel(safeZones, colorSettings, season);

  // Draw avoid colors wheel
  drawAvoidColorsWheel(avoidZones, colorSettings);
}

function drawSafeColorsWheel(safeZones, colorSettings, season) {
  const canvas = document.getElementById("colorWheelSafe");
  const ctx = canvas.getContext("2d");
  const centerX = canvas.width / 2;
  const centerY = canvas.height / 2;
  const radius = 160;
  const { saturation, lightness } = colorSettings;

  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw grey background for entire wheel
  for (let angle = 0; angle < 360; angle++) {
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    const startAngle = ((angle - 90) * Math.PI) / 180;
    const endAngle = ((angle - 89) * Math.PI) / 180;
    ctx.arc(centerX, centerY, radius, startAngle, endAngle);
    ctx.closePath();
    ctx.fillStyle = "#e5e7eb";
    ctx.fill();
  }

  // Draw only the safe color zones with season-appropriate saturation/lightness
  safeZones.forEach((zone) => {
    for (let angle = zone.start; angle <= zone.end; angle++) {
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      const startAngle = ((angle - 90) * Math.PI) / 180;
      const endAngle = ((angle - 89) * Math.PI) / 180;
      ctx.arc(centerX, centerY, radius, startAngle, endAngle);
      ctx.closePath();
      ctx.fillStyle = `hsl(${angle}, ${saturation}%, ${lightness}%)`;
      ctx.fill();
    }
  });

  // Add interactivity with season info
  setupWheelInteractivity(canvas, safeZones, [], "safe", colorSettings);
}

function drawAvoidColorsWheel(avoidZones, colorSettings) {
  const canvas = document.getElementById("colorWheelAvoid");
  const ctx = canvas.getContext("2d");
  const centerX = canvas.width / 2;
  const centerY = canvas.height / 2;
  const radius = 160;
  const { saturation, lightness } = colorSettings;

  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw grey background for entire wheel
  for (let angle = 0; angle < 360; angle++) {
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    const startAngle = ((angle - 90) * Math.PI) / 180;
    const endAngle = ((angle - 89) * Math.PI) / 180;
    ctx.arc(centerX, centerY, radius, startAngle, endAngle);
    ctx.closePath();
    ctx.fillStyle = "#e5e7eb";
    ctx.fill();
  }

  // Draw only the avoid color zones with season-appropriate saturation/lightness
  avoidZones.forEach((zone) => {
    for (let angle = zone.start; angle <= zone.end; angle++) {
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      const startAngle = ((angle - 90) * Math.PI) / 180;
      const endAngle = ((angle - 89) * Math.PI) / 180;
      ctx.arc(centerX, centerY, radius, startAngle, endAngle);
      ctx.closePath();
      ctx.fillStyle = `hsl(${angle}, ${saturation}%, ${lightness}%)`;
      ctx.fill();
    }
  });

  // Add interactivity with season info
  setupWheelInteractivity(canvas, [], avoidZones, "avoid", colorSettings);
}

function setupWheelInteractivity(
  canvas,
  safeZones,
  avoidZones,
  wheelType,
  colorSettings,
) {
  const tooltip = document.getElementById("colorWheelTooltip");
  const colorZoom = document.getElementById("colorZoom");
  const zoomSwatch = document.getElementById("zoomSwatch");
  const zoomHex = document.getElementById("zoomHex");
  const zoomRgb = document.getElementById("zoomRgb");
  const zoomHsl = document.getElementById("zoomHsl");
  const radius = 160;
  const ctx = canvas.getContext("2d");

  canvas.addEventListener("mousemove", (e) => {
    const rect = canvas.getBoundingClientRect();
    // Scale mouse coordinates to canvas coordinate space
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const x = Math.floor((e.clientX - rect.left) * scaleX);
    const y = Math.floor((e.clientY - rect.top) * scaleY);

    // Check if mouse is within the wheel radius
    const dx = x - canvas.width / 2;
    const dy = y - canvas.height / 2;
    const distance = Math.sqrt(dx * dx + dy * dy);

    if (distance <= radius) {
      // Get the actual pixel color from the canvas
      const pixelData = ctx.getImageData(x, y, 1, 1).data;
      const r = pixelData[0];
      const g = pixelData[1];
      const b = pixelData[2];

      // Check if it's a colored pixel (not grey background)
      const isColored = !(r === g && g === b && r >= 220); // Grey background check

      if (isColored && (r > 0 || g > 0 || b > 0)) {
        // Calculate hue from the actual pixel color
        const hsl = rgbToHsl(r, g, b);
        const hue = Math.round(hsl.h);

        // Find if in any zone
        const zone = findZone(hue, safeZones, avoidZones);

        if (zone) {
          // Show category tooltip
          tooltip.textContent = `${zone.name} - ${zone.category}`;
          tooltip.style.left = `${e.clientX + 10}px`;
          tooltip.style.top = `${e.clientY - 30}px`;
          tooltip.classList.add("show");
        }

        // Show color zoom with values
        const hexColor = rgbToHex(r, g, b);
        const rgbColor = `rgb(${r}, ${g}, ${b})`;

        zoomSwatch.style.backgroundColor = rgbColor;
        zoomHex.textContent = `HEX: ${hexColor}`;
        zoomRgb.textContent = `RGB: ${r}, ${g}, ${b}`;
        zoomHsl.textContent = `HSL: ${hue}°, ${Math.round(hsl.s)}%, ${Math.round(hsl.l)}%`;

        // Position the zoom popup
        const zoomX =
          e.clientX + 220 > window.innerWidth
            ? e.clientX - 230
            : e.clientX + 20;
        const zoomY =
          e.clientY + 200 > window.innerHeight
            ? e.clientY - 180
            : e.clientY + 20;

        colorZoom.style.left = `${zoomX}px`;
        colorZoom.style.top = `${zoomY}px`;
        colorZoom.classList.add("show");
      } else {
        tooltip.classList.remove("show");
        colorZoom.classList.remove("show");
      }
    } else {
      tooltip.classList.remove("show");
      colorZoom.classList.remove("show");
    }
  });

  canvas.addEventListener("mouseleave", () => {
    tooltip.classList.remove("show");
    colorZoom.classList.remove("show");
  });

  canvas.addEventListener("click", (e) => {
    const rect = canvas.getBoundingClientRect();
    // Scale mouse coordinates to canvas coordinate space
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const x = Math.floor((e.clientX - rect.left) * scaleX);
    const y = Math.floor((e.clientY - rect.top) * scaleY);

    // Check if click is within the wheel
    const dx = x - canvas.width / 2;
    const dy = y - canvas.height / 2;
    const distance = Math.sqrt(dx * dx + dy * dy);

    if (distance <= radius) {
      // Get the actual pixel color from the canvas
      const pixelData = ctx.getImageData(x, y, 1, 1).data;
      const r = pixelData[0];
      const g = pixelData[1];
      const b = pixelData[2];

      // Check if it's a colored pixel (not grey background)
      const isColored = !(r === g && g === b && r >= 220);

      if (isColored && (r > 0 || g > 0 || b > 0)) {
        // Calculate hue from the actual pixel color
        const hsl = rgbToHsl(r, g, b);
        const hue = Math.round(hsl.h);
        const zone = findZone(hue, safeZones, avoidZones);

        // Hide zoom popup on click
        if (zone) {
          colorZoom.classList.remove("show");
          tooltip.classList.remove("show");
        }
      }
    }
  });
}

function getHueFromPosition(x, y, cx, cy) {
  const dx = x - cx;
  const dy = y - cy;
  let angle = (Math.atan2(dy, dx) * 180) / Math.PI + 90;
  if (angle < 0) angle += 360;
  return Math.round(angle);
}

function findZone(hue, safeZones, avoidZones) {
  for (const zone of safeZones) {
    if (hue >= zone.start && hue <= zone.end) return zone;
  }
  for (const zone of avoidZones) {
    if (hue >= zone.start && hue <= zone.end) return zone;
  }
  return null;
}

// Color conversion utilities
function hslToRgb(h, s, l) {
  s /= 100;
  l /= 100;

  const c = (1 - Math.abs(2 * l - 1)) * s;
  const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
  const m = l - c / 2;

  let r = 0,
    g = 0,
    b = 0;

  if (0 <= h && h < 60) {
    r = c;
    g = x;
    b = 0;
  } else if (60 <= h && h < 120) {
    r = x;
    g = c;
    b = 0;
  } else if (120 <= h && h < 180) {
    r = 0;
    g = c;
    b = x;
  } else if (180 <= h && h < 240) {
    r = 0;
    g = x;
    b = c;
  } else if (240 <= h && h < 300) {
    r = x;
    g = 0;
    b = c;
  } else if (300 <= h && h < 360) {
    r = c;
    g = 0;
    b = x;
  }

  r = Math.round((r + m) * 255);
  g = Math.round((g + m) * 255);
  b = Math.round((b + m) * 255);

  return { r, g, b };
}

function rgbToHex(r, g, b) {
  const toHex = (n) => {
    const hex = n.toString(16);
    return hex.length === 1 ? "0" + hex : hex;
  };
  return `#${toHex(r)}${toHex(g)}${toHex(b)}`.toUpperCase();
}

function rgbToHsl(r, g, b) {
  r /= 255;
  g /= 255;
  b /= 255;

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  let h,
    s,
    l = (max + min) / 2;

  if (max === min) {
    h = s = 0; // achromatic
  } else {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);

    switch (max) {
      case r:
        h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
        break;
      case g:
        h = ((b - r) / d + 2) / 6;
        break;
      case b:
        h = ((r - g) / d + 4) / 6;
        break;
    }
  }

  return {
    h: h * 360,
    s: s * 100,
    l: l * 100,
  };
}

// Add animations
const style = document.createElement("style");
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
