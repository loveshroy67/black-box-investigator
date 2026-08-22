# Black Box Investigator

AI-powered incident investigation platform for analyzing incident evidence, extracting event timelines, generating competing hypotheses, and correlating evidence with possible root causes.

## Overview

Black Box Investigator is a full-stack incident investigation system designed to help engineers understand what happened during a production incident.

The system accepts incident evidence such as logs and reports, extracts structured events, builds a chronological timeline, generates competing hypotheses, and maps supporting and contradicting evidence to each hypothesis.

The investigation engine supports Gemini-based reasoning with a deterministic local fallback when the AI service is unavailable or quota-limited.

---

## Key Features

- Incident evidence upload
- Automatic event extraction
- Chronological incident timeline
- AI-assisted hypothesis generation
- Local hypothesis fallback engine
- Supporting vs contradicting evidence
- Hypothesis confidence scoring
- Evidence → hypothesis correlation
- Investigation relationship graph
- Incident severity and status indicators
- Investigation dashboard
- Loading, error, and empty states
- REST API backend
- React frontend

---

## Architecture

```text
                         ┌──────────────────────┐
                         │      User / SRE      │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   React Frontend    │
                         │                      │
                         │  Dashboard           │
                         │  Evidence            │
                         │  Timeline            │
                         │  Investigation       │
                         │  Correlation Graph  │
                         └──────────┬───────────┘
                                    │
                              REST API / HTTP
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     FastAPI API      │
                         │                      │
                         │ /evidence            │
                         │ /timeline             │
                         │ /investigate          │
                         │ /investigation        │
                         └──────────┬───────────┘
                                    │
                                    ▼
                    ┌──────────────────────────────┐
                    │    Investigation Services   │
                    │                              │
                    │ Parser                       │
                    │ Timeline                     │
                    │ Investigation                 │
                    │ Hypothesis Engine             │
                    │ Reasoning                     │
                    └──────────────┬───────────────┘
                                   │
                         ┌─────────┴─────────┐
                         │                   │
                         ▼                   ▼
                ┌────────────────┐   ┌─────────────────┐
                │ Gemini Engine  │   │ Local Fallback  │
                │ AI reasoning   │   │ Hypothesis      │
                │                │   │ Engine          │
                └────────────────┘   └─────────────────┘

Investigation Workflow
Incident Evidence
       │
       ▼
Evidence Upload
       │
       ▼
Event Extraction
       │
       ▼
Structured Timeline
       │
       ▼
Hypothesis Generation
       │
       ├───────────────┐
       │               │
       ▼               ▼
Gemini AI        Local Fallback
       │               │
       └───────┬───────┘
               ▼
       Investigation Results
               │
               ▼
      Evidence Correlation
               │
               ▼
       Root Cause Analysis
Tech Stack
Frontend
React
Vite
React Router
JavaScript / JSX
CSS
Backend
Python
FastAPI
Uvicorn
Pydantic
AI / Reasoning
Google Gemini
Local deterministic hypothesis engine
Evidence-based hypothesis scoring
API Communication
REST
JSON
Multipart file upload
Project Structure
black-box-investigator/
│
├── backend/
│   └── app/
│       ├── agents/
│       ├── api/
│       │   └── incidents.py
│       ├── core/
│       │   └── config.py
│       ├── models/
│       │   └── schemas.py
│       ├── services/
│       │   ├── hypothesis.py
│       │   ├── investigation.py
│       │   ├── local_hypothesis.py
│       │   ├── parser.py
│       │   ├── reasoning.py
│       │   ├── store.py
│       │   └── timeline.py
│       └── main.py
│
├── frontend/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── services/
│       │   └── api.js
│       ├── App.jsx
│       ├── index.css
│       └── main.jsx
│
└── README.md
Backend Services
Parser

parser.py

Responsible for extracting structured incident events from uploaded evidence.

The system can fall back to local parsing when Gemini event extraction is unavailable.

Timeline

timeline.py

Builds and serves the chronological event sequence associated with an incident.

Hypothesis Engine

hypothesis.py

Handles hypothesis generation and investigation reasoning.

Local Hypothesis Engine

local_hypothesis.py

Provides deterministic fallback hypotheses when Gemini is unavailable or quota is exhausted.

The local engine currently considers categories such as:

Database issues
Deployment issues
Infrastructure degradation
Investigation

investigation.py

Combines extracted events and hypotheses into an investigation result.

Relationships are represented as:

{
  "hypothesis_id": "H1",
  "event_id": "E001",
  "relationship": "supports"
}

or:

{
  "hypothesis_id": "H1",
  "event_id": "E002",
  "relationship": "contradicts"
}
Store

store.py

Provides the application's incident/evidence data storage layer.

Reasoning

reasoning.py

Contains reasoning-related investigation functionality.

Frontend

The frontend is organized around an incident investigation workspace.

Dashboard

Provides:

Incident summary
Evidence statistics
Event statistics
Hypothesis statistics
Investigation status
Incident timeline
Investigation results
Evidence → hypothesis correlation
Investigation relationship graph
Evidence

Provides:

Evidence upload
Processing status
Latest artifact information
Extracted event count
Timeline

Displays extracted events chronologically.

Each event can expose:

Timestamp
Event type
Severity
Description
Source
Event ID
Investigation

Displays generated hypotheses and their reasoning.

Each hypothesis includes:

Hypothesis ID
Title
Description
Confidence
Supporting evidence
Contradicting evidence
Reasoning
Insufficient evidence notes
API

The backend exposes incident investigation endpoints under:

/incidents/{incident_id}
Upload Evidence
POST /incidents/{incident_id}/evidence

Uploads an incident evidence file for processing.

Example:

POST /incidents/INC-001/evidence

The backend extracts structured events from the uploaded evidence.

Get Timeline
GET /incidents/{incident_id}/timeline

Returns the extracted incident timeline.

Example:

GET /incidents/INC-001/timeline
Investigate Incident
POST /incidents/{incident_id}/investigate

Starts the investigation process.

Example:

POST /incidents/INC-001/investigate

The system attempts AI-assisted hypothesis generation and can fall back to the local hypothesis engine.

Get Investigation
GET /incidents/{incident_id}/investigation

Returns the generated investigation.

Example:

GET /incidents/INC-001/investigation
Health Check
GET /health

Returns:

{
  "status": "healthy"
}
Gemini → Local Fallback

The investigation system is designed to remain usable when Gemini is unavailable.

The reasoning flow is:

Attempt Gemini
     │
     ├── Success ──→ Use Gemini results
     │
     └── Failure
           │
           ▼
     Local hypothesis engine
           │
           ▼
     Generate deterministic hypotheses

This allows the application to continue generating investigation results even when:

Gemini quota is exhausted
Gemini requests fail
The AI service is temporarily unavailable

For example, when Gemini returns a 429 RESOURCE_EXHAUSTED response, the backend switches to the local hypothesis engine.

Local Hypothesis Engine

The current local investigation engine can generate hypotheses based on detected event categories.

Example hypotheses include:

H1 — Database Performance or Migration Issue

Considers database-related events as supporting evidence.

H2 — Application Defect Introduced During Deployment

Considers deployment-related events as supporting evidence.

H3 — Independent Infrastructure Degradation

Considers infrastructure, database, and application events as potential supporting evidence.

Each hypothesis contains a confidence score and evidence relationships.

Running Locally
Backend

Navigate to:

cd backend

Create and activate a virtual environment:

python -m venv .venv

Windows PowerShell:

.\.venv\Scripts\Activate.ps1

Install dependencies:

pip install -r requirements.txt

Start FastAPI:

python -m uvicorn app.main:app --reload

The backend will be available at:

http://127.0.0.1:8000

FastAPI documentation:

http://127.0.0.1:8000/docs
Frontend

Open another terminal:

cd frontend

Install dependencies:

npm install

Start the development server:

npm run dev

The Vite development server will display the local frontend URL in the terminal.

Environment Variables

The frontend can use:

VITE_API_URL=http://127.0.0.1:8000

The frontend accesses the API through:

const API_URL = import.meta.env.VITE_API_URL;

Backend AI credentials should be stored in environment variables and should never be committed to Git.

Example Investigation

An incident may contain events such as:

Deployment
     │
     ▼
Database activity
     │
     ▼
Connection timeout
     │
     ▼
Application failures

The investigation engine evaluates competing explanations.

Example:

H1 — Database Performance Issue
Confidence: 65%


Supporting:
- Database event
- Connection timeout


Contradicting:
- Infrastructure event
H2 — Deployment Issue
Confidence: 40%


Supporting:
- Deployment event


Contradicting:
- Database event
H3 — Infrastructure Degradation
Confidence: 25%


Supporting:
- Infrastructure event
- Database event
- Application event

The purpose is not to automatically declare a root cause, but to provide an evidence-backed set of competing explanations for further investigation.

Design Philosophy

Black Box Investigator follows an evidence-first approach.

Instead of presenting a single unexplained AI conclusion, the system exposes:

Evidence
   ↓
Events
   ↓
Timeline
   ↓
Hypotheses
   ↓
Supporting / Contradicting Evidence
   ↓
Confidence
   ↓
Investigator Review

This makes the investigation process more transparent and easier to audit.

Current Status
Completed
 FastAPI backend
 Incident API
 Evidence upload
 Event extraction
 Timeline generation
 Gemini integration
 Local event parser fallback
 Local hypothesis engine
 Investigation API
 React dashboard
 Evidence page
 Timeline page
 Investigation page
 Hypothesis confidence visualization
 Evidence correlation
 Investigation relationship graph
 Loading states
 Error states
 Empty states
Future Improvements
Persistent database storage
Authentication and authorization
Multiple incidents
Advanced graph visualization
More sophisticated root-cause scoring
Observability integrations
Kubernetes / cloud log ingestion
Incident collaboration
Investigation history
Production deployment
License

This project is intended for educational, portfolio, and engineering demonstration purposes.



### Important before committing


Because GitHub **already rejected your push for a repository rule violation**, don't run `git add .` and push yet if your Gemini/API key may be somewhere in the repository.


First run:


```powershell
git status

and:

git ls-files | Select-String "\.env"