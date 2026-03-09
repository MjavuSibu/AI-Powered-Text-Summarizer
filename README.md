# AI-Powered Text Summarizer

A production-quality desktop application for summarizing long texts using multiple AI-powered methods. Built with Python and PyQt6, this project is designed as an example of a modern AI productivity tool.

---

## Features

**Multiple Summarization Methods**

The application supports three distinct summarization approaches, each suited to different use cases and resource constraints.

| Method | Engine | Best For |
|---|---|---|
| Extractive (NLP) | Sumy (LSA, LexRank, Luhn, TextRank) | Fast, offline summarization |
| Abstractive (Transformer) | HuggingFace BART / T5 | High-quality, human-like summaries |
| LLM API (OpenAI) | OpenAI GPT-4o-mini | Best quality, requires API key |

**Core Capabilities**

The application provides a professional, feature-complete workflow for document summarization. Users can paste text directly into the input panel or upload `.txt` and `.pdf` files using the drag-and-drop upload zone. Summary length is adjustable between Short, Medium, and Long settings. The output panel displays the generated summary alongside key statistics including word count, estimated reading time, and compression ratio. Summaries can be copied to the clipboard with a single click or exported as professionally formatted PDF documents.

**Bonus Features**

A persistent summary history panel in the sidebar stores the last 50 summaries across application sessions. The application also includes a full suite of keyboard shortcuts for power users and supports both light and dark UI themes.

---

## Architecture

The project uses a modular, layered architecture to ensure clean separation of concerns between the GUI, business logic, and data processing layers.

```
AI-Powered-Text-Summarizer/
├── main.py                        # Application entry point
├── requirements.txt               # Python dependencies
├── spec.spec                      # PyInstaller packaging spec
├── PACKAGING.md                   # Packaging instructions
├── .env                           # (You create this) API keys
│
├── assets/
│   ├── icons/                     # Application icon files
│   └── theme/
│       ├── light.qss              # Light theme stylesheet
│       └── dark.qss               # Dark theme stylesheet
│
├── gui/                           # All PyQt6 GUI components
│   ├── main_window.py             # Top-level application window
│   ├── widgets/
│   │   ├── toolbar.py             # Method, length, and action controls
│   │   ├── sidebar.py             # Navigation and history panel
│   │   ├── input_panel.py         # Text input and file upload area
│   │   ├── output_panel.py        # Summary display and stats
│   │   └── history_list.py        # History entry widgets and manager
│   └── workers/
│       └── summary_worker.py      # Background QThread for AI inference
│
├── summarization/                 # Core AI summarization engines
│   ├── base_summarizer.py         # Abstract base class interface
│   ├── extractive.py              # Sumy NLP algorithms
│   ├── abstractive.py             # HuggingFace Transformers
│   └── llm_api.py                 # OpenAI API integration
│
├── processing/                    # Text pre-processing utilities
│   ├── file_reader.py             # .txt and .pdf file reader
│   ├── text_chunker.py            # Long document splitter
│   └── stats_calculator.py        # Word count, reading time, compression
│
├── export/                        # Output handlers
│   ├── pdf_exporter.py            # ReportLab PDF generation
│   └── clipboard_handler.py       # System clipboard integration
│
└── utils/                         # Shared application utilities
    ├── constants.py               # Enums and application-wide constants
    ├── config.py                  # User preference persistence (QSettings)
    └── helpers.py                 # Stateless utility functions
```

---

## Installation

**Prerequisites:** Python 3.9 or higher, and Git.

**Step 1: Clone the Repository**

```bash
git clone https://github.com/YOUR_USERNAME/AI-Powered-Text-Summarizer.git
cd AI-Powered-Text-Summarizer
```

**Step 2: Create a Virtual Environment**

Using a virtual environment is strongly recommended to isolate project dependencies.

```bash
# Create the virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (macOS / Linux)
source venv/bin/activate
```

**Step 3: Install Dependencies**

```bash
pip install -r requirements.txt
```

This will install PyQt6, HuggingFace Transformers, PyTorch (CPU), Sumy, OpenAI, pdfplumber, ReportLab, and all other required packages.

> **Note on PyTorch:** The `requirements.txt` installs the CPU-only version of PyTorch by default. For significantly faster abstractive summarization on a machine with an NVIDIA GPU, install the CUDA version instead:
> ```bash
> pip install torch --index-url https://download.pytorch.org/whl/cu118
> ```

**Step 4: Configure Your API Key (Optional)**

The LLM API summarization method requires an OpenAI API key. To configure it, create a file named `.env` in the project root directory and add the following line:

```
OPENAI_API_KEY=your_secret_api_key_here
```

This file is listed in `.gitignore` and will never be committed to version control.

---

## Running the Application

Once installation is complete, launch the application from the project root:

```bash
python main.py
```

---

## Keyboard Shortcuts

| Action | Shortcut |
|---|---|
| Summarize | `Ctrl + Enter` |
| Copy Summary | `Ctrl + Shift + C` |
| Export to PDF | `Ctrl + Shift + E` |
| Open File | `Ctrl + O` |
| New Summary | `Ctrl + N` |
| Clear Input | `Ctrl + Shift + X` |
| Toggle Theme | `Ctrl + Shift + T` |
| Show Shortcuts | `Ctrl + ?` |

---

## Building a Windows Executable

To package the application into a standalone `.exe` file, refer to the detailed instructions in [PACKAGING.md](PACKAGING.md).

The short version:

```bash
pip install pyinstaller
pyinstaller spec.spec
```

The final executable will be located at `dist/AI-Powered-Text-Summarizer/AI-Powered-Text-Summarizer.exe`.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
