# Mimic User Guide

Mimic is an AI-powered tool that analyzes your calendar to identify high-value meetings and generates a personalized workback plan annotation interface.

## Prerequisites

1.  **Python 3.8+** installed.
2.  **Internet Connection** (for Microsoft Graph API authentication).

## Setup

1.  **Install Dependencies & Download Model**:
    The setup script will create a virtual environment, install required packages, and automatically download the Qwen3-Embedding model (~1.1GB).

    ```bash
    # macOS / Linux
    ./setup.sh

    # Windows
    setup.bat
    ```

    *Note: If the model download fails during setup, you can retry it manually:*
    ```bash
    source venv/bin/activate  # or venv\Scripts\activate on Windows
    python download_model.py
    ```

## Usage

Run the tool with your email address:

### macOS / Linux
```bash
source venv/bin/activate
python mimic.py your.email@company.com
```

### Windows
```cmd
venv\Scripts\activate
python mimic.py your.email@company.com
```

## What Happens Next?

1.  **Authentication**: The tool will ask you to visit `microsoft.com/devicelogin` and enter a code. This securely connects to your calendar.
2.  **Analysis**: Mimic downloads your last 6 months of meetings and uses a local AI model (Qwen3-Embedding) to score them by business value.
3.  **Generation**: It creates an HTML file (e.g., `output/mimic_yourname.html`).
4.  **Interface**: The HTML file opens automatically. It contains:
    *   **5 Synthetic Scenarios**: Pre-defined high-value examples.
    *   **5 Auto-Selected Meetings**: Your highest-value real meetings.
    *   **15 Candidates**: Other high-potential meetings you can choose to annotate.

## Offline Mode

If you already have a JSON file of your calendar events, you can skip authentication:

```bash
python mimic.py your.email@company.com --file my_calendar.json
```
