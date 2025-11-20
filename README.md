# Mimic: Meeting Value Estimator & Workback Plan Generator

**Version:** 1.0.0

This package provides a high-performance, calibrated AI model for estimating the business value of meetings. It uses a local embedding model (Qwen3-Embedding) that has been calibrated against large reasoning models (Qwen3-30B) to provide accurate, sub-second value estimation.

## Features

- **Ultra-Fast**: Processes meetings in ~0.2 seconds (CPU).
- **Calibrated Scoring**: Scores are aligned with large model reasoning (0-100 scale).
- **Privacy-First**: Runs entirely locally. No data leaves your machine.
- **Categorization**: Automatically classifies meetings (Strategic, Operational, Social, etc.).

## Installation

The setup process will install Python dependencies and automatically download the required AI model (Qwen3-Embedding, ~1.1GB).

### macOS / Linux

1. Open a terminal.
2. Run the setup script:

   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

   *If the model download fails, activate the environment and run `python download_model.py` manually.*

### Windows

1. Open Command Prompt or PowerShell.
2. Run the setup script:

   ```cmd
   setup.bat
   ```

   *If the model download fails, activate the environment and run `python download_model.py` manually.*

   ```cmd
   setup.bat
   ```

This creates an isolated Python virtual environment (`venv`) with all necessary dependencies.

## Usage

You can run the tool using the provided wrapper scripts, which handle the environment activation for you.

### Run on macOS / Linux

```bash
./run.sh path/to/your/calendar.json
```

### Run on Windows

```cmd
run.bat path\to\your\calendar.json
```

The output will be saved to `output/calendar_estimated.json`.

### Manual Usage (Advanced)

If you prefer to activate the environment manually:

**macOS/Linux:**

```bash
source venv/bin/activate
python estimate_value.py path/to/your/calendar.json
```

**Windows:**

```cmd
venv\Scripts\activate
python estimate_value.py path\to\your\calendar.json
```

## Input Format

The input JSON should be a list of meeting objects or an object with an `events` key. Each meeting object should ideally have:

- `subject`: The meeting title
- `bodyPreview` or `body.content`: The meeting description
- `attendees`: A list of attendees (used for impact sizing)

## Model Details

- **Base Model**: Qwen3-Embedding (0.6B parameters)
- **Calibration**: Linear regression against Qwen3-30B ground truth.
- **Logic**: Semantic similarity to "High Value" vs "Low Value" anchors + Attendee count boost.

## Workback Plan Workflow

1.  **Generate Report**: Run Mimic to identify high-value meetings.
2.  **Get Prompt**: Copy the AI-optimized prompt from the Mimic report.
3.  **BizChat**: Paste into BizChat to generate a detailed workback plan (Milestones, Owners, T-Minus schedule).
4.  **Share**: Use `/share` in BizChat to generate a DevUI link.
5.  **Save**: Copy the link back into Mimic's "DevUI Link" field and add comments.
6.  **Extract**: *(Coming Soon)* ContextFlow extraction is pending implementation.
