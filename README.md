# Local AI Bank Statement Converter - FastAPI Backend

This is the decoupled FastAPI backend for the **Local AI Bank Statement & Document to Excel Converter**. It exposes a secure REST API for document upload, processing (OCR + local/cloud AI analysis), and compiling structured financial transactions into Excel files.

## Features

- **FastAPI Framework**: Decoupled, high-performance, asynchronous endpoints.
- **Dynamic OCR Engine**: Support for EasyOCR, PaddleOCR, and PyTesseract with layout geometry sorting.
- **Hybrid AI Model Router**: Orchestrates local Ollama/LM Studio models and cloud models (OpenAI, Claude, Gemini, Groq) to parse unstructured OCR text.
- **SQLModel & SQLite**: Lightweight, relational database for storing statement metadata, audit status, and encrypted API credentials.
- **Spreadsheet Compilation**: Formats and styles Excel sheets using `openpyxl` with real-time ledger balance calculations.
- **Enterprise Security**: 
  - AES-GCM (Fernet) encryption for third-party API keys (stored locally, encrypted).
  - Magic byte file signature checks to prevent malicious binary execution.
  - Zero-overwriting file shredding to completely wipe sensitive statement files from disk.

---

## Directory Structure

```text
backend/
├── app/
│   ├── api/             # API Endpoints (auth, documents, extraction, settings, export)
│   ├── ai/              # AI Orchestrator & LLM prompt handlers
│   ├── ocr/             # Multi-engine OCR runners & geometric layout sorters
│   ├── excel/           # openpyxl excel builder & styling engine
│   ├── database/        # SQLite connection setup & SQLModel schemas
│   ├── security/        # JWT auth, magic bytes checker, AES credentials encryption
│   └── services/        # Background queue worker system
├── Dockerfile           # Multi-stage build Docker container configuration
├── requirements.txt     # Python libraries
├── run.py               # Main dev server entrypoint
├── temp_reset.py        # Utility script to clean up databases and uploads
└── Bank_Statement_Template.xlsx # Target Excel template file
```

---

## Setup & Installation

### Prerequisites
- **Python 3.10 or 3.11** installed on your system.
- **Tesseract OCR (Optional)**: If you plan to use PyTesseract.
  - *Windows*: Download installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) and install. Add to system PATH, or specify the executable in your `.env` file.

### 1. Set Up Virtual Environment
Navigate to the `backend/` directory in your terminal and run:

```bash
# Create environment
python -m venv venv

# Activate on Windows (PowerShell):
.\venv\Scripts\Activate.ps1

# Activate on macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env` and configure your settings:
```bash
cp .env.example .env
```
Key variables inside `.env`:
- `SECRET_KEY`: Random string for JWT tokens.
- `TESSERACT_CMD`: Path to `tesseract.exe` (only needed on Windows if not in path, e.g. `C:\Program Files\Tesseract-OCR\tesseract.exe`).
- `OLLAMA_BASE_URL`: Base URL for local Ollama instances (defaults to `http://localhost:11434`).

### 4. Run the Dev Server
```bash
python run.py
```
- The backend will start on **`http://127.0.0.1:8000`**.
- OpenAPI Docs are available at **`http://127.0.0.1:8000/docs`**.

---

## Tauri Desktop Sidecar Compilation

If you are bundling this application as a desktop app via Tauri, you can package the backend as a standalone "sidecar" binary using PyInstaller:

1. Activate your virtual environment and install PyInstaller:
   ```bash
   pip install pyinstaller
   ```
2. Compile the python app:
   ```bash
   pyinstaller --name="converter-backend" --onedir run.py
   ```
3. Place the generated executable folder into the Tauri resources directory: `frontend/src-tauri/bin/`.
4. Rename it using the target triple naming format (e.g. `converter-backend-x86_64-pc-windows-msvc.exe` for Windows).

---

## Docker Deployment

Build and run using Docker:

```bash
# Build the image
docker build -t pdf-excel-backend .

# Run the container (binds to port 8000)
docker run -p 8000:8000 pdf-excel-backend
```

---

## Testing

Run backend tests using pytest:
```bash
pip install pytest
pytest
```
