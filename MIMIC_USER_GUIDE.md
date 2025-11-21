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

    ![Main Page](Mimic_cyl_portal.html.png)
    *Main page of Mimic showing synthetic scenarios and high-value meetings.*

    ![Meeting Selected](Mimic_cyl_portal_meeting_selected.png)
    *Mimic with one meeting selected showing the WBP prompt and user input boxes.*

## Offline Mode

If you already have a JSON file of your calendar events, you can skip authentication:

```bash
python mimic.py your.email@company.com --file my_calendar.json
```

## Generating Workback Plans with BizChat

Once Mimic generates the HTML report, you can use it to create detailed workback plans in BizChat:

1.  **Select a Meeting**: In the Mimic HTML report, click on any high-value meeting.
2.  **Copy Prompt**: Click the "Copy Prompt" button to get a specialized prompt designed for that specific meeting type.
3.  **Generate in BizChat**: Paste the prompt into BizChat.
4.  **Refine the Plan**: The initial prompt starts the conversation. Guide BizChat to refine the plan until it matches your needs. A recommended target format is a table with the following columns:
    *   **Milestone Date**: Date of the activity.
    *   **Owner(s)**: Person responsible.
    *   **Completed**: Checkbox or status.
    *   **Milestone Activity**: Description of the task.
    *   **T-Minus**: Days remaining until the event (T-0).
    *   **Notes**: Special attention items.
    *   **Required Tasks & Responsible Owners**: Detailed breakdown of subtasks.

    **Sample Target Output:**

    | Milestone Date | Owner(s) | Completed | Milestone Activity | T‑Minus | Notes | Required Tasks & Responsible Owners |
    | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
    | Nov 30, 2025 | Priya / Dante | [ ] | Final music licensing & talent agreements | T‑12 | Contracts locked | 1) Verify cue sheets (Priya); 2) Confirm talent appearance terms (Dante); 3) Archive signed docs (Leo) |
    | Dec 6, 2025 | Hana / Sofia | [ ] | Social countdown + press junket schedule | T‑6 | Publicity ramp | 1) Publish countdown content (Hana); 2) Confirm media slots (Sofia); 3) Prepare talking points (Maya) |

    *Usage Notes: All names are fictional and intended for anonymization.*

5.  **Share & Save**:
    *   When satisfied, type `/share` in BizChat.
    *   This creates a share card with a **DevUI link**.
    *   **Copy the link** and paste it into the **DevUI Link** field for that meeting in the Mimic interface.
    *   Add any additional comments about your analysis experience in the corresponding fields.
    *   *Note: The **ContextFlow** extraction step is coming soon. For now, simply saving the DevUI link is sufficient.*
