# CommAi — Sales Intelligence Platform (MVP)

A tool that analyzes meeting audio transcripts, extracts client updates and requirements, and matches them to watsonx Orchestrate product capabilities using an AI agent.

## Architecture

```
CommAi/
├── frontend/          # React + Carbon UI (Vite + TypeScript)
├── backend/           # FastAPI (Python) — REST API + LangChain AI agent
├── docker-compose.yml # Local PostgreSQL database
├── .env               # Environment variables (copy from .env.example)
└── .env.example       # Template
```

## Data Flow

```mermaid
flowchart TD
    %% ── FRONTEND ─────────────────────────────────────────────────────────────
    subgraph FE["React 19 Frontend  ·  :5173"]
        direction TB
        DASH["Dashboard\n/dashboard"]
        ACCS["Accounts\n/accounts"]
        ACCD["Account Detail\n/accounts/:id"]
        TRNS["Transcripts\n/transcripts"]
        TRND["Transcript Detail\n/transcripts/:id"]
        OPPS["Opportunities\n/opportunities"]
        APICL["api/client.ts  ·  axios\nbaseURL → /api"]
        DASH & ACCS & ACCD & TRNS & TRND & OPPS --> APICL
    end

    %% ── FASTAPI ROUTERS ──────────────────────────────────────────────────────
    subgraph API["FastAPI  ·  Uvicorn  ·  :8000"]
        direction TB
        subgraph ROUTER_ACCS["prefix /accounts"]
            RA1["GET  /accounts/"]
            RA2["GET  /accounts/:id  (joinload client + sales_rep)"]
            RA3["POST /accounts/"]
        end
        subgraph ROUTER_CLIS["prefix /clients"]
            RC1["GET  /clients/"]
            RC2["GET  /clients/:id"]
            RC3["POST /clients/"]
        end
        subgraph ROUTER_REPS["prefix /sales-reps"]
            RR1["GET  /sales-reps/"]
            RR2["GET  /sales-reps/:id"]
            RR3["POST /sales-reps/"]
        end
        subgraph ROUTER_TRNS["prefix /transcripts"]
            RT1["GET  /transcripts/  (?account_id filter)"]
            RT2["GET  /transcripts/:id"]
            RT3["GET  /transcripts/:id/updates"]
            RT4["GET  /transcripts/:id/opportunities"]
            RT5["POST /transcripts/"]
        end
        subgraph ROUTER_AGNT["prefix /agent"]
            RG1["POST /agent/analyze  → BackgroundTask"]
            RG2["GET  /agent/opportunities  (all, order by score↓)"]
        end
    end

    %% ── ORM / SCHEMAS ────────────────────────────────────────────────────────
    subgraph ORM["SQLAlchemy ORM  +  Pydantic v2 Schemas"]
        direction LR
        MOD["models.py\nSalesRep · Client · Account\nTranscript · ClientUpdate · Opportunity"]
        SCH["schemas.py\n*Out · *Create\nfrom_attributes=True"]
        MOD <--> SCH
    end

    %% ── POSTGRESQL ───────────────────────────────────────────────────────────
    subgraph PG["PostgreSQL  ·  Docker  ·  :5432  ·  db: commai"]
        direction TB
        T_REPS[("sales_reps\nid · name · email · territory")]
        T_CLIS[("clients\nid · company_name · industry · website")]
        T_ACCS[("accounts\nid · sales_rep_id · client_id\naccount_name · stage · notes")]
        T_TRNS[("transcripts\nid · account_id · sales_rep_id\ntitle · meeting_date · raw_text\nstatus: pending→processing→completed|failed")]
        T_UPDS[("client_updates\nid · transcript_id · category\nsummary · verbatim_quote · speaker · priority")]
        T_OPPS[("opportunities\nid · transcript_id · title · description\nmatched_product · matched_capability\nconfidence_score · status · agent_reasoning")]
        T_REPS --> T_ACCS
        T_CLIS --> T_ACCS
        T_ACCS --> T_TRNS
        T_REPS --> T_TRNS
        T_TRNS --> T_UPDS
        T_TRNS --> T_OPPS
    end

    %% ── AI PIPELINE ──────────────────────────────────────────────────────────
    subgraph AIPIPE["LangChain AI Pipeline  ·  agent/analyzer.py"]
        direction TB
        STEP1["Step 1 · Extraction\nSystemMessage: EXTRACTION_SYSTEM_PROMPT\nHumanMessage: raw_text\n→ JSON { updates[], opportunities[] }"]
        STEP2["Step 2 · MCP Enrichment  (per opportunity)\nSystemMessage: SOLUTION_MATCHING_SYSTEM_PROMPT\nHumanMessage: title + description\nllm.bind_tools(mcp_tools)\n→ matched_product · matched_capability\n  confidence_score · agent_reasoning"]
        MCP_LOAD["_get_mcp_tools()\nStdioServerParameters\nuvx mcp-proxy --transport streamablehttp"]
        STEP1 --> STEP2
        MCP_LOAD --> STEP2
    end

    %% ── EXTERNAL IBM SERVICES ────────────────────────────────────────────────
    subgraph IBM["IBM Cloud  ·  External"]
        WXO["ChatWxO  (ibm-watsonx-orchestrate-sdk)\nwatsonx/ibm/granite-3-8b-instruct\ntemp=0.2  max_tokens=4000"]
        MCP_SRV["wxo-docs MCP Server\ndeveloper.watson-orchestrate.ibm.com/mcp\nProduct capability tool registry"]
    end

    %% ── DATA FLOW EDGES ──────────────────────────────────────────────────────
    APICL -->|"HTTP GET/POST /api/*"| API

    ROUTER_ACCS & ROUTER_CLIS & ROUTER_REPS & ROUTER_TRNS & ROUTER_AGNT --> ORM
    ORM -->|"Depends(get_db)\nSELECT / INSERT / UPDATE"| PG

    RG1 -->|"add_task(_run_analysis)"| STEP1
    STEP1 -->|"await llm.ainvoke()"| WXO
    WXO -->|"JSON response"| STEP1
    STEP2 -->|"tool_call via bind_tools"| WXO
    MCP_LOAD -->|"SSE / StreamableHTTP"| MCP_SRV
    MCP_SRV -->|"tool results"| STEP2
    WXO -->|"enriched JSON"| STEP2

    STEP1 -->|"UPDATE status=processing"| T_TRNS
    STEP2 -->|"INSERT client_updates"| T_UPDS
    STEP2 -->|"INSERT opportunities\nUPDATE status=completed|failed"| T_OPPS
```

## Quick Start

### 1. Prerequisites

- Docker Desktop (for PostgreSQL)
- Node.js 18+
- Python 3.11+
- `uvx` (install via `pip install uv`)

### 2. Environment variables

```bash
cp .env.example .env
# Edit .env and fill in:
#   WXO_INSTANCE_URL — your watsonx Orchestrate instance URL
#   WXO_API_KEY      — your watsonx Orchestrate API key
```

### 3. Start the database

```bash
docker-compose up -d
```

### 4. Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Seed mock data (creates tables + inserts sample data)
python -m app.data.seed

# Start the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at: http://localhost:8000/docs

### 5. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend available at: http://localhost:5173

---

## Features

### Dashboard
- KPI tiles: active accounts, transcripts, pending analysis, high-confidence opportunities
- Account cards with deal stage indicators
- Recent transcript list with status badges

### Accounts
- Full account listing with search
- Account detail page with client info, deal notes, and linked transcripts

### Transcripts
- List and filter transcripts by account
- Transcript detail with raw text viewer
- **Run AI Analysis** button — triggers LangChain agent pipeline

### Opportunities
- All AI-identified opportunities ranked by confidence score
- Filter by status and confidence level
- AI reasoning panel per opportunity

---

## AI Agent Pipeline

1. **Transcript → LangChain Agent (ChatWxO)**
   - Extracts client updates: requirements, feedback, blockers, action items
   - Identifies solution opportunities with confidence scores

2. **MCP Enrichment (wxo-docs)**
   - Connects to the watsonx Orchestrate documentation MCP server
   - Looks up specific product capabilities to match each opportunity
   - Updates matched_product, matched_capability, and agent_reasoning

3. **Results persisted to PostgreSQL**
   - Updates and opportunities stored and surfaced in the UI

---

## Database Schema

| Table | Purpose |
|---|---|
| `sales_reps` | Sales team members |
| `clients` | Client organizations |
| `accounts` | Rep ↔ client relationships and deal context |
| `transcripts` | Raw meeting transcripts |
| `client_updates` | AI-extracted requirements, feedback, blockers |
| `opportunities` | AI-matched solution opportunities |

---

## Mock Data

5 realistic sales transcripts pre-seeded across 4 client accounts:

| Client | Industry | Account |
|---|---|---|
| Acme Corp | Financial Services | Customer service automation (2 meetings) |
| TechFlow Inc | SaaS | Engineering knowledge assistant |
| GlobalRetail | Retail | AI platform — 3 use cases |
| HealthBridge | Healthcare | Ambient documentation & prior auth |

---

## Configuration

All config lives in `.env`. Key variables:

| Variable | Description |
|---|---|
| `WXO_INSTANCE_URL` | watsonx Orchestrate instance URL |
| `WXO_API_KEY` | watsonx Orchestrate API key |
| `WXO_MODEL` | Model ID (e.g. `watsonx/ibm/granite-3-8b-instruct`) |
| `DATABASE_URL` | PostgreSQL connection string |
| `WXO_MCP_URL` | MCP server URL (default: `https://developer.watson-orchestrate.ibm.com/mcp`) |
# CommAI
