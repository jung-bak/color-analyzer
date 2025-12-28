# 🎨 Personal Color Analysis

An intelligent web application that analyzes face photos to determine your seasonal color palette using computer vision and color theory. Built with FastAPI, MediaPipe, and vanilla JavaScript.

> 🚀 **Now using `uv`** - the blazingly fast Python package installer (10-100x faster than pip!)  
> See [UV_BENEFITS.md](UV_BENEFITS.md) for details.

## ✨ Features

- **Intelligent Face Detection**: Uses MediaPipe Face Mesh to detect 468 facial landmarks
- **Dual-Mode White Balance Correction**:
  - Background-based method for photos with neutral backgrounds
  - Skin Locus method for cluttered backgrounds (scientifically validated)
- **CIELAB Color Space Analysis**: Precise skin tone analysis using professional color space
- **Season Classification**: Determines if you're Winter, Summer, Autumn, or Spring
- **Beautiful UI**: Modern, responsive design with smooth animations
- **Detailed Analysis**: View technical metrics, confidence scores, and LAB values
- **Color Palettes**: Get personalized color recommendations with hex codes

## 🔬 How It Works

### 1. Face Detection & Landmark Mapping
MediaPipe's Face Mesh detects 468 precise points on your face, allowing us to isolate the cheek region for accurate skin tone extraction while avoiding eyes, lips, and shadows.

### 2. Intelligent White Balance Correction

**Background Method** (Primary):
- Segments person from background using MediaPipe Selfie Segmentation
- Uses neutral background pixels as reference for lighting correction
- Ideal for photos with plain walls or neutral backgrounds

**Skin Locus Method** (Fallback):
- Uses the scientific fact that human skin tones cluster in a specific area of the chromaticity diagram
- Works regardless of ethnicity or background
- Applied automatically when background is insufficient or non-neutral

### 3. CIELAB Color Space Analysis
- **L\* (Lightness)**: Determines Light vs Deep coloring
- **b\* (Blue-Yellow axis)**: Determines Cool vs Warm undertones

### 4. Season Classification
- **Winter**: Cool + Deep (L\* ≤ 155, b\* ≤ 132)
- **Summer**: Cool + Light (L\* > 155, b\* ≤ 132)
- **Autumn**: Warm + Deep (L\* ≤ 155, b\* > 132)
- **Spring**: Warm + Light (L\* > 155, b\* > 132)

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- uv (Python package installer)

### Installation

1. **Clone or download the repository**

```bash
cd color_analyzer
```

2. **Install uv (if not already installed)**

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Mac/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Or with pip:**
```bash
pip install uv
```

3. **Install dependencies**

```bash
uv sync
```

This automatically creates a virtual environment and installs all dependencies.

4. **Run the application**

```bash
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Or use the convenience scripts:
- Windows: `run.bat`
- Mac/Linux: `./run.sh`

4. **Open your browser**

Navigate to: http://localhost:8000

## 📁 Project Structure

```
color_analyzer/
├── backend/
│   ├── main.py                    # FastAPI application entry point
│   ├── api/
│   │   └── routes.py              # API endpoints
│   ├── core/
│   │   ├── config.py              # Configuration settings
│   │   └── palettes.py            # Seasonal color palettes
│   ├── services/
│   │   ├── face_analyzer.py       # Face detection & skin extraction
│   │   ├── color_processor.py     # White balance & color conversion
│   │   └── season_classifier.py   # Season determination logic
│   └── models/
│       └── schemas.py             # Pydantic models
├── frontend/
│   ├── index.html                 # Main HTML page
│   ├── css/
│   │   └── style.css              # Styles
│   └── js/
│       └── app.js                 # Frontend logic
├── requirements.txt               # Python dependencies
├── .gitignore                     # Git ignore file
└── README.md                      # This file
```

## 🌐 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints

#### `POST /api/analyze`
Analyze an uploaded image to determine seasonal color palette.

**Parameters:**
- `file`: Image file (multipart/form-data)
- `white_balance`: Boolean query parameter (default: true)

**Response:**
```json
{
  "season": "Winter",
  "full_season_name": "Winter (Cool & Deep)",
  "confidence": 87.5,
  "skin_tone_rgb": [180, 140, 120],
  "lab_values": {
    "L": 145.2,
    "a": 128.5,
    "b": 125.8
  },
  "palette": ["#000000", "#FFFFFF", ...],
  "white_balance_method": "background",
  ...
}
```

#### `GET /api/health`
Health check endpoint.

#### `GET /api/seasons`
Get all season color palettes.

## 📸 Photo Guidelines

### For Best Results:
- Use natural daylight (near window, outdoors in shade)
- Face the camera directly with a neutral expression
- No makeup or minimal makeup
- Plain neutral background (white/grey wall) for most accurate results

### The App Works With:
- Photos with cluttered backgrounds (uses Skin Locus method automatically)
- Indoor lighting (white balance correction applied)
- Various skin tones and ethnicities (algorithm is universal)

### Avoid:
- Colored lighting (red/blue/green bulbs)
- Strong shadows across face
- Filters or heavy editing
- Hats/scarves covering forehead or cheeks

## 🐳 Docker (Optional)

If you prefer Docker:

```bash
# Build and run with Docker Compose
docker-compose up

# Or build manually
docker build -t color-analyzer .
docker run -p 8000:8000 color-analyzer
```

Visit: http://localhost:8000

## 🚢 Deployment

### Option 1: Railway (Recommended)

1. Railway automatically detects `pyproject.toml` and uses uv
2. Set the start command in Railway dashboard:
```bash
uv run uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```
3. Or create a `Procfile`:
```
web: uv run uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```
4. Push to GitHub and connect to Railway
5. Deploy automatically

### Option 2: Render

1. Create a `render.yaml` file or use the dashboard
2. Set build command: `pip install uv && uv sync`
3. Set start command: `uv run uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

### Option 3: PythonAnywhere

1. Upload files to PythonAnywhere
2. Install uv: `pip install uv`
3. Install dependencies: `uv sync`
4. Configure WSGI file to point to the FastAPI app

### Environment Variables

Create a `.env` file (based on `.env.example`):

```
DEBUG=False
MAX_UPLOAD_SIZE=10485760
ALLOWED_ORIGINS=http://localhost:8000,https://yourdomain.com
```

## 🛠️ Development

### Running in Development Mode

```bash
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The `--reload` flag enables auto-reload on code changes.

### Installing Development Dependencies

```bash
uv sync --extra dev
```

This installs additional tools like pytest, ruff, etc.

### Running Tests

(Tests can be added in the future)

```bash
uv run pytest tests/
```

### Linting and Formatting

```bash
uv run ruff check .
uv run ruff format .
```

## 🎨 Color Theory Background

This application implements the seasonal color analysis system based on:
- **Temperature**: Warm (yellow-based) vs Cool (blue-based) undertones
- **Value**: Light vs Deep coloring intensity

The four seasons each have distinct characteristics:
- **Winter**: Cool, deep, high contrast
- **Summer**: Cool, light, soft
- **Autumn**: Warm, deep, rich
- **Spring**: Warm, light, clear

## 🔧 Troubleshooting

### "No face detected" Error
- Ensure face is clearly visible and well-lit
- Face the camera directly
- Remove any obstructions (sunglasses, masks, etc.)

### "Multiple faces detected" Error
- Use a photo with only one person
- Crop the image to show only your face

### "Photo is too dark/bright" Error
- Retake photo with better lighting
- Avoid direct sunlight or very dim environments

### White Balance Method Shows "None"
- This happens if white balance is disabled
- Enable the white balance toggle before uploading

## 📦 Dependencies

This project uses **uv** for blazingly fast dependency management (10-100x faster than pip!).

See [UV_BENEFITS.md](UV_BENEFITS.md) for why we use uv and how it works.

Main dependencies:
- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server
- **MediaPipe**: Google's ML solutions for face detection
- **OpenCV**: Computer vision library
- **NumPy**: Numerical computing
- **Pillow**: Image processing
- **Pydantic**: Data validation

All dependencies are managed via `pyproject.toml` (modern Python packaging standard).

## 📄 License

This project is open source and available for personal and educational use.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## 📧 Support

For questions or issues, please open an issue on the project repository.

---

**Built with ❤️ using FastAPI, MediaPipe, and Computer Vision**

