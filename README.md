Job Companion Studio
This agentic AI application leverages LangGraph, Pydantic, and Streamlit to transform a master resume into tailored, high-impact job application materials. Operating as a unified workspace, the platform orchestrates dual graph workflows to generate ATS-dense resumes and strategic cover letters targeted precisely to job descriptions. The system combines deterministic scoring, iterative critique-revision loops, and native dual-format document compilation (.docx and PDF) optimized for automated tracking systems and recruiter screens.

Unlike standard one-shot prompt generators, Job Companion Studio relies on stateful, multi-agent evaluation loops. It extracts explicit technical signals, cross-functional bridge competencies, and structural requirements from target postings. Before delivering output, specialized critic nodes inspect draft artifacts against ATS density, keyword coverage, and strict word constraints—conditionally routing documents back for automated refinement.

🏗️ Architecture Flow

```mermaid
flowchart TD
    A([User Input: Master Resume & Target JD]) --> Splitter{Select Artifact}

    %% Resume Subgraph
    subgraph Resume Multi-Agent Graph
        Splitter -->|Route Resume| R_Extract[extract_requirements_node]
        R_Extract --> R_Draft[resume_builder_node: Drafts Structured JSON]
        R_Draft --> R_Eval{evaluate_ats_fit: Check Match Score & Density}
        R_Eval -->|Score < 85% AND Iterations < 3| R_Draft
        R_Eval -->|Score >= 85% OR Iterations = 3| R_Output[Final ATS Structured Resume]
    end

    %% Cover Letter Subgraph
    subgraph Cover Letter Multi-Agent Graph
        Splitter -->|Route Cover Letter| CL_Extract[extract_keywords_node]
        CL_Extract --> CL_Draft[drafter_node: Drafts Narrative Letter]
        CL_Draft --> CL_Eval{route_draft: Check Length & Theme Coverage}
        CL_Eval -->|Score < 80% AND Iterations < 3| CL_Draft
        CL_Eval -->|Score >= 80% OR Iterations = 3| CL_Polish[polisher_node: Style & Tone Polish]
        CL_Polish --> CL_Output[Final Strategic Cover Letter]
    end

    %% Export Pipeline
    R_Output --> ExportEngine[Shared Export Engine: docx_builder & pdf_builder]
    CL_Output --> ExportEngine
    ExportEngine --> FinalFiles([Export: ATS-Optimized Word .docx & WeasyPrint PDF])

    %% Styling
    style A fill:#EAE6FF,stroke:#3B3273,color:#3B3273
    style FinalFiles fill:#EAE6FF,stroke:#3B3273,color:#3B3273
    style Splitter fill:#FFFFFF,stroke:#8B7355,color:#1E1E1E
    style R_Eval fill:#FFFFFF,stroke:#8B7355,color:#1E1E1E
    style CL_Eval fill:#FFFFFF,stroke:#8B7355,color:#1E1E1E
    style R_Extract fill:#FAF7F2,stroke:#D4C4B7,color:#4A3B32
    style R_Draft fill:#FAF7F2,stroke:#D4C4B7,color:#4A3B32
    style R_Output fill:#FAF7F2,stroke:#D4C4B7,color:#4A3B32
    style CL_Extract fill:#FAF7F2,stroke:#D4C4B7,color:#4A3B32
    style CL_Draft fill:#FAF7F2,stroke:#D4C4B7,color:#4A3B32
    style CL_Polish fill:#FAF7F2,stroke:#D4C4B7,color:#4A3B32
    style CL_Output fill:#FAF7F2,stroke:#D4C4B7,color:#4A3B32
    style ExportEngine fill:#EAE6FF,stroke:#3B3273,color:#3B3273
 ```


🗂️ Project Structure

```text
jobcompanion/
├── .env                          # Environment credentials (API keys)
├── .streamlit/
│   └── config.toml               # Engine-level theme enforcement (light baseline override)
├── requirements.txt              # Project package dependencies
├── src/
│   ├── __init__.py
│   ├── cover_letter/
│   │   ├── __init__.py
│   │   ├── state.py              # TypedDict schema defining Cover Letter graph state
│   │   ├── tools.py              # Deterministic evaluation logic (word counts, keyword metrics)
│   │   ├── nodes.py              # LLM operations (keyword extraction, drafting, polish)
│   │   ├── edges.py              # Conditional routing logic for critique-revision loops
│   │   └── graph.py              # StateGraph assembly & MemorySaver checkpointing
│   ├── resume/
│   │   ├── __init__.py
│   │   ├── state.py              # Pydantic schemas & state models for structured resumes
│   │   ├── nodes.py              # ATS signal analysis, content generation, and auditing
│   │   ├── edges.py              # Quality gates & revision routing
│   │   └── graph.py              # Resume graph compilation & memory checkpointing
│   └── shared/
│       ├── __init__.py           # Package interface exposing docx & PDF generation builders
│       └── export/
│           ├── __init__.py       # Re-exports export functions for application consumption
│           ├── docx_builder.py   # Native python-docx builder (tab stops, ATS font rules)
│           └── pdf_builder.py    # Print-ready CSS rendering via WeasyPrint
├── app.py                        # Multi-tab Streamlit UI with unified styling
└── experimentation.ipynb         # Sandbox notebook for testing agent chains & prompts
```

⚙️ Local Development Setup
This project uses a Python virtual environment (venv) to isolate dependencies and prevent conflicts with other system packages.

1. Create a Virtual Environment

Navigate to the root of the project directory in your terminal and create the environment:

```bash
python3.12 -m venv .venv
```

1. Activate the Virtual Environment

You must activate the environment every time you work on or run the project.

On Ubuntu/Linux/macOS:

```bash
source .venv/bin/activate
```

On Windows (Command Prompt):

```bash
venv\Scripts\activate
```

(Your terminal prompt should now show (venv) at the beginning of the line.)

1. Install Dependencies

With the virtual environment active, install Streamlit, LangGraph, and the required AI libraries:

```bash
pip install streamlit langgraph langchain langchain-openai pydantic python-dotenv python-docx weasyprint
```
(Alternatively, if using requirements.txt: pip install -r requirements.txt)

Note: For mac users only.

WeasyPrint relies on several underlying libraries (like Pango, Cairo, Glib, etc.) that might be installed differently or missing on macOS compared to your Linux distribution.
```bash
brew install pango cairo gdk-pixbuf
```

1. Configure Environment Variables

Create a .env file in the root directory and add your OpenAI API key:
OPENAI_API_KEY="sk-your-actual-api-key-here"

🚀 Running the Application
To launch the frontend interface, ensure your virtual environment is active and execute the Streamlit command:

```bash
python3 -m streamlit run app.py
```

🧠 Core Agentic Logic & System Features
Multi-Domain Graph Orchestration (src/cover_letter/, src/resume/): Two independent LangGraph state machines operate side by side. The resume engine optimizes structured data points for scanning efficiency, while the cover letter engine controls long-form narrative voice and contextual fit.

Deterministic Quality Gates (tools.py): Keyword scores, section quotas, and length parameters are verified using pure Python utilities to ground validation metrics and prevent LLM grading hallucinations.

Cyclical Revision Loops (edges.py): Both workflows evaluate drafts against pre-set acceptance criteria. Inadequate drafts route backward into the drafter node alongside concrete critiques for up to 3 iterative passes.

ATS Document Engineering (src/shared/export/):

Resume Formatting: Built in Times New Roman with tight margins (0.5–0.6 in.) and precise tab stops to guarantee single/dual-page density and clear ATS parsing.

Cover Letter Formatting: Built in Calibri with standard 1-inch margins and proportional spacing, tailored for modern tech roles.

Dual Engine Delivery: Compiles native, edit-ready .docx files via python-docx alongside pixel-aligned .pdf files via WeasyPrint.

Cross-Theme UI Architecture (.streamlit/config.toml & app.py): Employs explicit server-level theme locking and high-specificity CSS rules to prevent browser or OS-level dark mode interference, keeping inputs, tabs, and document previews legible across all environments.