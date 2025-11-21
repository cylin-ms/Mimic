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
    | Nov 21, 2025 | Jules / Aria | [ ] | Push press‑kit email + templates to media contacts | T‑21 | Initial outreach wave | 1) Finalize press kit assets (Aria); 2) Build media list & segments (Sofia); 3) Draft email templates (Jules); 4) Schedule sends (Leo) |
    | Nov 24, 2025 | Maya | [ ] | Revisit action items from last Studio Slate Review (SSR) | T‑18 | Close carry‑overs | 1) Compile SSR action log (Maya); 2) Resolve open owner assignments (Ravi); 3) Update central tracker (Leo) |
    | Nov 26, 2025 | Ravi | [ ] | Check OOFs/conflicts for Noah (or delegate) | T‑16 | Exec availability check | 1) Pull exec calendars (Ravi); 2) Confirm delegate chain (Noah); 3) Adjust review slots (Leo) |
    | Nov 28, 2025 | Jules / Aria | [ ] | Sync on Premiere content & campaign narrative | T‑14 | Creative lock checkpoint | 1) Align trailer cut notes (Aria); 2) Approve key art variations (Jules); 3) Draft run‑of‑show skeleton (Leo) |
    | Dec 1, 2025 | Jules | [ ] | Draft SSR deck for Executive Review | T‑11 | Slides v1 due | 1) Build deck storyline (Jules); 2) Insert performance metrics (Victor); 3) Add PR activation calendar (Maya) |
    | Dec 2, 2025 | Aria / Jules | [ ] | Align on topics for Executive Touchpoint Meeting | T‑10 | Finalize talking points | 1) Curate agenda (Aria); 2) Pre‑wire key decisions (Noah); 3) Circulate pre‑reads (Leo) |
    | Dec 4, 2025 | Jules | [ ] | Close gaps in SSR deck (creative, PR, distribution) | T‑8 | Deck v2 readiness | 1) Fill creative stills (Aria); 2) Confirm press junket slots (Sofia); 3) Add distribution timelines (Victor) |
    | Dec 9, 2025 | Jules / Aria | [ ] | Slides Final Due | T‑3 | Critical deadline | 1) Lock deck & export (Jules); 2) QA visual consistency (Aria); 3) Publish to review folder (Leo) |
    | Dec 10, 2025 | Maya | [ ] | Noah to review and approve final content | T‑2 | End‑of‑day approval | 1) Route deck to execs (Maya); 2) Track comments (Leo); 3) Capture decision log (Ravi) |
    | Dec 12, 2025 | All Crew | [ ] | Premiere Night: “Starfall” | T‑0 | Live event | 1) Venue readiness & tech check (Leo); 2) Red‑carpet media ops (Sofia); 3) Legal clearances on sponsor signage (Dante); 4) Social live coverage plan (Hana) |
    | Dec 13, 2025 | Maya / Jules | [ ] | Update SSR action items & publish post‑mortem | T+1 | | |

    *Usage Notes: All names are fictional and intended for anonymization.*

5.  **Share & Save**:
    *   When satisfied, type `/share` in BizChat.
    *   This creates a share card with a **DevUI link**.
    *   **Copy the link** and paste it into the **DevUI Link** field for that meeting in the Mimic interface.
    *   Add any additional comments about your analysis experience in the corresponding fields.
    *   *Note: The **ContextFlow** extraction step is coming soon. For now, simply saving the DevUI link is sufficient.*
