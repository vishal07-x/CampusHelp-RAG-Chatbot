# CampusHelp: Enterprise AI-Powered RAG College Assistance Chatbot

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-3.4-38B2AC.svg)](https://tailwindcss.com/)
[![Qdrant](https://img.shields.io/badge/Qdrant-Vector_DB-dc2626.svg)](https://qdrant.tech/)
[![Tests](https://img.shields.io/badge/Tests-27%20Passed%20(100%25)-success.svg)](#19-testing-instructions)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

**CampusHelp** is an end-to-end, production-grade Retrieval-Augmented Generation (RAG) assistant designed for universities and collegiate institutions. It extracts, chunks, indexes, and queries official institutional policies—including academic regulations, fee structures, scholarship rules, placement guidelines, examination codes, and campus facility manuals—delivering real-time, context-grounded answers with exact document and page citations.

---

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Problem Statement](#2-problem-statement)
3. [Key Features](#3-key-features)
4. [Technology Stack](#4-technology-stack)
5. [System Architecture](#5-system-architecture)
6. [RAG Pipeline Workflow](#6-rag-pipeline-workflow)
7. [Project Directory Structure](#7-project-directory-structure)
8. [Prerequisites](#8-prerequisites)
9. [Installation & Setup](#9-installation--setup)
10. [Environment Variables Setup](#10-environment-variables-setup)
11. [Docker Startup Instructions](#11-docker-startup-instructions)
12. [Manual Startup Instructions (Local VS Code)](#12-manual-startup-instructions-local-vs-code)
13. [Database Configuration](#13-database-configuration)
14. [Qdrant Vector Database Configuration](#14-qdrant-vector-database-configuration)
15. [PDF Document Ingestion & Seed Data](#15-pdf-document-ingestion--seed-data)
16. [How to Use the Chatbot](#16-how-to-use-the-chatbot)
17. [Admin Portal & Management](#17-admin-portal--management)
18. [API Documentation](#18-api-documentation)
19. [Testing Instructions & Verification Report](#19-testing-instructions--verification-report)
20. [Security & Anti-Hallucination Safeguards](#20-security--anti-hallucination-safeguards)
21. [Troubleshooting Guide](#21-troubleshooting-guide)

---

## 1. Project Overview

CampusHelp acts as an intelligent, 24/7 college information desk. Instead of searching through tens of multi-page PDF documents or queuing outside administrative departments, students can ask conversational questions and receive verified, context-grounded answers immediately.

Every answer is strictly supported by evidence chunks and includes **document citations**, **page numbers**, and **relevance confidence scores**.

---

## 2. Problem Statement

In academic institutions:
- Critical information (fee deadlines, condonation rules, attendance limits, placement eligibility, grading formulas) is dispersed across numerous documents, handbooks, and PDFs.
- Students frequently experience confusion, miss deadlines, or must contact departmental deans for information already codified in documents.
- Standard generative AI chatbots hallucinate policies, hallucinate fees, and cannot provide verified page references.

**CampusHelp solves this** using a hybrid retrieval architecture combining dense vector embeddings, BM25 lexical keyword matching, and cross-encoder reranking.

---

## 3. Key Features

- **Document Ingestion Pipeline**:
  - Validates and parses multiple PDF files via **PyMuPDF (`fitz`)**.
  - Intelligent recursive text splitting with configurable chunk size (~500 tokens) and overlap (~50 tokens).
  - Metadata preservation: document title, page number, department, category, upload date, SHA-256 fingerprint.
  - Automatic duplicate upload detection preventing redundant indexing.
- **Hybrid Retrieval Architecture**:
  - Dense semantic search using **OpenAI `text-embedding-3-small`** (1536 dimensions).
  - Sparse lexical search using **BM25 Okapi (`rank_bm25`)**.
  - **Reciprocal Rank Fusion (RRF)** fusing semantic and lexical rankings.
  - Metadata filtering by department and document category.
- **Cross-Encoder Reranking**:
  - Top 10 hybrid candidate chunks reranked to isolate the 4 most relevant chunks before LLM generation.
- **Strict Context-Grounded Generation**:
  - Configurable LLM (default `gpt-4o-mini`), temperature 0.2.
  - Anti-hallucination guard: If retrieved context is insufficient, responds:
    > *"I couldn't find sufficient information about this in the available college documents. Please contact the concerned department for confirmation."*
  - Prompt injection defense isolating untrusted document content inside XML-delimited blocks.
- **Interactive Student Chat Interface**:
  - Modern, responsive React 18 UI built with Tailwind CSS.
  - Markdown-formatted answers, expandable citation drawer, latency indicator.
  - Thumbs up / thumbs down feedback with comment submission.
  - Conversation history thread sidebar with persistence.
- **Admin Management Portal**:
  - Drag-and-drop multi-file PDF upload dropzone.
  - Document status, page count, chunk count, and deletion / re-indexing controls.
  - Real-time analytics: total queries, latency breakdown, satisfaction rating.
  - Complete query audit trail with latency and citation tracking.
- **Security & RBAC**:
  - Passwords hashed using standard `bcrypt`.
  - JWT-based authentication with role-based access control (`student` vs `admin`).

---

## 4. Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite 6, Tailwind CSS, Axios, Lucide React Icons |
| **Backend API** | Python 3.11/3.12/3.13, FastAPI, Pydantic v2, Uvicorn |
| **Relational DB** | PostgreSQL 16 (Docker) / SQLite 3 (Zero-config local fallback), SQLAlchemy 2.0 ORM |
| **Vector DB** | Qdrant (Docker server & embedded local storage) |
| **PDF Extraction** | PyMuPDF (`fitz`) |
| **Retrieval & RAG**| OpenAI Embeddings (`text-embedding-3-small`), BM25 Okapi, Reciprocal Rank Fusion, Cross-Encoder Reranker |
| **LLM Generation** | OpenAI API (`gpt-4o-mini`), Temperature 0.2 |
| **DevOps & Containers** | Docker, Docker Compose, Nginx Alpine |
| **Testing** | Pytest, Pytest-Asyncio, HTTPX |

---

## 5. System Architecture

```
                                      +---------------------------------------------+
                                      |            CampusHelp Frontend              |
                                      |         React 18 + Vite + Tailwind          |
                                      +----------------------+----------------------+
                                                             |
                                           REST API & JWT    |
                                                             v
+------------------------------------------------------------+-----------------------------------------------------------+
|                                              FastAPI Backend Application                                               |
|                                                                                                                        |
|  +--------------------+   +-------------------+   +--------------------+   +------------------+   +-----------------+  |
|  |    Auth Router     |   |    Chat Router    |   |  Documents Router  |   | Feedback Router  |   |  Admin Router   |  |
|  +--------------------+   +---------+---------+   +---------+----------+   +------------------+   +-----------------+  |
|                                     |                       |                                                          |
|                                     v                       v                                                          |
|                        +------------+------------+     +----+-------------------+                                      |
|                        |   Hybrid RAG Pipeline   |     |    Ingestion Service   |                                      |
|                        +------------+------------+     +----+-------------------+                                      |
|                                     |                       |                                                          |
|           +-------------------------+------+                | (Extract, Chunk, Embed)                                  |
|           |                                |                |                                                          |
|           v                                v                v                                                          |
|  +-------------------+            +------------------+  +-------------------+                                          |
|  |  Qdrant Vector DB |            |  BM25 In-Memory  |  |  PyMuPDF Parser   |                                          |
|  |  (Cosine 1536-dim)|            |  (Rank-BM25)     |  |  & Text Chunker   |                                          |
|  +-------------------+            +------------------+  +-------------------+                                          |
|           |                                |                                                                           |
|           +----------------+---------------+                                                                           |
|                            | (Reciprocal Rank Fusion - Top 10)                                                         |
|                            v                                                                                           |
|               +------------+------------+                                                                              |
|               |  Cross-Encoder Rerank   |                                                                              |
|               |  (Best 4 Chunks)        |                                                                              |
|               +------------+------------+                                                                              |
|                            |                                                                                           |
|                            v                                                                                           |
|               +------------+------------+                                                                              |
|               |   Grounded LLM Prompt   |                                                                              |
|               |   (OpenAI gpt-4o-mini)  |                                                                              |
|               +-------------------------+                                                                              |
+------------------------------------------------------------------------------------------------------------------------+
                               |                                                      |
                               v                                                      v
             +-----------------+-------------------+                +-----------------+-------------------+
             |       PostgreSQL / SQLite Database  |                |       Persistent File Storage       |
             | Users, Docs, Chunks, Logs, Feedback |                | Uploaded PDFs & Extracted Artifacts |
             +-------------------------------------+                +-------------------------------------+
```

---

## 6. RAG Pipeline Workflow

```
[Student Query]
       │
       ▼
1. Query Preprocessing & Normalization
       │
       ├─────────────────────────────────┬─────────────────────────────────┐
       ▼                                                                   ▼
2. Vector Embedding Generation                                   3. BM25 Keyword Search
   (OpenAI text-embedding-3-small)                                  (Tokenized Lexical Matching)
       ▼                                                                   ▼
4. Qdrant Dense Vector Search                                    5. Top BM25 Ranked Candidates
   (Cosine Similarity + Metadata Filters)                           (Filter by Dept / Category)
       │                                                                   │
       └─────────────────────────────────┬─────────────────────────────────┘
                                         ▼
                       6. Reciprocal Rank Fusion (RRF)
                          Combined Score = 1/(60 + r_vec) + 1/(60 + r_bm25)
                                         ▼
                       7. Select Top 10 Fused Candidates
                                         ▼
                       8. Cross-Encoder Reranker
                          Evaluates (Query, Chunk) semantic match
                                         ▼
                       9. Select Top 4 Evidence Chunks
                                         ▼
                       10. Context-Grounded LLM Generation
                           (System Prompt + Delimited Context + Citations)
                                         ▼
                       [Grounded Answer + Citations + Latency Logs]
```

---

## 7. Project Directory Structure

```
CampusHelp/
├── .env.example                       # Root environment variables reference
├── .gitignore                         # Git exclusion rules
├── README.md                          # Comprehensive project documentation
├── docker-compose.yml                 # Multi-container production configuration
├── run_backend.ps1                    # One-click Windows PowerShell backend launcher
├── run_backend.bat                    # One-click Windows Batch backend launcher
├── run_frontend.ps1                   # One-click Windows PowerShell frontend launcher
├── run_frontend.bat                   # One-click Windows Batch frontend launcher
├── backend/
│   ├── Dockerfile                     # Production backend Docker image
│   ├── requirements.txt               # Python package dependencies
│   ├── .env.example                   # Backend environment configuration template
│   ├── seed_sample_docs.py            # Startup seed script for institutional PDFs
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI entrypoint, lifespan, CORS, and routers
│   │   ├── core/
│   │   │   ├── config.py              # Pydantic BaseSettings configuration
│   │   │   ├── logging.py             # Structured logging configuration
│   │   │   └── security.py            # JWT token creation, decoding & bcrypt hashing
│   │   ├── db/
│   │   │   ├── database.py            # SQLAlchemy engine, session maker, SQLite fallback
│   │   │   ├── init_db.py             # Schema initialization & default admin seeder
│   │   │   └── models.py              # User, Document, Chunk, Conversation, Message, Log models
│   │   ├── schemas/
│   │   │   ├── auth.py                # User login, register, token schemas
│   │   │   ├── chat.py                # Chat request, response, citation schemas
│   │   │   ├── document.py            # Document response & upload progress schemas
│   │   │   ├── feedback.py            # Rating and feedback schemas
│   │   │   └── analytics.py           # Dashboard stats & audit log schemas
│   │   ├── services/
│   │   │   ├── ingestion_service.py   # PDF upload, duplicate check, chunking & indexing
│   │   │   ├── analytics_service.py   # Latency stats & query log retrieval
│   │   │   └── rag/
│   │   │       ├── pdf_extractor.py   # PyMuPDF text extraction & cleaning
│   │   │       ├── chunker.py         # Recursive character text splitting
│   │   │       ├── embeddings.py      # OpenAI & deterministic offline embeddings
│   │   │       ├── vector_db.py       # Qdrant client wrapper (Docker / Local)
│   │   │       ├── bm25_retriever.py  # BM25Okapi keyword index & search
│   │   │       ├── reranker.py        # Cross-encoder reranker
│   │   │       ├── hybrid_retriever.py# Hybrid Vector + BM25 + RRF
│   │   │       ├── llm_generator.py   # Grounded prompt, anti-hallucination guard
│   │   │       └── pipeline.py        # Complete RAG pipeline orchestrator
│   │   └── api/
│   │       ├── deps.py                # Auth dependencies (student, admin, optional)
│   │       ├── auth.py                # /auth/register, /auth/login, /auth/me
│   │       ├── chat.py                # /chat, /chat/conversations
│   │       ├── documents.py           # /documents/upload, /documents, /documents/{id}
│   │       ├── feedback.py            # /feedback
│   │       ├── admin.py               # /admin/analytics, /admin/logs
│   │       └── health.py              # /health, /ready probes
│   └── tests/
│       ├── conftest.py                # Pytest fixtures & in-memory test DB
│       ├── test_auth.py               # Authentication and RBAC tests
│       ├── test_pdf_extraction.py     # PyMuPDF parser tests
│       ├── test_chunker.py            # Text splitting and overlap tests
│       ├── test_hybrid_retrieval.py   # BM25, vector search, RRF & reranking tests
│       ├── test_ingestion_e2e.py      # End-to-end PDF upload & duplicate rejection
│       ├── test_rag_quality.py        # 10 comprehensive RAG quality evaluation tests
│       └── generate_sample_docs.py    # ReportLab synthetic college PDF generator
├── frontend/
│   ├── Dockerfile                     # Multi-stage production frontend Docker image
│   ├── nginx.conf                     # Nginx configuration with SPA routing & API proxy
│   ├── package.json                   # React, Tailwind, Lucide dependencies
│   ├── vite.config.js                 # Vite server & backend proxy configuration
│   ├── tailwind.config.js             # Tailwind CSS theme configuration
│   ├── postcss.config.js              # PostCSS plugins
│   ├── index.html                     # HTML root template
│   └── src/
│       ├── main.jsx                   # React DOM entrypoint
│       ├── App.jsx                    # Root application component
│       ├── index.css                  # Tailwind styles and scrollbars
│       ├── api/
│       │   └── client.js              # Axios HTTP client with auth interceptors
│       ├── context/
│       │   └── AuthContext.jsx        # User state, JWT management & role helpers
│       └── components/
│           ├── Navbar.jsx             # Top bar, status indicator, tabs & profile
│           ├── DepartmentFilter.jsx   # Topic domain filter pills
│           ├── ConversationSidebar.jsx# Saved chat threads & new chat button
│           ├── ChatInterface.jsx      # Message thread, welcome hero & prompt input
│           ├── MessageItem.jsx        # Bubble, citations, latency & feedback buttons
│           ├── CitationCard.jsx       # Verified document citation cards
│           ├── AdminDashboard.jsx     # Document upload, stats & query audit logs
│           └── AuthModal.jsx          # Login/Register modal with 1-click demo fill
└── data/
    ├── uploads/                       # Uploaded institutional PDF documents
    └── sample_documents/              # Synthetic institutional reference PDFs
        ├── 1_Academic_Regulations_and_Attendance_Policy.pdf
        ├── 2_Fee_Structure_and_Scholarship_Guidelines_2024.pdf
        ├── 3_Examination_Rules_and_Grading_System.pdf
        ├── 4_Placement_Eligibility_and_Recruitment_Policy.pdf
        └── 5_Campus_Facilities_Hostel_and_Library_Rules.pdf
```

---

## 8. Prerequisites

- **Python**: 3.11, 3.12, or 3.13
- **Node.js**: 18.x, 20.x, or 22.x+ with `npm`
- **Docker & Docker Compose** (Optional, for single-command containerized execution)
- **OpenAI API Key** (For production embeddings and generation; fallback offline synthesizer included for testing)

---

## 9. Installation & Setup

### Step 1: Clone or Open Project in VS Code
```bash
git clone <repository-url>
cd CampusHelp
```

### Step 2: Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(On Windows PowerShell: `Copy-Item .env.example .env`)*

---

## 10. Environment Variables Setup

Edit `.env` to configure your API keys and parameters:

```ini
# Environment
ENV=development
DEBUG=true

# Database (Leave as SQLite for zero-config local run, or PostgreSQL for Docker)
DATABASE_URL=sqlite:///./campushelp.db
# DATABASE_URL=postgresql://campus_user:campus_secure_password_2026@localhost:5432/campushelp

# Security
SECRET_KEY=campushelp_super_secure_jwt_secret_key_change_in_production_2026
ADMIN_DEFAULT_EMAIL=admin@campushelp.edu
ADMIN_DEFAULT_PASSWORD=Admin@CampusHelp2026!

# Qdrant Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=campus_documents

# OpenAI API (Add your key here)
OPENAI_API_KEY=sk-your-openai-api-key-here

# RAG Hyperparameters
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_CANDIDATES=10
RERANK_TOP_K=4
```

> **Note on Offline Development**: If `OPENAI_API_KEY` is not provided, CampusHelp automatically activates its deterministic offline embeddings and grounded synthesizer. The application **will never crash** due to missing API keys.

---

## 11. Docker Startup Instructions

The fastest way to run the complete stack (Postgres, Qdrant, FastAPI, and React):

```bash
# 1. Start all services in the background
docker-compose up -d --build

# 2. View running logs
docker-compose logs -f backend
```

Once started:
- **Frontend Web UI**: http://localhost:3000
- **FastAPI API & Swagger Docs**: http://localhost:8000/docs
- **Qdrant Vector DB Console**: http://localhost:6333/dashboard

To shut down services:
```bash
docker-compose down
```

---

## 12. Manual Startup Instructions (Local VS Code)

You can also run both the backend and frontend locally without Docker in two simple steps:

### Option A: Using Provided Scripts

#### Windows PowerShell:
- **Terminal 1 (Backend)**:
  ```powershell
  .\run_backend.ps1
  ```
- **Terminal 2 (Frontend)**:
  ```powershell
  .\run_frontend.ps1
  ```

#### Windows Command Prompt / Batch:
- Double click or run `run_backend.bat` and `run_frontend.bat`.

---

### Option B: Manual Command Line

#### Terminal 1 — Backend:
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Seed sample institutional documents
python seed_sample_docs.py

# Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*Backend runs at: http://localhost:8000 (OpenAPI docs at http://localhost:8000/docs)*

#### Terminal 2 — Frontend:
```bash
# Navigate to frontend
cd frontend

# Install npm dependencies
npm install

# Start Vite development server
npm run dev
```
*Frontend runs at: http://localhost:5173*

---

## 13. Database Configuration

CampusHelp supports both **PostgreSQL** (production standard) and **SQLite** (local development standard):
- If `DATABASE_URL` starts with `postgresql://`, it connects to PostgreSQL.
- If PostgreSQL is unavailable or `DATABASE_URL` starts with `sqlite:///`, it automatically initializes `campushelp.db` locally.
- Table schemas and the default administrator account (`admin@campushelp.edu`) are automatically created on startup.

---

## 14. Qdrant Vector Database Configuration

CampusHelp automatically detects its vector database environment:
1. **Remote/Docker Server**: If `QDRANT_URL` or `localhost:6333` is detected, it connects via HTTP/gRPC.
2. **Local Embedded Mode**: If no Qdrant server is running, it automatically uses an embedded local database at `backend/qdrant_storage/`.
3. Collection `campus_documents` is configured with **1536-dimensional vectors** and **Cosine Distance**.

---

## 15. PDF Document Ingestion & Seed Data

The project includes 5 synthetic institutional college policy PDFs located in `data/sample_documents/`:
1. `1_Academic_Regulations_and_Attendance_Policy.pdf`: 75% attendance rule, 65% medical condonation, add/drop deadlines.
2. `2_Fee_Structure_and_Scholarship_Guidelines_2024.pdf`: Tuition fee breakdown, August 15 / January 15 deadlines, CGPA merit scholarship bands.
3. `3_Examination_Rules_and_Grading_System.pdf`: CIA vs ESE weightage, 10-point absolute grading scale, supplementary exam rules.
4. `4_Placement_Eligibility_and_Recruitment_Policy.pdf`: CGPA >= 6.50 cutoff, 1 active backlog rule, Dream Offer policy.
5. `5_Campus_Facilities_Hostel_and_Library_Rules.pdf`: 9:30 PM hostel curfew, 4 books / 14 days borrowing quota, 24/7 health center.

To regenerate or re-seed them at any time:
```bash
python backend/seed_sample_docs.py
```

---

## 16. How to Use the Chatbot

1. Open http://localhost:5173 (or http://localhost:3000 in Docker).
2. Click any of the **Suggested Questions** or type your own question in the input box.
3. Example questions to try:
   - *"What is the minimum attendance requirement for semester examinations?"*
   - *"When is the tuition fee payment deadline for the Fall semester?"*
   - *"What is the minimum CGPA and backlog limit required for campus placement?"*
   - *"How many books can undergraduate students borrow from the library and for how long?"*
   - *"What happens if my attendance is 68% due to medical reasons?"*
4. View the AI response with:
   - **Clickable document citations** showing document title, page number, and confidence score.
   - **Expandable Evidence Drawer** revealing the exact textual excerpt retrieved.
   - **Performance Latency** showing retrieval and total response time.
   - **Thumbs Up / Down** feedback buttons.

---

## 17. Admin Portal & Management

1. In the top navigation bar, click **Admin Portal**.
2. If not authenticated, click **Sign In** and select **Demo Admin 🛡️** (or enter `admin@campushelp.edu` / `Admin@CampusHelp2026!`).
3. Inside the Admin Center:
   - **Upload Documents**: Drag and drop any institutional PDF, assign Department and Category, and click **Upload & Index Documents**.
   - **Manage Documents**: Inspect page count, chunk count, and status. Click **Re-index** to refresh vectors or **Delete** to purge from Qdrant and database.
   - **Analytics**: Monitor total queries, satisfaction rating, retrieval latency, and document distributions.
   - **Query Audit Trail**: Review every student query, response latency, and retrieved sources.

---

## 18. API Documentation

Comprehensive Swagger/OpenAPI documentation is available at **http://localhost:8000/docs**.

### Key Endpoints:
- `POST /api/v1/auth/register`: Register new student or admin.
- `POST /api/v1/auth/login`: Authenticate and receive JWT Bearer token.
- `GET /api/v1/auth/me`: Fetch current authenticated profile.
- `POST /api/v1/chat`: Submit user query to RAG pipeline.
- `GET /api/v1/chat/conversations`: List user conversation threads.
- `GET /api/v1/chat/conversations/{id}`: Fetch message history for a thread.
- `POST /api/v1/documents/upload`: Upload and index multiple PDF files (Admin only).
- `GET /api/v1/documents`: List indexed documents with metadata.
- `DELETE /api/v1/documents/{id}`: Delete document and purge vector points (Admin only).
- `POST /api/v1/documents/{id}/reindex`: Re-index document (Admin only).
- `POST /api/v1/feedback`: Submit rating (+1 / -1) and feedback text for a response.
- `GET /api/v1/admin/analytics`: Aggregate usage and latency metrics (Admin only).
- `GET /api/v1/admin/logs`: Query audit logs (Admin only).
- `GET /health`: Liveness probe.
- `GET /ready`: Readiness probe (validates DB and Qdrant connectivity).

---

## 19. Testing Instructions & Verification Report

CampusHelp includes a thorough automated test suite covering unit tests, integration tests, and RAG quality evaluation.

### Running Automated Tests:
```bash
# From workspace root:
.\backend\venv\Scripts\pytest.exe backend\tests -v
```

### Verified Test Matrix (27 Tests, 100% Passing):

| Test File | Test Case | Status | Verified Functionality |
|---|---|:---:|---|
| `test_auth.py` | `test_register_student` | **PASSED** | Student account registration & JWT issuance |
| `test_auth.py` | `test_register_duplicate_email` | **PASSED** | Duplicate email validation |
| `test_auth.py` | `test_login_successful` | **PASSED** | Password verification & token generation |
| `test_auth.py` | `test_login_invalid_password` | **PASSED** | Invalid credential rejection |
| `test_auth.py` | `test_get_current_user_profile` | **PASSED** | Protected route JWT Bearer decoding |
| `test_chunker.py` | `test_chunker_small_text` | **PASSED** | Single chunk boundary handling |
| `test_chunker.py` | `test_chunker_splits_large_text` | **PASSED** | Recursive splitting & overlap preservation |
| `test_pdf_extraction.py` | `test_pdf_extraction_sample_docs` | **PASSED** | PyMuPDF text & page extraction |
| `test_pdf_extraction.py` | `test_pdf_extraction_non_existent`| **PASSED** | Missing file exception handling |
| `test_pdf_extraction.py` | `test_clean_text_normalizes` | **PASSED** | Whitespace & newline normalization |
| `test_hybrid_retrieval.py`| `test_bm25_indexing_and_search` | **PASSED** | BM25 keyword matching & metadata filtering |
| `test_hybrid_retrieval.py`| `test_reranker_prioritizes` | **PASSED** | Cross-encoder reranking priority |
| `test_hybrid_retrieval.py`| `test_vector_db_and_embedding` | **PASSED** | Qdrant point upsert, vector query & delete |
| `test_ingestion_e2e.py` | `test_upload_pdf_admin` | **PASSED** | Multi-page PDF upload & Qdrant indexing |
| `test_ingestion_e2e.py` | `test_upload_duplicate_pdf` | **PASSED** | SHA-256 duplicate document detection |
| `test_ingestion_e2e.py` | `test_upload_pdf_student_forbidden`| **PASSED**| Role-based authorization enforcement |
| `test_ingestion_e2e.py` | `test_list_documents` | **PASSED** | Document metadata listing |
| `test_rag_quality.py` | `test_scenario_1_direct_factual` | **PASSED** | Factual question with page citation |
| `test_rag_quality.py` | `test_scenario_2_multiple_docs` | **PASSED** | Multi-document synthesis |
| `test_rag_quality.py` | `test_scenario_3_numerical_fees` | **PASSED** | Numerical extraction (tuition fee amounts & dates) |
| `test_rag_quality.py` | `test_scenario_4_placement_criteria`| **PASSED**| Eligibility rules (CGPA & backlogs) |
| `test_rag_quality.py` | `test_scenario_5_attendance_condonation`| **PASSED**| Attendance medical certificate deadline |
| `test_rag_quality.py` | `test_scenario_6_multiple_chunks` | **PASSED** | Multi-chunk aggregation |
| `test_rag_quality.py` | `test_scenario_7_out_of_domain` | **PASSED** | Anti-hallucination fallback triggered |
| `test_rag_quality.py` | `test_scenario_8_ambiguous_question`| **PASSED**| Robust handling of vague queries |
| `test_rag_quality.py` | `test_scenario_9_irrelevant_question`| **PASSED**| Irrelevant query handling |
| `test_rag_quality.py` | `test_scenario_10_prompt_injection`| **PASSED**| Prompt injection neutralization |

---

## 20. Security & Anti-Hallucination Safeguards

1. **Anti-Hallucination Mandate**:
   When the retrieved document context does not contain sufficient facts to answer a question, the LLM is constrained to output the exact institutional fallback message:
   > *"I couldn't find sufficient information about this in the available college documents. Please contact the concerned department for confirmation."*
2. **Prompt Injection Protection**:
   Retrieved chunks are parsed as untrusted strings inside `<document_chunk>` blocks. System prompts explicitly instruct the model to ignore any instructions inside document text attempting to override assistant behavior or leak keys.
3. **Password Security**:
   Passwords are salted and hashed using `bcrypt` (12 rounds) before persistence.
4. **Role-Based Access Control**:
   All document ingestion, deletion, re-indexing, and analytics endpoints strictly enforce `admin` role checks via FastAPI dependencies.
5. **Duplicate Document Prevention**:
   Every uploaded file is checked against existing SHA-256 hashes to prevent redundant vector storage and duplicate search candidates.

---

## 21. Troubleshooting Guide

| Issue | Likely Cause | Solution |
|---|---|---|
| `Qdrant connection refused on localhost:6333` | Qdrant container is not running | The system automatically falls back to local embedded Qdrant (`qdrant_storage`). To use the server, run `docker-compose up -d qdrant`. |
| `OpenAI API key error or rate limit` | Missing or invalid key | Add your key in `.env`. CampusHelp automatically uses the offline context synthesizer if no key is configured. |
| `Port 8000 already in use` | Another process is occupying port 8000 | Kill the existing process: `Stop-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess` |
| `Port 5173 already in use` | Another Vite server is running | Vite will automatically offer port 5174, or stop the existing dev server. |
| `Duplicate document detected during upload` | Same PDF file was already uploaded | File already exists in the vector index. You can re-index or delete the existing document from the Admin Portal. |

---

## License & Credits

Built for college student empowerment and institutional efficiency. Developed with FastAPI, React, Qdrant, and OpenAI RAG architecture.
