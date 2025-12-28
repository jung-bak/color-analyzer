# 🚀 Quick Start Guide

## Installation (First Time Only)

### 1. Install uv (if not already installed)

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

### 2. Install Python Dependencies

```bash
uv sync
```

This will install all dependencies using uv's fast resolver:
- FastAPI
- Uvicorn
- MediaPipe
- OpenCV
- NumPy
- Pillow
- Pydantic

## Running the Application

### Windows:
Double-click `run.bat` or run in command prompt:
```cmd
run.bat
```

### Mac/Linux:
Make the script executable and run:
```bash
chmod +x run.sh
./run.sh
```

### Manual Start:
```bash
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

## Accessing the Application

Once the server starts, open your browser and go to:
- **Main App**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/api/health

## Using the Application

1. **Upload a Photo**
   - Click the upload area or drag and drop
   - Supports: JPG, JPEG, PNG (max 10MB)

2. **Wait for Analysis**
   - The app will automatically process your photo
   - Takes 2-5 seconds

3. **View Results**
   - Your seasonal color type (Winter/Summer/Autumn/Spring)
   - Personalized color palette
   - Styling recommendations
   - Technical details

## Tips for Best Results

✅ **Do:**
- Use natural daylight
- Face camera directly
- Plain neutral background
- No or minimal makeup

❌ **Avoid:**
- Colored lighting
- Strong shadows
- Heavy filters
- Face obstructions

## Troubleshooting

### "Module not found" Error
```bash
uv sync
```

### "Port 8000 already in use"
Change the port:
```bash
uv run uvicorn backend.main:app --reload --port 8001
```

### Application won't start
Make sure you're in the correct directory:
```bash
cd color_analyzer
uv run python -c "import backend.main"
```

### Python version error
This project requires Python 3.9 or higher. Check your version:
```bash
python --version
```

If needed, uv can manage Python versions for you:
```bash
uv python install 3.11
uv python pin 3.11
```

## What's Next?

- Read the full [README.md](README.md) for detailed information
- Check [API Documentation](http://localhost:8000/docs) for integration
- Explore the code in the `backend/` and `frontend/` directories

---

**Need Help?** Check the main README.md or open an issue.

