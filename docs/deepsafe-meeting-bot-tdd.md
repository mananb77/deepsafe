# DeepSafe Meeting Bot — Technical Design Document

**Document ID:** DS-TDD-001
**Version:** 1.0
**Status:** Draft
**Last Updated:** 2026-02-23
**Owner:** Engineering
**Classification:** Internal — Confidential

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Architecture](#2-system-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Service Decomposition](#4-service-decomposition)
5. [Data Architecture](#5-data-architecture)
6. [API Design](#6-api-design)
7. [Detection Pipeline](#7-detection-pipeline)
8. [Verification System](#8-verification-system)
9. [Stream Processing Pipeline](#9-stream-processing-pipeline)
10. [Workflow & Policy Engine](#10-workflow--policy-engine)
11. [Platform Integrations](#11-platform-integrations)
12. [Frontend Architecture](#12-frontend-architecture)
13. [Security Architecture](#13-security-architecture)
14. [Infrastructure & Deployment](#14-infrastructure--deployment)
15. [Observability](#15-observability)
16. [Performance Engineering](#16-performance-engineering)
17. [Failure Modes & Resilience](#17-failure-modes--resilience)
18. [Testing Strategy](#18-testing-strategy)
19. [Migration & Data Management](#19-migration--data-management)
20. [ADRs (Architecture Decision Records)](#20-adrs)

---

## 1. Introduction

### 1.1 Purpose

This document describes the technical architecture, design decisions, data models, and implementation details for the DeepSafe meeting bot platform. It serves as the authoritative reference for the engineering team and is intended to be a living document updated as the system evolves.

### 1.2 Scope

This TDD covers the full production system:
- Meeting bot service (Zoom, Google Meet)
- Real-time detection pipeline (audio, video, social engineering)
- Multi-channel verification service
- Workflow and policy engine
- Security dashboard (frontend)
- API gateway
- Data layer
- Infrastructure and deployment

### 1.3 Audience

- Backend engineers
- Frontend engineers
- ML/AI engineers
- DevOps / SRE
- Security engineers
- Engineering managers

### 1.4 Related Documents

| Document | Description |
|---|---|
| DS-PRD-001 | Product Requirements Document |
| `backend/src/` | Source code (source of truth for implementation details) |
| `deepsafe-app/src/` | Frontend source code |
| `backend/docker-compose.yml` | Local development environment |
| `.github/workflows/backend-ci.yml` | CI/CD pipeline definition |

---

## 2. System Architecture

### 2.1 Architecture Style

DeepSafe uses a **modular monolith** architecture deployed as a set of co-located services within a single repository. Services communicate via:
- **In-process calls** for synchronous operations (API → Detection → Risk Aggregation)
- **RabbitMQ message queues** for asynchronous work (stream chunks → detection tasks → alert generation)
- **Redis pub/sub** for real-time event broadcast (risk score updates → WebSocket → dashboard)

This hybrid approach provides the operational simplicity of a monolith with the logical separation of microservices, allowing the team to decompose into independently deployable services later as scale demands.

### 2.2 High-Level Architecture

```
                    ┌─────────────────────────────┐
                    │        VIDEO PLATFORMS        │
                    │   Zoom SDK │ Google Meet API  │
                    └──────────┬──────────────────┘
                               │
                     Audio/Video Streams
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                    MEETING BOT SERVICE                            │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Zoom Bot    │  │ GMeet Bot   │  │ Lifecycle│  │ Metadata │  │
│  │ (SDK)       │  │ (Puppeteer) │  │ Manager  │  │ Collector│  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┘  └──────────┘  │
│         └────────┬───────┘                                       │
│                  │                                               │
└──────────────────┼───────────────────────────────────────────────┘
                   │
          Audio chunks (3s) + Video frames (5 FPS)
                   │
                   ▼
┌──────────────────────────────────────────────────────────────────┐
│                  STREAM PROCESSING PIPELINE                      │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Audio Buffer │  │ Video Frame  │  │ Analysis Pipeline    │  │
│  │ Manager      │  │ Queue        │  │ (Orchestrator)       │  │
│  │ (Ring Buffer)│  │ (FIFO Queue) │  │                      │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                      │               │
│         └─────────────────┴──────────────────────┘               │
│                           │                                      │
└───────────────────────────┼──────────────────────────────────────┘
                            │
               Celery Tasks (via RabbitMQ)
                            │
        ┌───────────────────┼────────────────────┐
        │                   │                    │
        ▼                   ▼                    ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐
│ Audio        │  │ Video        │  │ Social Engineering   │
│ Detection    │  │ Detection    │  │ Detection            │
│              │  │              │  │                      │
│ • Resemble   │  │ • Sensity    │  │ • Scenario Match     │
│ • Spectral   │  │ • Landmarks  │  │ • Keyword Scan       │
│ • Prosody    │  │ • Micro-Expr │  │ • GPT-4 Analysis     │
│ • Wav2Vec    │  │ • Lighting   │  │ • Participant Valid.  │
│   (fallback) │  │ • Efficient  │  │ • Metadata Anomaly   │
│              │  │   Net (fb)   │  │ • Behavioral         │
└──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘
       │                 │                      │
       └─────────────────┴──────────────────────┘
                         │
                         ▼
              ┌────────────────────┐
              │  RISK AGGREGATOR   │
              │                    │
              │  Composite Score   │
              │  0–100% + Level    │
              └─────────┬──────────┘
                        │
           ┌────────────┼─────────────┐
           │            │             │
           ▼            ▼             ▼
    ┌────────────┐ ┌──────────┐ ┌──────────────┐
    │ Alert      │ │ Policy   │ │ WebSocket    │
    │ Generator  │ │ Engine   │ │ Broadcast    │
    └────────────┘ └─────┬────┘ └──────────────┘
                         │                │
                         ▼                ▼
              ┌──────────────────┐  ┌─────────────┐
              │ VERIFICATION     │  │  DASHBOARD   │
              │ SERVICE          │  │  (React)     │
              │                  │  │              │
              │ • SMS (Twilio)   │  │ • Meetings   │
              │ • Voice (Twilio) │  │ • Incidents  │
              │ • Push (FCM)     │  │ • Profiles   │
              │ • Email          │  │ • Policies   │
              └──────────────────┘  └─────────────┘
                                          │
┌─────────────────────────────────────────┼────────────────────────┐
│                     DATA LAYER          │                        │
│                                         │                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ PostgreSQL   │  │ Redis        │  │ MongoDB      │          │
│  │              │  │              │  │              │          │
│  │ Users        │  │ Sessions     │  │ Transcripts  │          │
│  │ Companies    │  │ Active Mtgs  │  │ Forensic     │          │
│  │ Meetings     │  │ Pending Vfy  │  │ Evidence     │          │
│  │ Incidents    │  │ Rate Limits  │  │ Analysis     │          │
│  │ Policies     │  │ Cache        │  │ Results      │          │
│  │ Audit Logs   │  │              │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐                             │
│  │ RabbitMQ     │  │ S3           │                             │
│  │              │  │              │                             │
│  │ Task Queues  │  │ Recordings   │                             │
│  │ Event Fanout │  │ Evidence     │                             │
│  └──────────────┘  └──────────────┘                             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 2.3 Design Principles

| Principle | Implementation |
|---|---|
| **Fail open on detection, fail closed on verification** | If a detection API is unavailable, we flag as "unverified" (not "clean"). If a verification channel fails, the transaction stays blocked. |
| **Async by default** | All detection tasks are Celery tasks dispatched via RabbitMQ. The stream processor never blocks waiting for a detection result. |
| **Idempotent operations** | Verification triggers and policy actions use idempotency keys. Duplicate messages are safely ignored. |
| **Correlation IDs** | Every request generates a correlation ID (`X-Request-ID`) propagated through logs, traces, and message headers for end-to-end tracing. |
| **Configuration over code** | Risk thresholds, detection weights, verification timeouts, and policy rules are configurable per tenant without code changes. |

---

## 3. Technology Stack

### 3.1 Backend

| Component | Technology | Version | Rationale |
|---|---|---|---|
| Language | Python | 3.11+ | ML ecosystem compatibility, async support, team expertise |
| API Framework | FastAPI | 0.109+ | Async-native, auto-OpenAPI docs, Pydantic validation, high performance |
| ORM | SQLAlchemy | 2.0+ | Mature, async support, migration tooling (Alembic) |
| Validation | Pydantic | 2.5+ | FastAPI-native, fast validation, schema generation |
| Task Queue | Celery | 5.3+ | Mature distributed task system, RabbitMQ + Redis backends |
| Message Broker | RabbitMQ | 3.12+ | Reliable message delivery, routing flexibility, management UI |
| ASGI Server | Uvicorn | 0.25+ | High-performance ASGI server for FastAPI |
| Process Manager | Gunicorn | 21+ | Multi-worker process management wrapping Uvicorn |
| Logging | structlog | — | Structured JSON logging with context binding |

### 3.2 Databases

| Database | Version | Purpose | Justification |
|---|---|---|---|
| PostgreSQL | 15 | Primary relational store | ACID compliance, JSONB support, mature ecosystem, row-level security |
| Redis | 7 | Cache, sessions, real-time state | Sub-millisecond reads, pub/sub for WebSocket broadcast, sorted sets for rate limiting |
| MongoDB | 6 | Document storage | Flexible schema for transcripts, forensic evidence, ML analysis outputs |

**Why three databases?**
- PostgreSQL handles structured, relational data (users, meetings, incidents) where referential integrity and transactional guarantees matter.
- Redis handles ephemeral, high-frequency data (active meeting state, pending verifications, session tokens) where speed matters more than durability.
- MongoDB handles large, semi-structured documents (meeting transcripts, detection result payloads, forensic evidence packages) where schema flexibility and document-level queries matter.

### 3.3 AI/ML

| Technology | Purpose | Provider |
|---|---|---|
| Resemble AI Detect API | Audio deepfake detection (primary) | Resemble AI |
| Sensity / GetReal API | Video deepfake detection (primary) | Sensity |
| OpenAI GPT-4 | Social engineering semantic analysis, intent classification | OpenAI |
| Wav2Vec 2.0 | Audio deepfake detection (local fallback) | Meta/Facebook Research |
| EfficientNet-B4 | Video deepfake detection (local fallback, fine-tuned on FaceForensics++) | Google Research |
| PyTorch | Local model inference runtime | PyTorch |
| Hugging Face Transformers | Model loading and inference utilities | Hugging Face |

### 3.4 External Services

| Service | Provider | Purpose |
|---|---|---|
| SMS delivery | Twilio | OTP codes for verification |
| Voice calls | Twilio | IVR callback verification |
| Push notifications | Firebase Cloud Messaging | Mobile app biometric verification |
| Email | SendGrid | Verification emails, reports |
| SSO | Okta, Azure AD, Google Workspace | Enterprise identity + directory sync |
| SIEM | Splunk, Datadog | Security event export |

### 3.5 Frontend

| Component | Technology | Version | Rationale |
|---|---|---|---|
| Framework | React | 19+ | Component model, ecosystem, team expertise |
| Language | TypeScript | 5.9+ | Type safety, better DX, refactoring confidence |
| UI Library | Material-UI (MUI) | 7+ | Enterprise-grade component library, accessibility, theming |
| State Management | Redux Toolkit | 2.11+ | Predictable state, devtools, RTK Query for API caching |
| Server State | React Query (TanStack) | 5+ | Async data fetching, caching, background refetching |
| Build | Vite | 7+ | Fast dev server, ESM-native, optimized builds |
| Animation | Framer Motion | 12+ | Declarative animations, gesture support |
| Charts | Recharts | 3+ | React-native charting for dashboard metrics |
| Styling | Emotion | — | CSS-in-JS, MUI default styling engine |

### 3.6 Infrastructure

| Component | Technology | Purpose |
|---|---|---|
| Containers | Docker | Application packaging, consistent environments |
| Orchestration (dev) | Docker Compose | Local development stack |
| Orchestration (prod) | Kubernetes | Production container orchestration |
| Serverless | AWS Lambda | Event-driven functions (webhook handlers, scheduled jobs) |
| CDN | CloudFront / CloudFlare | Static asset delivery, DDoS protection |
| Object Storage | AWS S3 | Meeting recordings, forensic evidence, report exports |
| Secrets | AWS Secrets Manager | API keys, database credentials, JWT secrets |
| DNS | Route 53 / CloudFlare | DNS management, failover |

---

## 4. Service Decomposition

### 4.1 Service Map

```
backend/src/
├── services/
│   ├── api/                    # API Gateway Service
│   │   ├── main.py             # FastAPI application factory
│   │   ├── routers/            # Route handlers per domain
│   │   │   ├── auth.py         # POST /login, /refresh, /logout
│   │   │   ├── meetings.py     # CRUD + real-time meeting endpoints
│   │   │   ├── participants.py # Participant management + risk profiles
│   │   │   ├── incidents.py    # Incident lifecycle management
│   │   │   ├── verifications.py# Verification trigger + status
│   │   │   ├── policies.py     # Policy CRUD
│   │   │   ├── companies.py    # Company configuration
│   │   │   ├── users.py        # User profile management
│   │   │   └── health.py       # Health checks + metrics
│   │   ├── middleware/         # Auth, CORS, rate limiting, logging
│   │   ├── dependencies/       # FastAPI dependency injection
│   │   └── websocket/          # WebSocket connection manager
│   │
│   ├── detection/              # Detection Engine Service
│   │   ├── audio/              # Audio deepfake detection
│   │   │   ├── resemble_detector.py   # Resemble AI API client
│   │   │   ├── spectral_analyzer.py   # Frequency-domain analysis
│   │   │   ├── prosody_analyzer.py    # Speech rhythm analysis
│   │   │   ├── av_sync_detector.py    # Audio-video synchronization
│   │   │   └── wav2vec_detector.py    # Local fallback model
│   │   ├── video/              # Video deepfake detection
│   │   │   ├── sensity_detector.py    # Sensity API client
│   │   │   ├── facial_landmark.py     # Landmark geometry analysis
│   │   │   ├── micro_expression.py    # Temporal micro-expression
│   │   │   ├── lighting_analyzer.py   # Illumination consistency
│   │   │   └── efficientnet_detector.py # Local fallback model
│   │   ├── social_engineering/ # Social engineering detection
│   │   │   ├── scenario_detector.py   # Pattern matching (500+ scenarios)
│   │   │   ├── keyword_analyzer.py    # Real-time keyword scanning
│   │   │   ├── gpt4_analyzer.py       # GPT-4 semantic analysis
│   │   │   ├── participant_validator.py # Identity cross-reference
│   │   │   ├── metadata_analyzer.py   # Timing/location anomalies
│   │   │   └── behavioral_analyzer.py # Pressure/isolation tactics
│   │   └── risk_aggregator.py  # Composite score calculation
│   │
│   ├── verification/           # Verification Service
│   │   ├── orchestrator.py     # Channel selection + session management
│   │   ├── sms_verifier.py     # Twilio SMS integration
│   │   ├── voice_verifier.py   # Twilio Voice/IVR integration
│   │   ├── push_verifier.py    # Firebase FCM integration
│   │   ├── email_verifier.py   # SendGrid integration
│   │   └── session_manager.py  # Verification session state machine
│   │
│   ├── stream/                 # Stream Processing Pipeline
│   │   ├── processor.py        # Main stream orchestrator
│   │   ├── audio_buffer.py     # Ring buffer for audio chunks
│   │   ├── video_queue.py      # FIFO queue for video frames
│   │   ├── pipeline.py         # Analysis pipeline coordinator
│   │   ├── alert_generator.py  # Alert creation from risk scores
│   │   └── detection_tasks.py  # Celery task definitions
│   │
│   ├── workflow/               # Workflow & Policy Engine
│   │   ├── engine.py           # Workflow orchestrator
│   │   ├── rule_evaluator.py   # Policy rule evaluation
│   │   ├── action_dispatcher.py # Action execution (alert/verify/block)
│   │   └── default_policies.py # Pre-configured policy templates
│   │
│   └── integration/            # Platform Integration Service
│       ├── zoom/               # Zoom Meeting SDK integration
│       ├── google_meet/        # Google Meet API integration
│       └── calendar/           # Calendar sync (Google, Outlook)
│
├── integrations/               # External service clients
│   ├── zoom/                   # Zoom OAuth, webhooks, SDK wrapper
│   ├── google_meet/            # Google OAuth, Calendar, Meet API
│   └── teams/                  # Microsoft Bot Framework (future)
│
├── shared/                     # Shared libraries
│   ├── models/                 # SQLAlchemy ORM models
│   ├── schemas/                # Pydantic request/response schemas
│   ├── config/                 # Settings management (Pydantic BaseSettings)
│   ├── security/               # JWT, hashing, RBAC utilities
│   ├── database/               # Database session management
│   └── utils/                  # Common utilities
│
└── migrations/                 # Alembic database migrations
    └── versions/               # Migration scripts
```

### 4.2 Service Responsibilities

| Service | Owns | Depends On | Communicates Via |
|---|---|---|---|
| **API Service** | HTTP endpoints, WebSocket, request validation, response serialization | All other services, PostgreSQL, Redis | Synchronous function calls (in-process) |
| **Detection Service** | Audio/video analysis, social engineering scoring, risk aggregation | External APIs (Resemble, Sensity, OpenAI), PyTorch models | Celery tasks (async via RabbitMQ) |
| **Verification Service** | OOB identity verification, session lifecycle, channel delivery | Twilio, Firebase, SendGrid, PostgreSQL | Celery tasks (async via RabbitMQ) |
| **Stream Service** | Audio buffering, video queuing, pipeline orchestration, alert generation | Detection Service, Risk Aggregator | Celery tasks (async via RabbitMQ) |
| **Workflow Service** | Policy evaluation, action dispatch, approval workflows | Verification Service, API Service | In-process calls + Celery tasks |
| **Integration Service** | Platform bot management, OAuth flows, calendar sync | Zoom SDK, Google APIs, PostgreSQL | Webhooks (inbound), API calls (outbound) |

### 4.3 Dependency Graph

```
                 ┌─────────────┐
                 │ API Service  │
                 └──────┬───────┘
                        │ depends on
          ┌─────────────┼──────────────┐
          │             │              │
          ▼             ▼              ▼
   ┌────────────┐ ┌──────────┐ ┌────────────┐
   │ Detection  │ │ Workflow │ │ Integration│
   │ Service    │ │ Service  │ │ Service    │
   └─────┬──────┘ └────┬─────┘ └─────┬──────┘
         │              │             │
         │              ▼             │
         │      ┌──────────────┐      │
         │      │ Verification │      │
         │      │ Service      │      │
         │      └──────────────┘      │
         │                            │
         ▼                            ▼
   ┌────────────┐              ┌────────────┐
   │ Stream     │              │ Platform   │
   │ Service    │              │ SDKs       │
   └────────────┘              └────────────┘
```

---

## 5. Data Architecture

### 5.1 PostgreSQL Schema

#### 5.1.1 Entity Relationship Diagram

```
┌──────────────────┐         ┌──────────────────┐
│    companies     │─── 1:N ─│      users       │
│                  │         │                  │
│ id          (PK) │         │ id          (PK) │
│ name             │         │ company_id  (FK) │
│ domain           │         │ email            │
│ subscription_tier│         │ hashed_password  │
│ settings   (JSON)│         │ first_name       │
│ sso_config (JSON)│         │ last_name        │
│ integrations     │         │ role             │
│ created_at       │         │ phone_number     │
│ updated_at       │         │ is_active        │
└───────┬──────────┘         │ last_login       │
        │                    └──────────────────┘
        │ 1:N
        ▼
┌──────────────────┐         ┌──────────────────┐
│    meetings      │─── 1:N ─│  participants    │
│                  │         │                  │
│ id          (PK) │         │ id          (PK) │
│ company_id  (FK) │         │ meeting_id  (FK) │
│ platform         │         │ user_id     (FK) │
│ platform_mtg_id  │         │ name             │
│ title            │         │ email            │
│ url              │         │ ip_address       │
│ status           │         │ device_info(JSON)│
│ scheduled_start  │         │ risk_scores(JSON)│
│ actual_start     │         │ trust_level      │
│ actual_end       │         │ is_flagged       │
│ risk_score       │         │ is_verified      │
│ peak_risk_score  │         │ joined_at        │
│ risk_level       │         │ left_at          │
│ bot_joined_at    │         └──────┬───────────┘
│ bot_left_at      │                │
│ participant_count│                │ 1:N
│ has_recording    │                ▼
│ has_transcript   │         ┌──────────────────┐
└───────┬──────────┘         │ risk_indicators  │
        │                    │                  │
        │ 1:N                │ id          (PK) │
        ▼                    │ meeting_id  (FK) │
┌──────────────────┐         │ participant_id(FK│
│   incidents      │         │ type             │
│                  │         │ confidence       │
│ id          (PK) │         │ evidence   (JSON)│
│ meeting_id  (FK) │         │ timestamp        │
│ participant_id(FK│         └──────────────────┘
│ type             │
│ severity         │         ┌──────────────────┐
│ status           │         │  verifications   │
│ risk_score       │         │                  │
│ evidence   (JSON)│         │ id          (PK) │
│ detected_at      │         │ session_id  (UQ) │
│ resolved_at      │         │ user_id     (FK) │
│ resolved_by      │         │ incident_id (FK) │
└──────────────────┘         │ channel          │
                             │ status           │
┌──────────────────┐         │ code             │
│    policies      │         │ attempts         │
│                  │         │ expires_at       │
│ id          (PK) │         │ verified_at      │
│ company_id  (FK) │         └──────────────────┘
│ name             │
│ description      │         ┌──────────────────┐
│ rules      (JSON)│         │   audit_logs     │
│ actions    (JSON)│         │                  │
│ is_active        │         │ id          (PK) │
│ created_at       │         │ user_id     (FK) │
│ updated_at       │         │ action           │
└──────────────────┘         │ resource_type    │
                             │ resource_id      │
                             │ changes    (JSON)│
                             │ ip_address       │
                             │ timestamp        │
                             └──────────────────┘
```

#### 5.1.2 Key Schema Details

**meetings.status** — Enum values:
- `scheduled` — Calendar-synced, bot not yet joined
- `in_progress` — Bot is active in meeting
- `completed` — Meeting ended normally
- `cancelled` — Meeting cancelled before start

**meetings.risk_level** — Enum values:
- `low` (0–30%)
- `medium` (31–60%)
- `high` (61–85%)
- `critical` (86–100%)

**incidents.incident_type** (`IncidentType`) — Enum values:
- `audio_deepfake` — Synthetic voice detected
- `video_deepfake` — Face manipulation detected
- `social_engineering` — Manipulation pattern detected
- `impersonation` — Identity impersonation attempt
- `unauthorized_access` — Unauthorized meeting access
- `suspicious_behavior` — Anomalous behavioral pattern
- `verification_failed` — Identity verification failure
- `policy_violation` — Policy rule breach

**incidents.severity** (`IncidentSeverity`) — Enum values:
- `low` — Minor anomaly, logged for reference
- `medium` — Elevated risk, monitor closely (default)
- `high` — High risk, verification recommended
- `critical` — Immediate intervention required

**incidents.status** (`IncidentStatus`) — Enum values:
- `detected` — Automatically created by detection engine
- `investigating` — Analyst has opened the incident
- `verified` — Confirmed as a real threat
- `false_positive` — Analyst determined no real threat
- `resolved` — Investigation complete, action taken

**users.role** (`UserRole`) — Enum values:
- `admin` — Full access to all features, settings, user management
- `security_analyst` — Access to meetings, incidents, participants; no settings or user management
- `user` — Standard platform access
- `viewer` — Read-only dashboard access

**Indexes:**
```sql
-- High-frequency queries
CREATE INDEX idx_meetings_company_status ON meetings(company_id, status);
CREATE INDEX idx_meetings_status ON meetings(status) WHERE status = 'in_progress';
CREATE INDEX idx_incidents_meeting ON incidents(meeting_id);
CREATE INDEX idx_incidents_status ON incidents(status) WHERE status IN ('detected', 'investigating');
CREATE INDEX idx_participants_meeting ON participants(meeting_id);
CREATE INDEX idx_audit_logs_user_ts ON audit_logs(user_id, timestamp DESC);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
```

### 5.2 Redis Data Model

| Key Pattern | Type | TTL | Purpose |
|---|---|---|---|
| `session:{user_id}` | Hash | 7 days | User session data (JWT refresh token, last activity) |
| `meeting:active:{meeting_id}` | Hash | Meeting duration + 1h | Active meeting state (current risk score, participant list, bot status) |
| `meeting:risk:{meeting_id}` | Sorted Set | Meeting duration + 1h | Time-series risk scores (score=risk, member=timestamp) |
| `verify:pending:{session_id}` | Hash | 10 min | Pending verification (code, channel, attempts, expires_at) |
| `rate_limit:verify:{user_id}` | String (counter) | 1 hour | Verification rate limiting (max 10 resends/hour) |
| `rate_limit:api:{ip}` | String (counter) | 1 minute | API rate limiting (requests per minute) |
| `cache:participant:{email}` | Hash | 1 hour | Participant profile cache (directory lookup result) |
| `ws:connections:{meeting_id}` | Set | Meeting duration | WebSocket connection IDs subscribed to meeting updates |

### 5.3 MongoDB Collections

| Collection | Document Structure | Purpose |
|---|---|---|
| `transcripts` | `{ meeting_id, segments: [{ speaker, text, timestamp, risk_flags }] }` | Full meeting transcripts with per-segment risk annotations |
| `detection_results` | `{ meeting_id, participant_id, detector, result_payload, timestamp }` | Raw detection API response payloads for forensic analysis |
| `forensic_packages` | `{ incident_id, audio_clips, video_clips, transcript_excerpts, metadata }` | Complete evidence packages for incident investigation |

---

## 6. API Design

### 6.1 API Conventions

| Convention | Detail |
|---|---|
| **Base URL** | `https://api.deepsafe.io/api/v1` |
| **Auth** | `Authorization: Bearer <jwt_access_token>` |
| **Content Type** | `application/json` (request and response) |
| **Versioning** | URL-based (`/api/v1/`, `/api/v2/`) |
| **Pagination** | Cursor-based: `?cursor=<opaque>&limit=50` |
| **Filtering** | Query parameters: `?status=in_progress&risk_level=high` |
| **Sorting** | `?sort=-created_at` (prefix `-` for descending) |
| **Error format** | `{ "detail": "message", "code": "ERROR_CODE", "field": "field_name" }` |
| **Rate limiting** | `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` headers |

### 6.2 Authentication Endpoints

```
POST   /api/v1/auth/login
       Body: { "email": "...", "password": "..." }
       Response: { "access_token": "...", "refresh_token": "...", "expires_in": 900 }

POST   /api/v1/auth/refresh
       Body: { "refresh_token": "..." }
       Response: { "access_token": "...", "expires_in": 900 }

POST   /api/v1/auth/logout
       Headers: Authorization: Bearer <token>
       Response: 204 No Content
```

**Token lifecycle:**
- Access token: JWT, 15-minute expiry, contains `user_id`, `company_id`, `role`, `permissions`
- Refresh token: Opaque string, 7-day expiry, stored in Redis, single-use (rotation on refresh)

### 6.3 Core Resource Endpoints

#### Meetings

```
GET    /api/v1/meetings                    # List meetings (paginated, filterable)
GET    /api/v1/meetings/active             # List active meetings only
GET    /api/v1/meetings/{id}               # Meeting detail
POST   /api/v1/meetings                    # Create/register meeting for monitoring
PUT    /api/v1/meetings/{id}               # Update meeting status
GET    /api/v1/meetings/{id}/incidents     # Incidents for this meeting
GET    /api/v1/meetings/{id}/transcript    # Meeting transcript
GET    /api/v1/meetings/{id}/participants  # Participants in this meeting
```

#### Participants

```
GET    /api/v1/participants                # List all participants
GET    /api/v1/participants/{id}           # Participant detail + risk profile
GET    /api/v1/participants/{id}/history   # Meeting attendance history
```

#### Incidents

```
GET    /api/v1/incidents                   # List incidents (paginated, filterable)
GET    /api/v1/incidents/stats             # Aggregated incident statistics
GET    /api/v1/incidents/{id}              # Incident detail with evidence
POST   /api/v1/incidents/{id}/resolve      # Resolve incident
POST   /api/v1/incidents/{id}/escalate     # Escalate to security team
POST   /api/v1/incidents/{id}/false-positive  # Mark as false positive
```

#### Verifications

```
POST   /api/v1/verifications               # Initiate verification
GET    /api/v1/verifications/{session_id}/status  # Check status
POST   /api/v1/verifications/{session_id}/verify  # Submit verification code
POST   /api/v1/verifications/{session_id}/resend  # Resend code
POST   /api/v1/verifications/{session_id}/cancel  # Cancel verification
```

#### Policies

```
GET    /api/v1/policies                    # List active policies
POST   /api/v1/policies                    # Create policy
PUT    /api/v1/policies/{id}               # Update policy
DELETE /api/v1/policies/{id}               # Delete policy
```

### 6.4 WebSocket API

```
WS     /api/v1/ws/meetings/{meeting_id}

# Client → Server messages:
{ "type": "subscribe", "meeting_id": "..." }
{ "type": "unsubscribe", "meeting_id": "..." }

# Server → Client messages:
{ "type": "risk_update", "meeting_id": "...", "risk_score": 0.72, "risk_level": "high", "timestamp": "..." }
{ "type": "incident_created", "incident": { ... } }
{ "type": "participant_joined", "participant": { ... } }
{ "type": "participant_left", "participant_id": "..." }
{ "type": "verification_update", "session_id": "...", "status": "verified" }
```

**Connection management:**
- JWT authentication on WebSocket upgrade handshake
- Ping/pong keepalive every 30 seconds
- Auto-reconnect client-side with exponential backoff
- Connection state tracked in Redis set per meeting

### 6.5 Webhook Callbacks (Inbound)

```
POST   /api/v1/webhooks/zoom              # Zoom meeting events
POST   /api/v1/webhooks/twilio/sms        # Twilio SMS delivery/reply
POST   /api/v1/webhooks/twilio/voice      # Twilio Voice call status
```

All webhook endpoints validate request signatures using provider-specific HMAC verification.

---

## 7. Detection Pipeline

### 7.1 Audio Deepfake Detection

#### 7.1.1 Processing Flow

```
Audio Chunk (3 sec, 16kHz PCM)
         │
         ├──────────────────────────────┐
         │                              │
         ▼                              ▼
┌─────────────────────┐      ┌─────────────────────┐
│ Resemble AI API     │      │ Local Analyzers      │
│ (Primary)           │      │ (Parallel)           │
│                     │      │                      │
│ POST /detect        │      │ • Spectral Analysis  │
│ Returns: {          │      │   - FFT frequency    │
│   score: 0.0-1.0,   │      │   - Formant patterns │
│   label: "..."      │      │   - Noise floor      │
│ }                   │      │                      │
│                     │      │ • Prosody Analysis   │
│ Timeout: 3s         │      │   - Pitch contour    │
│ Fallback: Wav2Vec   │      │   - Speech rate      │
│                     │      │   - Pause patterns   │
└─────────┬───────────┘      └─────────┬───────────┘
          │                            │
          └────────────┬───────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Score Fusion    │
              │                 │
              │ Weighted avg:   │
              │ Resemble: 0.50  │
              │ Spectral: 0.25  │
              │ Prosody:  0.25  │
              │                 │
              │ If Resemble down│
              │ → Wav2Vec: 0.50 │
              │ → Spectral:0.25 │
              │ → Prosody: 0.25 │
              └────────┬────────┘
                       │
                       ▼
              Audio Deepfake Score
              (0.0 – 1.0)
```

#### 7.1.2 Resemble AI Integration

```python
# Pseudocode for Resemble AI client
class ResembleDetector:
    """Primary audio deepfake detection via Resemble AI API."""

    API_ENDPOINT = "https://api.resemble.ai/v1/detect"
    TIMEOUT_SECONDS = 3
    CIRCUIT_BREAKER_THRESHOLD = 5  # consecutive failures

    async def detect(self, audio_chunk: bytes) -> DetectionResult:
        """
        Send audio chunk to Resemble AI for deepfake analysis.

        Args:
            audio_chunk: 3-second PCM audio, 16kHz, 16-bit

        Returns:
            DetectionResult with score (0.0-1.0) and label

        Fallback:
            On timeout or circuit breaker open → Wav2Vec local model
        """
        try:
            response = await self.client.post(
                self.API_ENDPOINT,
                files={"audio": audio_chunk},
                timeout=self.TIMEOUT_SECONDS
            )
            return DetectionResult(
                detector="resemble_ai",
                score=response["probability"],
                label=response["label"],
                confidence=response["confidence"],
                raw_response=response
            )
        except (TimeoutError, CircuitBreakerOpen):
            return await self.wav2vec_fallback.detect(audio_chunk)
```

#### 7.1.3 Audio-Video Sync Detection

```
┌──────────────────────────────────────────────────┐
│  A/V Sync Detector                                │
│                                                    │
│  Input: Audio chunk + corresponding video frames   │
│                                                    │
│  Method:                                           │
│  1. Extract lip movement timeline from video       │
│  2. Extract speech onset timeline from audio       │
│  3. Compute cross-correlation                      │
│  4. Measure drift in milliseconds                  │
│                                                    │
│  Threshold: 42ms                                   │
│  • < 42ms drift → Normal (network jitter)          │
│  • 42–100ms drift → Suspicious (score: 0.3–0.6)   │
│  • > 100ms drift → Likely synthetic (score: 0.8+)  │
│                                                    │
│  Special case: Virtual camera detected →           │
│    weight A/V sync 2× (known deepfake delivery)    │
└──────────────────────────────────────────────────┘
```

### 7.2 Video Deepfake Detection

#### 7.2.1 Processing Flow

```
Video Frame Batch (5 frames at 5 FPS = 1 second)
         │
         ├──────────────────────────────┐
         │                              │
         ▼                              ▼
┌─────────────────────┐      ┌─────────────────────┐
│ Sensity/GetReal API │      │ Local Analyzers      │
│ (Primary)           │      │ (Parallel)           │
│                     │      │                      │
│ POST /analyze       │      │ • Facial Landmarks   │
│ Returns: {          │      │   - 68-point geometry │
│   manipulation:     │      │   - Symmetry analysis│
│     score, type     │      │   - Boundary artifacts│
│ }                   │      │                      │
│                     │      │ • Micro-Expressions  │
│ Timeout: 3s         │      │   - FACS AU tracking │
│ Fallback:           │      │   - Temporal smoothness│
│   EfficientNet-B4   │      │                      │
│                     │      │ • Lighting Analysis  │
│                     │      │   - Per-region illum. │
│                     │      │   - Shadow direction  │
│                     │      │   - Specular reflect. │
└─────────┬───────────┘      └─────────┬───────────┘
          │                            │
          └────────────┬───────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Score Fusion    │
              │                 │
              │ Sensity:   0.50 │
              │ Landmarks: 0.20 │
              │ Micro-Exp: 0.15 │
              │ Lighting:  0.15 │
              └────────┬────────┘
                       │
                       ▼
              Video Deepfake Score
              (0.0 – 1.0)
```

#### 7.2.2 Virtual Camera Detection

The system detects known virtual camera software that is commonly used as a delivery mechanism for deepfake video:

| Software | Detection Method |
|---|---|
| OBS Virtual Camera | Device enumeration name matching |
| Snap Camera | Process name / device metadata |
| ManyCam | Device name / driver signature |
| mmhmm | Device name matching |
| XSplit VCam | Device name matching |
| DeepFaceLive | Process detection (known deepfake tool) |

Detection of virtual camera software does not automatically mean deepfake. It raises the participant's risk score by a configurable multiplier (default: 1.2×) and is logged as a `virtual_camera` risk indicator.

### 7.3 Social Engineering Detection

#### 7.3.1 6-Metric Scoring Architecture

```
Meeting Transcript (rolling 5-minute window)
         │
         ├───────┬───────┬───────┬───────┬───────┐
         │       │       │       │       │       │
         ▼       ▼       ▼       ▼       ▼       ▼
      ┌─────┐┌─────┐┌─────┐┌─────┐┌─────┐┌─────┐
      │  A  ││  B  ││  C  ││  D  ││  E  ││  F  │
      │     ││     ││     ││     ││     ││     │
      │Scen.││Keyw.││GPT-4││Part.││Meta.││Behv.│
      │ 20% ││ 20% ││ 20% ││ 15% ││ 10% ││ 15% │
      └──┬──┘└──┬──┘└──┬──┘└──┬──┘└──┬──┘└──┬──┘
         │      │      │      │      │      │
         └──────┴──────┴──────┴──────┴──────┘
                          │
                          ▼
                 Social Engineering Score
                 (0.0 – 1.0)

Composite formula:
SE_Score = (A × 0.20) + (B × 0.20) + (C × 0.20)
         + (D × 0.15) + (E × 0.10) + (F × 0.15)
```

#### 7.3.2 GPT-4 Semantic Analysis (Metric C)

```python
# GPT-4 prompt structure (simplified)
SYSTEM_PROMPT = """
You are a social engineering detection system.
Analyze the following meeting transcript segment for manipulation tactics.

Respond in JSON:
{
  "risk_score": 0.0-1.0,
  "intent_classification": "legitimate|suspicious|malicious",
  "tactics_detected": ["urgency", "authority", "isolation", ...],
  "financial_request": {
    "detected": true/false,
    "amount": null or number,
    "type": "wire_transfer|payment|invoice|other",
    "recipient": "..."
  },
  "reasoning": "...",
  "recommended_action": "monitor|alert|verify|block"
}
"""
```

**Rate limiting:** GPT-4 calls are batched per meeting (one call per 60-second transcript window, not per utterance) to manage API costs and latency.

**Cost estimate:** ~$0.05 per analysis call × ~60 calls per hour-long meeting = ~$3/meeting for GPT-4 analysis.

### 7.4 Risk Aggregation

#### 7.4.1 Composite Score Calculation

```python
class RiskAggregator:
    """Compute composite risk score from all detection signals.

    Uses a 3-component model:
    - Deepfake score (audio + video combined): 40% weight
    - Social engineering score: 40% weight
    - Virtual camera detection: 20% weight

    Within the deepfake component, audio and video are weighted equally (50/50).
    """

    # Top-level component weights
    WEIGHT_DEEPFAKE = 0.40
    WEIGHT_SOCIAL_ENGINEERING = 0.40
    WEIGHT_VIRTUAL_CAMERA = 0.20

    # Within deepfake, audio/video weights
    WEIGHT_AUDIO = 0.50
    WEIGHT_VIDEO = 0.50

    # Risk thresholds (score is 0–100)
    THRESHOLD_LOW = 30.0
    THRESHOLD_MEDIUM = 60.0
    THRESHOLD_HIGH = 85.0

    # Action thresholds
    ACTION_ALERT_THRESHOLD = 40.0
    ACTION_VERIFY_THRESHOLD = 65.0
    ACTION_INTERVENE_THRESHOLD = 85.0

    RISK_LEVELS = {
        (0.0, 30.0):   "low",
        (30.1, 60.0):  "medium",
        (60.1, 85.0):  "high",
        (85.1, 100.0): "critical",
    }

    def compute(self, audio_score: float, video_score: float,
                social_eng_score: float, virtual_camera: bool) -> AggregatedRiskResult:
        deepfake_score = (audio_score * self.WEIGHT_AUDIO
                          + video_score * self.WEIGHT_VIDEO)
        vc_score = 100.0 if virtual_camera else 0.0

        composite = (deepfake_score * self.WEIGHT_DEEPFAKE
                     + social_eng_score * self.WEIGHT_SOCIAL_ENGINEERING
                     + vc_score * self.WEIGHT_VIRTUAL_CAMERA)
        composite = min(composite, 100.0)

        level = self._classify(composite)
        actions = self._determine_actions(composite)
        return AggregatedRiskResult(
            composite_risk_score=composite, risk_level=level,
            deepfake_score=deepfake_score,
            social_engineering_score=social_eng_score,
            audio_deepfake_score=audio_score,
            video_deepfake_score=video_score,
            virtual_camera_detected=virtual_camera,
            recommended_actions=actions, ...
        )
```

#### 7.4.2 Temporal Smoothing

Risk scores use an exponential moving average (EMA) to prevent flickering:

```
smoothed_score[t] = α × raw_score[t] + (1 - α) × smoothed_score[t-1]

where α = 0.3 (configurable)
```

This ensures that a single noisy detection doesn't spike the score, but sustained signals cause the score to rise steadily.

---

## 8. Verification System

### 8.1 Verification Orchestrator

```
┌──────────────────────────────────────────────────────────────────┐
│                   VERIFICATION ORCHESTRATOR                       │
│                                                                   │
│  Input: RiskScore + TransactionContext                            │
│                                                                   │
│  1. Look up risk-based channel matrix                             │
│  2. Resolve target user from corporate directory                  │
│  3. Generate verification session (UUID)                          │
│  4. Generate OTP code (6-digit, crypto-random)                    │
│  5. Dispatch to selected channels IN PARALLEL                     │
│  6. Start expiry timer (10 min default)                           │
│  7. Await response on any channel                                 │
│                                                                   │
│  Outcomes:                                                        │
│  • VERIFIED — User confirmed identity                             │
│  • DENIED   — User reported fraud                                 │
│  • EXPIRED  — No response within timeout                          │
│  • FAILED   — Max attempts exceeded                               │
│                                                                   │
│  Post-verification:                                               │
│  • Update meeting risk score                                      │
│  • Update participant trust level                                 │
│  • Notify policy engine of verification result                    │
│  • Log to audit trail                                             │
└──────────────────────────────────────────────────────────────────┘
```

### 8.2 Verification Session State Machine

```
                    ┌─────────┐
                    │ PENDING │
                    └────┬────┘
                         │ send()
                         ▼
                    ┌─────────┐
                    │  SENT   │
                    └────┬────┘
                         │ delivery_confirmed()
                         ▼
                    ┌───────────┐
            ┌───── │ DELIVERED │ ─────┐
            │      └─────┬─────┘      │
            │            │            │
    timeout │     verify()│    max_attempts
            │            │            │
            ▼            ▼            ▼
     ┌──────────┐ ┌──────────┐ ┌──────────┐
     │ EXPIRED  │ │ VERIFIED │ │  FAILED  │
     └──────────┘ └──────────┘ └──────────┘
```

**Note:** There is no explicit `DENIED` status in the verification model. When a user replies "NO" to an SMS or presses 2 (fraud) on the IVR callback, the verification is marked `FAILED` and a separate fraud alert incident is created with `incident_type=impersonation`. This separation ensures the verification model tracks channel delivery state while incident management handles threat response.

### 8.3 Channel Implementations

#### 8.3.1 SMS (Twilio)

```python
class SMSVerifier:
    """Send verification codes via Twilio SMS."""

    async def send(self, session: VerificationSession) -> None:
        message = self.twilio_client.messages.create(
            body=self._format_message(session),
            from_=settings.TWILIO_PHONE_NUMBER,
            to=session.target_phone,
            status_callback=f"{settings.BASE_URL}/api/v1/webhooks/twilio/sms"
        )
        session.external_id = message.sid
        session.status = VerificationStatus.SENT

    async def handle_reply(self, from_number: str, body: str) -> None:
        """Handle inbound SMS reply (YES/NO/code)."""
        session = await self.find_session_by_phone(from_number)
        if body.strip().upper() == "NO":
            await self.deny(session)  # Trigger fraud alert
        elif body.strip().upper() == "YES" or self.validate_code(session, body):
            await self.verify(session)
        else:
            session.attempts += 1
            if session.attempts >= 5:
                await self.fail(session)
```

#### 8.3.2 Voice Callback (Twilio IVR)

```
IVR Flow:
1. "This is DeepSafe Security."
2. "Someone is requesting authorization for a $[amount]
    [transaction_type] in a video meeting."
3. "Press 1 if you are in this meeting and authorize."
   "Press 2 if you are NOT in this meeting — this is fraud."
   "Press 3 to speak with IT security."
4a. [1] → "Please say the verification phrase: [phrase]"
    → Voice biometric comparison
    → Match → VERIFIED
    → No match → "Verification failed. Connecting to IT security."
4b. [2] → DENIED → Fraud alert triggered immediately
4c. [3] → Transfer to security team phone number
```

#### 8.3.3 Push Notification (Firebase)

```json
{
  "notification": {
    "title": "DeepSafe Verification Required",
    "body": "Wire transfer request of $60,000 needs your approval"
  },
  "data": {
    "type": "verification_request",
    "session_id": "uuid-...",
    "meeting_title": "Q4 Finance Review",
    "requester": "Mary Johnson",
    "action": "Wire transfer $60,000",
    "actions": ["approve", "deny"]
  }
}
```

Mobile app receives push → presents biometric challenge (Face ID / Touch ID) → sends result back to API via `POST /api/v1/verifications/{session_id}/verify`.

---

## 9. Stream Processing Pipeline

### 9.1 Pipeline Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    STREAM PROCESSOR                             │
│                    (Main Orchestrator)                          │
│                                                                │
│  For each active meeting:                                      │
│                                                                │
│  1. Meeting Bot → Audio chunks (3s) + Video frames (5 FPS)     │
│  2. Audio Buffer Manager receives chunks                       │
│  3. Video Frame Queue receives frames                          │
│  4. Analysis Pipeline dispatches detection tasks               │
│  5. Detection results aggregated by Risk Aggregator            │
│  6. Alert Generator evaluates risk thresholds                  │
│  7. Alerts pushed via WebSocket + policy engine triggered       │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### 9.2 Audio Buffer Manager

```python
@dataclass
class AudioBufferConfig:
    """Configuration for audio buffer."""
    chunk_duration_ms: int = 3000       # 3 seconds per chunk
    overlap_ms: int = 500               # 500ms overlap between chunks
    sample_rate: int = 16000            # 16kHz
    channels: int = 1                   # Mono
    bits_per_sample: int = 16
    max_buffer_duration_ms: int = 30000 # Max 30 seconds buffered
    min_chunk_duration_ms: int = 1000   # Min 1 second for analysis


class AudioBufferManager:
    """Sliding-window audio buffer for per-participant audio chunking.

    Design:
    - Audio frames are accumulated into a bytearray
    - When accumulated data reaches chunk_duration_ms, a chunk is extracted
    - 500ms overlap between consecutive chunks ensures continuity
    - Max 30 seconds of audio buffered per participant
    - Thread-safe with threading.Lock (not asyncio — used in sync context)

    Tested: 30 tests passing
    """

    def __init__(self, participant_id: str, config: AudioBufferConfig = None):
        self.participant_id = participant_id
        self.config = config or AudioBufferConfig()
        self._buffer = bytearray()
        self._lock = threading.Lock()
        self._chunk_count = 0

    def add_frames(self, audio_data: bytes) -> None:
        """Append raw audio frames to the buffer."""
        with self._lock:
            self._buffer.extend(audio_data)
            # Trim to max buffer size
            max_bytes = int(self.config.max_buffer_duration_ms
                            * self.config.bytes_per_ms)
            if len(self._buffer) > max_bytes:
                self._buffer = self._buffer[-max_bytes:]

    def extract_chunk(self) -> Optional[bytes]:
        """Extract a chunk when enough data has accumulated.

        Returns chunk_duration_ms of audio, retaining overlap_ms
        at the start of the buffer for the next chunk.
        """
        with self._lock:
            chunk_bytes = self.config.chunk_size_bytes
            if len(self._buffer) < chunk_bytes:
                return None
            chunk = bytes(self._buffer[:chunk_bytes])
            # Keep overlap for continuity
            overlap_bytes = self.config.overlap_size_bytes
            self._buffer = self._buffer[chunk_bytes - overlap_bytes:]
            self._chunk_count += 1
            return chunk
```

### 9.3 Video Frame Queue

```python
@dataclass
class VideoFrameConfig:
    """Configuration for video frame queue."""
    sample_fps: int = 2             # Target frames per second for analysis
    max_queue_size: int = 30        # Max frames in queue per participant
    max_total_queue_size: int = 100 # Max total frames across all participants
    analysis_interval_ms: int = 1000  # Min time between analyses
    prioritize_screen_share: bool = True
    prefer_keyframes: bool = True
    min_frame_interval_ms: int = 400  # Min 400ms between sampled frames
    max_width: int = 1920
    max_height: int = 1080


class VideoFrameQueue:
    """Intelligent video frame queue with downsampling.

    Design:
    - Source video (e.g., 30 FPS) is downsampled to 2 FPS for analysis
    - Per-participant queues with max 30 frames each
    - Global queue limit of 100 frames across all participants
    - Intelligent frame selection: prefers keyframes, respects min interval
    - Screen share frames can be prioritized
    - Thread-safe with threading.Lock

    Key difference from audio: video uses intelligent selection
    rather than fixed-interval chunking, because not every frame
    is equally useful for deepfake detection.
    """

    def __init__(self, config: VideoFrameConfig = None):
        self.config = config or VideoFrameConfig()
        self._queues: Dict[str, Deque[QueuedFrame]] = {}
        self._lock = threading.Lock()
        self._last_sample_time: Dict[str, float] = {}
        self._total_frames = 0

    def should_sample(self, participant_id: str, timestamp_ms: float) -> bool:
        """Determine if this frame should be sampled based on FPS target."""
        min_interval = self.config.sample_interval_ms  # 500ms at 2 FPS
        last = self._last_sample_time.get(participant_id, 0)
        return (timestamp_ms - last) >= min_interval

    def enqueue(self, participant_id: str, frame: VideoFrame) -> bool:
        """Add a frame to the participant's queue if sampling criteria met."""
        with self._lock:
            if self._total_frames >= self.config.max_total_queue_size:
                self._evict_oldest()
            queue = self._queues.setdefault(
                participant_id,
                deque(maxlen=self.config.max_queue_size)
            )
            queue.append(QueuedFrame(frame=frame))
            self._total_frames += 1
            return True

    def get_frames(self, participant_id: str,
                   count: int = 5) -> List[VideoFrame]:
        """Get up to `count` frames for analysis."""
        with self._lock:
            queue = self._queues.get(participant_id, deque())
            frames = []
            for _ in range(min(count, len(queue))):
                frames.append(queue.popleft().frame)
                self._total_frames -= 1
            return frames
```

### 9.4 Detection Task Dispatch (Celery)

```python
# Celery task definitions for async detection

@celery_app.task(
    bind=True,
    max_retries=2,
    default_retry_delay=1,
    time_limit=10,
    soft_time_limit=8
)
def analyze_audio_chunk(self, meeting_id: str, participant_id: str,
                        audio_data: bytes, timestamp: float):
    """Async task: Run audio deepfake detection on a single chunk."""
    try:
        result = audio_detection_service.detect(audio_data)
        risk_aggregator.update_signal(
            meeting_id, participant_id,
            signal="audio_deepfake",
            score=result.score,
            timestamp=timestamp
        )
        return result.to_dict()
    except ExternalAPIError as exc:
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, time_limit=10)
def analyze_video_batch(self, meeting_id: str, participant_id: str,
                        frames: list[bytes], timestamp: float):
    """Async task: Run video deepfake detection on a frame batch."""
    ...


@celery_app.task(bind=True, max_retries=1, time_limit=15)
def analyze_transcript_segment(self, meeting_id: str,
                               transcript_window: str, timestamp: float):
    """Async task: Run social engineering detection on transcript."""
    ...
```

### 9.5 Alert Generator

```python
class AlertGenerator:
    """Generate alerts based on risk score changes.

    Rules:
    - Score crosses from below to above HIGH threshold → generate alert
    - Score crosses from HIGH to CRITICAL → generate escalation alert
    - Score sustained above CRITICAL for 60s → generate intervention alert
    - Score drops below MEDIUM → generate "risk reduced" notification

    Tested: 28 tests passing (10 in progress)
    """

    THRESHOLDS = {
        "high": 0.61,
        "critical": 0.86,
    }

    SUSTAINED_CRITICAL_SECONDS = 60

    async def evaluate(self, meeting_id: str, participant_id: str,
                       risk_score: RiskScore) -> list[Alert]:
        alerts = []
        previous = await self.get_previous_score(meeting_id, participant_id)

        # Threshold crossing detection
        if previous.score < self.THRESHOLDS["high"] <= risk_score.score:
            alerts.append(Alert(
                type="risk_threshold_crossed",
                severity="high",
                meeting_id=meeting_id,
                participant_id=participant_id,
                message=f"Risk score exceeded HIGH threshold: {risk_score.score:.0%}",
                recommended_action="verify"
            ))

        if previous.score < self.THRESHOLDS["critical"] <= risk_score.score:
            alerts.append(Alert(
                type="risk_threshold_crossed",
                severity="critical",
                meeting_id=meeting_id,
                participant_id=participant_id,
                message=f"CRITICAL risk detected: {risk_score.score:.0%}",
                recommended_action="intervene"
            ))

        return alerts
```

### 9.6 Latency Budget

```
┌────────────────────────────────────────────────────────────────┐
│                  END-TO-END LATENCY BUDGET                      │
│                                                                  │
│  Target: < 5 seconds from capture to dashboard alert             │
│                                                                  │
│  ┌──────────────────────┐                                        │
│  │ Audio capture + buffer│ 50ms                                  │
│  ├──────────────────────┤                                        │
│  │ Queue dispatch        │ 20ms                                  │
│  ├──────────────────────┤                                        │
│  │ Celery task pickup    │ 100ms                                 │
│  ├──────────────────────┤                                        │
│  │ Detection API call    │ 1500ms (p95)                          │
│  │ (Resemble/Sensity)    │                                       │
│  ├──────────────────────┤                                        │
│  │ Local analyzers       │ 500ms (parallel with API)             │
│  ├──────────────────────┤                                        │
│  │ Risk aggregation      │ 50ms                                  │
│  ├──────────────────────┤                                        │
│  │ Alert evaluation      │ 20ms                                  │
│  ├──────────────────────┤                                        │
│  │ WebSocket broadcast   │ 50ms                                  │
│  ├──────────────────────┤                                        │
│  │ Dashboard render      │ 100ms                                 │
│  ├──────────────────────┤                                        │
│  │ BUFFER                │ ~2610ms remaining                     │
│  └──────────────────────┘                                        │
│                                                                  │
│  Total: ~2390ms typical, ~5000ms worst case                      │
└────────────────────────────────────────────────────────────────┘
```

---

## 10. Workflow & Policy Engine

### 10.1 Policy Rule Schema

```json
{
  "id": "policy-001",
  "name": "High-value wire transfer protection",
  "company_id": "company-uuid",
  "is_active": true,
  "rules": [
    {
      "condition": {
        "operator": "AND",
        "clauses": [
          { "field": "risk_score", "op": ">=", "value": 0.60 },
          { "field": "social_engineering.financial_request.detected", "op": "==", "value": true },
          { "field": "social_engineering.financial_request.amount", "op": ">=", "value": 10000 }
        ]
      },
      "actions": [
        {
          "type": "verify",
          "channels": ["sms", "callback"],
          "target_role": "CFO",
          "timeout_minutes": 10
        },
        {
          "type": "alert",
          "channels": ["dashboard", "email", "slack"],
          "recipients": ["security_team"]
        },
        {
          "type": "block",
          "scope": "transaction",
          "until": "verification_complete"
        }
      ]
    }
  ]
}
```

### 10.2 Rule Evaluation Engine

```python
class RuleEvaluator:
    """Evaluate policy rules against detection context.

    The evaluator supports:
    - Nested AND/OR conditions
    - Numeric comparisons (>=, <=, ==, !=, >, <)
    - String matching (==, contains, regex)
    - Boolean checks
    - Nested field access (dot notation)
    """

    def evaluate(self, rule: PolicyRule, context: DetectionContext) -> bool:
        if rule.condition.operator == "AND":
            return all(
                self._evaluate_clause(clause, context)
                for clause in rule.condition.clauses
            )
        elif rule.condition.operator == "OR":
            return any(
                self._evaluate_clause(clause, context)
                for clause in rule.condition.clauses
            )

    def _evaluate_clause(self, clause: Clause, context: DetectionContext) -> bool:
        value = self._resolve_field(clause.field, context)
        return self._compare(value, clause.op, clause.value)
```

### 10.3 Action Dispatcher

```
Policy Rule Match
        │
        ▼
┌──────────────────────────────────────────────────┐
│              ACTION DISPATCHER                    │
│                                                   │
│  Receives: list[Action] from rule evaluation      │
│                                                   │
│  Dispatches (in parallel where independent):      │
│                                                   │
│  ┌─────────┐                                      │
│  │ ALERT   │ → Dashboard notification             │
│  │         │ → Email to security team              │
│  │         │ → Slack webhook                       │
│  │         │ → In-meeting host alert               │
│  └─────────┘                                      │
│                                                   │
│  ┌─────────┐                                      │
│  │ VERIFY  │ → Verification Orchestrator           │
│  │         │   (select channels, send codes)       │
│  └─────────┘                                      │
│                                                   │
│  ┌─────────┐                                      │
│  │ BLOCK   │ → Transaction gate activated          │
│  │         │   (hold until verification complete)  │
│  └─────────┘                                      │
│                                                   │
│  ┌──────────┐                                     │
│  │ ESCALATE │ → PagerDuty / Opsgenie alert         │
│  │          │ → Security team SMS                   │
│  │          │ → Management notification             │
│  └──────────┘                                     │
└──────────────────────────────────────────────────┘
```

### 10.4 Default Policy Templates

The system ships with pre-configured policies that customers can enable and customize:

| Template | Trigger | Action |
|---|---|---|
| **Wire Fraud Protection** | risk_score >= 60% AND financial_request.amount >= $10K | Verify (SMS + callback) + Block transaction |
| **Executive Impersonation** | deepfake_audio >= 70% AND participant.role in [CEO, CFO, CTO] | Verify (all channels) + Alert security + Block |
| **First-Time Vendor Payment** | participant.is_first_time AND financial_request.detected | Verify (SMS) + Alert finance team |
| **After-Hours Emergency** | meeting.is_outside_business_hours AND financial_request.detected | Verify (SMS + callback) + Alert + 24h hold |
| **Multi-Signal Alert** | high_confidence_signals >= 3 | Escalate to security team + Block all actions |

---

## 11. Platform Integrations

### 11.1 Zoom Integration

```
┌────────────────────────────────────────────────────────────────┐
│                     ZOOM INTEGRATION                            │
│                                                                 │
│  ┌─────────────────┐                                           │
│  │ Zoom OAuth 2.0  │                                           │
│  │                 │                                           │
│  │ • Client ID     │                                           │
│  │ • Client Secret │                                           │
│  │ • Scopes:       │                                           │
│  │   - meeting:read│                                           │
│  │   - meeting:write│                                          │
│  │   - user:read   │                                           │
│  └────────┬────────┘                                           │
│           │                                                     │
│  ┌────────▼────────┐     ┌──────────────────┐                  │
│  │ Zoom Bot (SDK)  │────▶│ Stream Capture   │                  │
│  │                 │     │                  │                  │
│  │ • Joins meeting │     │ • Raw audio API  │                  │
│  │ • Silent mode   │     │ • Video stream   │                  │
│  │ • Appears as    │     │ • Per-participant │                  │
│  │   "DeepSafe"    │     │   isolation      │                  │
│  └─────────────────┘     └──────────────────┘                  │
│                                                                 │
│  ┌──────────────────┐    ┌──────────────────┐                  │
│  │ Zoom Webhooks    │    │ Zoom Apps SDK    │                  │
│  │                  │    │ (In-Meeting UI)  │                  │
│  │ • meeting.started│    │                  │                  │
│  │ • meeting.ended  │    │ • Trust badges   │                  │
│  │ • participant.   │    │ • Host alerts    │                  │
│  │   joined/left    │    │ • Risk overlay   │                  │
│  └──────────────────┘    └──────────────────┘                  │
└────────────────────────────────────────────────────────────────┘
```

### 11.2 Google Meet Integration

```
┌────────────────────────────────────────────────────────────────┐
│                   GOOGLE MEET INTEGRATION                       │
│                                                                 │
│  ┌─────────────────┐                                           │
│  │ Google OAuth 2.0│                                           │
│  │                 │                                           │
│  │ • Client ID     │                                           │
│  │ • Client Secret │                                           │
│  │ • Service Acct  │                                           │
│  │ • Scopes:       │                                           │
│  │   - calendar    │                                           │
│  │   - meet        │                                           │
│  └────────┬────────┘                                           │
│           │                                                     │
│  ┌────────▼────────┐     ┌──────────────────┐                  │
│  │ Meet Bot        │────▶│ Stream Capture   │                  │
│  │ (Puppeteer)     │     │                  │                  │
│  │                 │     │ • Browser audio  │                  │
│  │ • Headless      │     │   capture API    │                  │
│  │   Chrome        │     │ • Screen capture │                  │
│  │ • Joins via     │     │   for video      │                  │
│  │   meeting link  │     │ • Web Audio API  │                  │
│  └─────────────────┘     └──────────────────┘                  │
│                                                                 │
│  ┌──────────────────┐                                          │
│  │ Calendar Sync    │                                          │
│  │                  │                                          │
│  │ • Watch for new  │                                          │
│  │   meetings       │                                          │
│  │ • Auto-schedule  │                                          │
│  │   bot joins      │                                          │
│  └──────────────────┘                                          │
└────────────────────────────────────────────────────────────────┘
```

### 11.3 Platform Abstraction Layer

All platform-specific logic is behind an abstract interface:

```python
class MeetingBot(ABC):
    """Abstract base class for platform-specific meeting bots."""

    @abstractmethod
    async def join(self, meeting_url: str) -> None: ...

    @abstractmethod
    async def leave(self) -> None: ...

    @abstractmethod
    async def get_audio_stream(self) -> AsyncIterator[AudioChunk]: ...

    @abstractmethod
    async def get_video_stream(self) -> AsyncIterator[VideoFrame]: ...

    @abstractmethod
    async def get_participants(self) -> list[Participant]: ...

    @abstractmethod
    async def get_metadata(self) -> MeetingMetadata: ...


class ZoomMeetingBot(MeetingBot): ...
class GoogleMeetBot(MeetingBot): ...
class TeamsMeetingBot(MeetingBot): ...  # Future
```

---

## 12. Frontend Architecture

### 12.1 Application Structure

```
deepsafe-app/src/
├── App.tsx                     # Root component, routing, providers
├── pages/
│   ├── Dashboard.tsx           # Main dashboard (overview)
│   ├── MeetingHistory.tsx      # Meeting list + filters
│   ├── MeetingDetail.tsx       # Single meeting deep-dive
│   ├── ParticipantHistory.tsx  # Participant list + profiles
│   ├── ParticipantDetail.tsx   # Single participant profile
│   ├── Incidents.tsx           # Incident management
│   ├── IncidentDetail.tsx      # Single incident investigation
│   ├── Policies.tsx            # Policy management
│   ├── Settings.tsx            # Admin settings
│   └── Login.tsx               # Authentication
│
├── components/
│   ├── layout/
│   │   ├── Header.tsx          # Top nav + theme toggle + notifications
│   │   ├── Sidebar.tsx         # Side navigation
│   │   └── PageLayout.tsx      # Standard page wrapper
│   ├── features/
│   │   ├── dashboard/          # Dashboard-specific components
│   │   ├── meetings/           # Meeting list, detail components
│   │   ├── participants/       # Participant cards, profiles
│   │   └── incidents/          # Incident cards, evidence viewer
│   └── common/
│       ├── RiskBadge.tsx       # Color-coded risk level badge
│       ├── TrustBadge.tsx      # Participant trust indicator
│       ├── RiskIndicator.tsx   # Visual risk score display
│       ├── MetricCard.tsx      # Dashboard metric card
│       └── DataTable.tsx       # Filterable, sortable data table
│
├── features/
│   └── Walkthrough/            # Onboarding tutorial system
│
├── hooks/
│   ├── useWebSocket.ts         # WebSocket connection management
│   ├── useMeetings.ts          # Meeting data fetching (React Query)
│   ├── useIncidents.ts         # Incident data fetching
│   └── useAuth.ts              # Authentication state
│
├── services/
│   └── api.ts                  # API client (axios/fetch wrapper)
│
├── store/
│   └── index.ts                # Redux store configuration
│
├── types/
│   ├── meeting.ts              # Meeting TypeScript interfaces
│   ├── participant.ts          # Participant interfaces
│   ├── incident.ts             # Incident interfaces
│   └── api.ts                  # API response types
│
├── theme/
│   ├── colors.ts               # Brand color palette
│   ├── gradients.ts            # Gradient definitions
│   └── index.ts                # MUI theme configuration
│
└── context/
    └── ThemeContext.tsx         # Light/dark mode toggle
```

### 12.2 Design System

#### 12.2.1 Brand Colors

| Name | Hex | Usage |
|---|---|---|
| Deep Safe Blue | `#1F3C88` | Primary brand, headers, navigation |
| Signal Teal | `#1FB6A6` | Success states, verified badges, positive metrics |
| Threat Red | `#D64545` | Critical alerts, high-risk badges, error states |
| Warning Amber | `#F5A623` | Medium risk, warnings, pending states |
| Neutral Gray | `#6B7280` | Secondary text, borders, inactive states |

#### 12.2.2 Risk Badge Mapping

| Risk Level | Color | Badge Text |
|---|---|---|
| Low (0–30%) | Green (`#1FB6A6`) | "Low Risk" |
| Medium (31–60%) | Amber (`#F5A623`) | "Medium Risk" |
| High (61–85%) | Orange (`#E67E22`) | "High Risk" |
| Critical (86–100%) | Red (`#D64545`) | "Critical" |

### 12.3 State Management Strategy

| Data Type | Management | Rationale |
|---|---|---|
| **Server state** (meetings, incidents, participants) | React Query (TanStack Query) | Automatic caching, background refetching, stale-while-revalidate |
| **Real-time state** (active meeting risk scores, live incidents) | WebSocket → Redux store | Need immediate, push-based updates; Redux for predictable state |
| **UI state** (filters, modals, theme) | React local state / Context | Component-scoped, no persistence needed |
| **Auth state** (tokens, user info) | Redux store + localStorage | Persist across page refreshes; need global access |

### 12.4 WebSocket Integration

```typescript
// hooks/useWebSocket.ts
function useMeetingWebSocket(meetingId: string) {
  const dispatch = useDispatch();

  useEffect(() => {
    const ws = new WebSocket(
      `${WS_BASE_URL}/api/v1/ws/meetings/${meetingId}`
    );

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);

      switch (message.type) {
        case "risk_update":
          dispatch(updateMeetingRisk(message));
          break;
        case "incident_created":
          dispatch(addIncident(message.incident));
          queryClient.invalidateQueries(["incidents"]);
          break;
        case "participant_joined":
          dispatch(addParticipant(message.participant));
          break;
        case "verification_update":
          dispatch(updateVerification(message));
          break;
      }
    };

    return () => ws.close();
  }, [meetingId]);
}
```

---

## 13. Security Architecture

### 13.1 Authentication Flow

```
┌──────────┐          ┌──────────────┐          ┌─────────────┐
│  Client  │          │   API        │          │   Redis     │
│  (React) │          │   Service    │          │             │
└────┬─────┘          └──────┬───────┘          └──────┬──────┘
     │                       │                         │
     │  POST /auth/login     │                         │
     │  {email, password}    │                         │
     ├──────────────────────▶│                         │
     │                       │  Verify password        │
     │                       │  (bcrypt, 12 rounds)    │
     │                       │                         │
     │                       │  Generate JWT           │
     │                       │  (access: 15 min)       │
     │                       │                         │
     │                       │  Generate refresh token │
     │                       │  (opaque, 7 days)       │
     │                       │                         │
     │                       │  Store refresh ──────▶ │
     │                       │  in Redis               │
     │                       │                         │
     │  {access_token,       │                         │
     │   refresh_token}      │                         │
     │◀──────────────────────│                         │
     │                       │                         │
```

### 13.2 JWT Token Structure

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user-uuid",
    "company_id": "company-uuid",
    "role": "analyst",
    "permissions": ["meetings:read", "incidents:read", "incidents:write"],
    "iat": 1700000000,
    "exp": 1700000900
  }
}
```

### 13.3 RBAC Permission Matrix

| Permission | Admin | Analyst | Viewer |
|---|:---:|:---:|:---:|
| `meetings:read` | Yes | Yes | Yes |
| `meetings:write` | Yes | — | — |
| `participants:read` | Yes | Yes | Yes |
| `incidents:read` | Yes | Yes | Yes |
| `incidents:write` | Yes | Yes | — |
| `incidents:escalate` | Yes | Yes | — |
| `verifications:trigger` | Yes | Yes | — |
| `policies:read` | Yes | Yes | Yes |
| `policies:write` | Yes | — | — |
| `users:read` | Yes | — | — |
| `users:write` | Yes | — | — |
| `company:read` | Yes | — | — |
| `company:write` | Yes | — | — |
| `audit:read` | Yes | Yes | — |

### 13.4 API Security Controls

| Control | Implementation |
|---|---|
| **Rate limiting** | Token bucket algorithm via Redis. Default: 100 req/min per user, 1000 req/min per company. |
| **Input validation** | Pydantic schemas enforce type, length, and format constraints on all request bodies. |
| **SQL injection** | SQLAlchemy parameterized queries. No raw SQL. |
| **XSS** | React auto-escapes output. Content-Security-Policy headers. |
| **CSRF** | SameSite cookie policy + CSRF tokens for session-based auth. |
| **CORS** | Allowlist of known frontend origins. No wildcard. |
| **Request size** | Max 10MB request body (configurable). |
| **Webhook verification** | HMAC signature validation for all inbound webhooks (Zoom, Twilio). |

### 13.5 Secrets Management

```
┌──────────────────────────────────────────────────────────────┐
│                    SECRETS ARCHITECTURE                        │
│                                                               │
│  Development:                                                 │
│  └── .env file (git-ignored) with local defaults              │
│                                                               │
│  Staging / Production:                                        │
│  └── AWS Secrets Manager                                      │
│      ├── deepsafe/api/jwt-secret                              │
│      ├── deepsafe/db/postgres-url                             │
│      ├── deepsafe/db/redis-url                                │
│      ├── deepsafe/db/mongo-url                                │
│      ├── deepsafe/api-keys/resemble                           │
│      ├── deepsafe/api-keys/sensity                            │
│      ├── deepsafe/api-keys/openai                             │
│      ├── deepsafe/api-keys/twilio-sid                         │
│      ├── deepsafe/api-keys/twilio-token                       │
│      ├── deepsafe/integrations/zoom-client-secret             │
│      └── deepsafe/integrations/google-service-account         │
│                                                               │
│  Rotation:                                                    │
│  └── Automated 90-day rotation for all API keys               │
│  └── JWT secret rotation requires zero-downtime key overlap   │
└──────────────────────────────────────────────────────────────┘
```

---

## 14. Infrastructure & Deployment

### 14.1 Local Development (Docker Compose)

```yaml
# docker-compose.yml services
services:
  api:          # FastAPI app, port 8000, hot reload
  celery-worker: # Celery worker for async tasks
  celery-beat:   # Celery scheduled tasks
  flower:        # Celery monitoring UI, port 5555
  postgres:      # PostgreSQL 15, port 5432
  redis:         # Redis 7, port 6379
  mongo:         # MongoDB 6, port 27017
  rabbitmq:      # RabbitMQ 3.12, ports 5672 + 15672 (mgmt UI)
  postgres-test: # Isolated test database, port 5433
```

### 14.2 Production Architecture (Kubernetes)

```
┌─────────────────────────────────────────────────────────────────┐
│                      KUBERNETES CLUSTER                          │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │ Ingress Controller (nginx / AWS ALB)                     │    │
│  │ • TLS termination                                        │    │
│  │ • Rate limiting                                          │    │
│  │ • Path-based routing                                     │    │
│  └──────────────────────┬──────────────────────────────────┘    │
│                         │                                        │
│  ┌──────────────────────▼──────────────────────────────────┐    │
│  │ API Deployment (3+ replicas)                             │    │
│  │ • FastAPI + Uvicorn                                      │    │
│  │ • Horizontal Pod Autoscaler (CPU > 70%)                  │    │
│  │ • Readiness/liveness probes on /health                   │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ Celery Worker Deployment (5+ replicas)                   │    │
│  │ • Concurrency: 4 workers per pod                         │    │
│  │ • Autoscaler based on RabbitMQ queue depth               │    │
│  │ • Separate queues for audio/video/social-eng/verify      │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ Meeting Bot Deployment (scaled per concurrent meetings)  │    │
│  │ • One pod per active meeting bot                         │    │
│  │ • Resource limits: 1 CPU, 2GB RAM per bot                │    │
│  │ • Autoscaler based on meeting count                      │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌─────────────────────┐  ┌─────────────────────┐              │
│  │ PostgreSQL           │  │ Redis               │              │
│  │ (AWS RDS / managed)  │  │ (AWS ElastiCache)   │              │
│  └─────────────────────┘  └─────────────────────┘              │
│                                                                  │
│  ┌─────────────────────┐  ┌─────────────────────┐              │
│  │ MongoDB              │  │ RabbitMQ            │              │
│  │ (Atlas / managed)    │  │ (AWS MQ / managed)  │              │
│  └─────────────────────┘  └─────────────────────┘              │
│                                                                  │
│  ┌─────────────────────┐                                        │
│  │ S3 Bucket            │                                        │
│  │ (Recordings,         │                                        │
│  │  Evidence,           │                                        │
│  │  Exports)            │                                        │
│  └─────────────────────┘                                        │
└─────────────────────────────────────────────────────────────────┘
```

### 14.3 CI/CD Pipeline

```
┌──────────────────────────────────────────────────────────────────┐
│                     CI/CD PIPELINE (GitHub Actions)                │
│                                                                   │
│  Trigger: Push / PR to main or develop                            │
│                                                                   │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │  Lint   │  │  Type    │  │  Test    │  │  Build Docker   │  │
│  │ (ruff)  │  │  Check   │  │ (pytest) │  │  Image          │  │
│  │         │  │ (mypy)   │  │          │  │                  │  │
│  │ Rules:  │  │          │  │ 586+     │  │ Multi-stage      │  │
│  │ E,W,F   │  │          │  │ tests    │  │ build            │  │
│  └────┬────┘  └────┬─────┘  └────┬─────┘  └────────┬─────────┘  │
│       │            │             │                   │            │
│       └────────────┴─────────────┘                   │            │
│                    │                                  │            │
│                All pass?                              │            │
│                    │                                  │            │
│              ┌─────▼─────┐                           │            │
│              │  Coverage  │                           │            │
│              │  Report    │                           │            │
│              │  (> 90%)   │                           │            │
│              └─────┬──────┘                           │            │
│                    │                                  │            │
│                    └──────────────┬───────────────────┘            │
│                                  │                                │
│                          ┌───────▼────────┐                       │
│                          │ Push to ECR    │                       │
│                          │ (if main)      │                       │
│                          └───────┬────────┘                       │
│                                  │                                │
│                          ┌───────▼────────┐                       │
│                          │ Deploy to      │                       │
│                          │ Staging (auto) │                       │
│                          │ Prod (manual)  │                       │
│                          └────────────────┘                       │
└──────────────────────────────────────────────────────────────────┘
```

### 14.4 Environment Configuration

```python
# shared/config/settings.py — Pydantic BaseSettings

class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Core
    ENVIRONMENT: Literal["development", "staging", "production", "testing"]
    SECRET_KEY: str
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str           # PostgreSQL connection string
    DATABASE_POOL_SIZE: int = 20
    REDIS_URL: str              # Redis connection string
    MONGODB_URL: str            # MongoDB connection string

    # Celery
    CELERY_BROKER_URL: str      # RabbitMQ connection string
    CELERY_RESULT_BACKEND: str  # Redis for task results

    # External API Keys
    OPENAI_API_KEY: str
    RESEMBLE_API_KEY: str
    SENSITY_API_KEY: str

    # Twilio
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str

    # Platform Integrations
    ZOOM_CLIENT_ID: str
    ZOOM_CLIENT_SECRET: str
    ZOOM_BOT_JID: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    # Detection Thresholds (configurable per deployment)
    DETECTION_LOW_RISK_THRESHOLD: float = 0.30
    DETECTION_MEDIUM_RISK_THRESHOLD: float = 0.60
    DETECTION_HIGH_RISK_THRESHOLD: float = 0.85
    DETECTION_AV_SYNC_THRESHOLD_MS: int = 42

    model_config = SettingsConfigDict(env_file=".env")
```

---

## 15. Observability

### 15.1 Logging Strategy

| Component | Log Format | Destination |
|---|---|---|
| All services | Structured JSON (structlog) | stdout → log aggregator |
| API requests | `{timestamp, request_id, method, path, status, duration_ms, user_id}` | Datadog / CloudWatch |
| Detection events | `{timestamp, meeting_id, participant_id, detector, score, latency_ms}` | Datadog / CloudWatch |
| Verification events | `{timestamp, session_id, channel, status, attempt, duration_ms}` | Datadog / CloudWatch |

**Correlation ID:** Every inbound request generates a UUID `request_id` (or inherits from `X-Request-ID` header). This ID is propagated through:
- All log entries
- Celery task headers
- RabbitMQ message properties
- WebSocket messages
- External API calls (where supported)

### 15.2 Metrics (Prometheus Format)

```
# API metrics
deepsafe_api_requests_total{method, path, status}
deepsafe_api_request_duration_seconds{method, path}

# Detection metrics
deepsafe_detection_audio_score{meeting_id, participant_id}
deepsafe_detection_video_score{meeting_id, participant_id}
deepsafe_detection_social_eng_score{meeting_id}
deepsafe_detection_latency_seconds{detector}
deepsafe_detection_api_errors_total{detector, error_type}

# Verification metrics
deepsafe_verification_triggered_total{channel}
deepsafe_verification_completed_total{channel, result}
deepsafe_verification_duration_seconds{channel}

# Stream processing metrics
deepsafe_stream_audio_chunks_processed_total
deepsafe_stream_video_frames_processed_total
deepsafe_stream_queue_depth{queue_name}

# Meeting metrics
deepsafe_meetings_active_gauge
deepsafe_meetings_total{platform}
deepsafe_meetings_risk_level{level}

# System metrics
deepsafe_celery_workers_active
deepsafe_celery_task_latency_seconds{task_name}
deepsafe_websocket_connections_gauge
```

### 15.3 Alerting Rules

| Alert | Condition | Severity | Action |
|---|---|---|---|
| API Error Rate High | 5xx rate > 5% over 5 min | P1 | Page on-call engineer |
| Detection Pipeline Stalled | No audio chunks processed for > 60s during active meeting | P1 | Page on-call engineer |
| External API Down | Circuit breaker open for Resemble/Sensity/OpenAI | P2 | Notify engineering Slack channel |
| Verification Delivery Failure | Twilio SMS delivery failure rate > 10% | P1 | Page on-call engineer |
| Database Connection Pool Exhausted | Available connections < 5 | P2 | Auto-scale; notify engineering |
| Queue Depth Growing | RabbitMQ queue depth > 1000 | P2 | Auto-scale Celery workers |
| Disk Space Low | S3 bucket approaching quota | P3 | Notify engineering |

---

## 16. Performance Engineering

### 16.1 Connection Pooling

| Resource | Pool Strategy | Size |
|---|---|---|
| PostgreSQL | SQLAlchemy async pool | 20 connections per API instance |
| Redis | aioredis connection pool | 50 connections per instance |
| MongoDB | Motor async driver pool | 20 connections per instance |
| HTTP (external APIs) | httpx.AsyncClient connection pool | 100 connections, keep-alive |

### 16.2 Caching Strategy

| Data | Cache Location | TTL | Invalidation |
|---|---|---|---|
| User session | Redis | 7 days | On logout or password change |
| Participant directory lookup | Redis | 1 hour | On directory sync |
| Meeting metadata | Redis | Meeting duration | On meeting end |
| Dashboard aggregations | Redis | 60 seconds | On new incident |
| Policy rules | In-memory (per-process) | 5 minutes | On policy update (pub/sub invalidation) |

### 16.3 Database Optimization

- **Read replicas:** For dashboard queries (analytics, meeting history, participant profiles)
- **Partitioning:** `audit_logs` table partitioned by month for query performance
- **Archival:** Incidents older than 1 year moved to cold storage (S3 + Athena for ad-hoc queries)
- **Vacuum:** Automated PostgreSQL vacuum and analyze schedules

---

## 17. Failure Modes & Resilience

### 17.1 Circuit Breaker Configuration

| Service | Failure Threshold | Recovery Timeout | Fallback |
|---|---|---|---|
| Resemble AI API | 5 consecutive failures | 60 seconds | Wav2Vec 2.0 local model |
| Sensity API | 5 consecutive failures | 60 seconds | EfficientNet-B4 local model |
| OpenAI GPT-4 | 3 consecutive failures | 120 seconds | Keyword-only analysis (metrics B, D, E) |
| Twilio SMS | 3 consecutive failures | 30 seconds | Retry with voice callback |
| Twilio Voice | 3 consecutive failures | 30 seconds | Fall back to push notification |
| Firebase FCM | 5 consecutive failures | 60 seconds | Fall back to SMS |

### 17.2 Failure Scenarios

| Scenario | Impact | Behavior |
|---|---|---|
| **PostgreSQL down** | No new meetings, incidents, or users can be created | API returns 503; active meetings continue (state in Redis); alert P1 |
| **Redis down** | No session validation, no real-time state | API returns 503 for authenticated endpoints; detection pipeline continues; alert P1 |
| **RabbitMQ down** | Detection tasks cannot be dispatched | Stream processor queues locally (bounded); alert P1 |
| **All detection APIs down** | No external detection available | Fall back to local models; flag all meetings as "limited detection"; alert P2 |
| **Twilio down** | No SMS or voice verification | Fall back to push + email; extend verification timeout; alert P1 |
| **Meeting bot crashes** | One meeting loses monitoring | Auto-restart with 15-second rejoin; alert P2 |
| **Celery worker OOM** | Worker pod killed | Kubernetes restarts pod; task retried from RabbitMQ (at-least-once delivery) |

### 17.3 Data Loss Prevention

- **WAL replication:** PostgreSQL streaming replication to standby
- **Redis persistence:** AOF (Append-Only File) with 1-second fsync for critical data
- **Message durability:** RabbitMQ durable queues + persistent messages for detection tasks
- **Backup schedule:** Automated daily PostgreSQL pg_dump + S3 upload; 30-day retention

---

## 18. Testing Strategy

### 18.1 Test Pyramid

```
                    ┌───────────┐
                    │    E2E    │  ~20 tests
                    │  (Cypress)│  Full user flows
                    ├───────────┤
                    │Integration│  ~100 tests
                    │ (pytest)  │  API + DB + Redis
                    ├───────────┤
                    │   Unit    │  ~500 tests
                    │ (pytest)  │  Business logic
                    └───────────┘

    Current: 586+ tests, >90% coverage target
```

### 18.2 Test Categories

| Category | Scope | Tools | Run Frequency |
|---|---|---|---|
| **Unit tests** | Individual functions, classes, modules | pytest, unittest.mock | Every commit (CI) |
| **Integration tests** | API endpoints with real DB/Redis | pytest, test PostgreSQL (port 5433) | Every commit (CI) |
| **Contract tests** | External API response schemas | pytest, VCR cassettes | Weekly |
| **Load tests** | API throughput, detection pipeline latency | Locust, k6 | Pre-release |
| **Security tests** | OWASP Top 10, dependency vulnerabilities | Bandit, Safety, OWASP ZAP | Weekly |
| **E2E tests** | Full user workflows through dashboard | Cypress / Playwright | Pre-release |

### 18.3 Test Infrastructure

```
# Test database (isolated from development)
postgres-test:
  image: postgres:15
  port: 5433
  environment:
    POSTGRES_DB: deepsafe_test

# Test configuration
ENVIRONMENT=testing
DATABASE_URL=postgresql://...@localhost:5433/deepsafe_test

# External API mocking
- Resemble AI: VCR cassettes + mock responses
- Sensity: VCR cassettes + mock responses
- OpenAI: Mock responses with expected schema
- Twilio: Mock client (no real SMS in tests)
```

### 18.4 Current Test Status

| Module | Tests | Passing | Coverage |
|---|---|---|---|
| API Service | 166 | 166 | >90% |
| Detection Engine | ~100 | ~100 | >85% |
| Verification Service | ~80 | ~80 | >90% |
| Stream Processing | ~100 | ~90 | >80% |
| — Audio Buffer | 30 | 30 | >95% |
| — Alert Generator | 38 | 28 | ~75% |
| Integration Tests | ~60 | ~60 | — |
| **Total** | **586+** | **~560** | **>90% target** |

---

## 19. Migration & Data Management

### 19.1 Database Migrations (Alembic)

```
backend/src/migrations/
├── alembic.ini           # Alembic configuration
├── env.py                # Migration environment setup
└── versions/
    ├── 001_initial_schema.py
    ├── 002_add_risk_indicators.py
    ├── 003_add_verification_tables.py
    ├── 004_add_policy_engine.py
    └── ...
```

**Migration rules:**
- All migrations must be reversible (implement `upgrade()` and `downgrade()`)
- Data migrations must be idempotent
- Schema changes must be backward-compatible (no column drops in the same release as code changes)
- Migrations run automatically on deployment (pre-deploy hook)

### 19.2 Data Retention Policy

| Data Type | Hot Storage | Warm Storage | Cold Storage | Delete |
|---|---|---|---|---|
| Active meeting state | Redis | — | — | On meeting end |
| Meeting records | PostgreSQL | — | S3 (after 1 year) | 7 years |
| Incident evidence | PostgreSQL + S3 | — | S3 Glacier (after 1 year) | 7 years |
| Transcripts | MongoDB | — | S3 (after 90 days) | 1 year |
| Audit logs | PostgreSQL | — | S3 (after 1 year) | 7 years |
| Detection results | MongoDB | — | — | 90 days |

---

## 20. ADRs

### ADR-001: Python over Node.js for Backend

**Status:** Accepted
**Context:** Need a backend language for API, detection pipeline, and ML model serving.
**Decision:** Python 3.11+ with FastAPI.
**Rationale:** ML/AI ecosystem (PyTorch, Transformers, NumPy) is Python-native. FastAPI provides async performance comparable to Node.js. Team has strong Python expertise. Single language for API + ML reduces operational complexity.
**Consequences:** WebSocket performance may be slightly lower than Node.js; mitigated by Redis pub/sub offloading.

### ADR-002: RabbitMQ over Redis Streams for Task Queue

**Status:** Accepted
**Context:** Need reliable async task processing for detection pipeline.
**Decision:** RabbitMQ with Celery, using Redis only for result backend.
**Rationale:** RabbitMQ provides durable message delivery, dead-letter queues, and priority routing. Celery's mature integration with RabbitMQ handles retries, rate limiting, and monitoring (Flower). Redis Streams lacks mature Python task framework support.
**Consequences:** Additional infrastructure component (RabbitMQ). Mitigated by managed service (AWS MQ).

### ADR-003: Three-Database Architecture

**Status:** Accepted
**Context:** Application has relational data (users, meetings), ephemeral state (sessions, active meetings), and large semi-structured documents (transcripts, evidence).
**Decision:** PostgreSQL + Redis + MongoDB.
**Rationale:** Each database excels at its use case. PostgreSQL for ACID transactions and relational queries. Redis for sub-millisecond ephemeral state. MongoDB for flexible document storage without schema migrations for every new detection result format.
**Consequences:** Increased operational complexity. Mitigated by using managed database services in production (RDS, ElastiCache, Atlas).

### ADR-004: External Detection APIs with Local Fallbacks

**Status:** Accepted
**Context:** Need high-accuracy deepfake detection. Building models from scratch would delay MVP by 6+ months.
**Decision:** Use Resemble AI and Sensity APIs as primary detectors with local Wav2Vec 2.0 and EfficientNet-B4 as fallbacks.
**Rationale:** External APIs provide state-of-the-art accuracy immediately. Local fallbacks ensure degraded-but-functional service during API outages. Plan to gradually replace with custom models as training data accumulates.
**Consequences:** Per-API-call cost (~$0.01–0.05 per detection). Vendor lock-in risk mitigated by abstraction layer and fallback models.

### ADR-005: Modular Monolith over Microservices

**Status:** Accepted
**Context:** Team size is small (< 10 engineers). Need to move fast while maintaining clean architecture.
**Decision:** Single repository with logically separated services that can be decomposed later.
**Rationale:** Avoids premature microservice complexity (distributed transactions, service mesh, inter-service auth). Logical separation via module boundaries and message queues preserves the ability to split later. Conway's Law: small team = small number of deployable units.
**Consequences:** Must maintain disciplined module boundaries. Risk of coupling if boundaries erode. Code review process enforces boundary discipline.

### ADR-006: GPT-4 for Social Engineering Analysis

**Status:** Accepted
**Context:** Need to classify conversational intent and detect manipulation tactics in real-time meeting transcripts.
**Decision:** Use OpenAI GPT-4 with structured output for semantic analysis, batched per 60-second transcript windows.
**Rationale:** GPT-4 provides superior natural language understanding for nuanced social engineering detection. Fine-tuned smaller models lack the reasoning capability for novel attack patterns. Cost is manageable at ~$3/meeting.
**Consequences:** Dependency on OpenAI API availability. 60-second batching adds latency to social engineering detection (acceptable since SE detection is supplementary to deepfake detection). Cost scales linearly with meeting volume.

### ADR-007: React + MUI for Dashboard

**Status:** Accepted
**Context:** Need an enterprise-grade security dashboard with real-time updates, data tables, and rich visualizations.
**Decision:** React 19 + TypeScript + Material-UI 7 + React Query + Redux Toolkit.
**Rationale:** MUI provides a comprehensive enterprise component library (data grids, dialogs, forms). React Query handles server state caching and background refetching. Redux manages WebSocket-driven real-time state. TypeScript provides type safety across API boundaries.
**Consequences:** Large bundle size from MUI. Mitigated by tree-shaking and code splitting via Vite.

---

*End of Document*
