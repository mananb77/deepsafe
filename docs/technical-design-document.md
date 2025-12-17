# DeepSafe Technical Design Document

**Version:** 1.0
**Last Updated:** December 17, 2025
**Status:** Living Document
**Authors:** DeepSafe Engineering Team

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Overview](#2-system-overview)
3. [Architecture](#3-architecture)
4. [Technology Stack](#4-technology-stack)
5. [Database Design](#5-database-design)
6. [API Specifications](#6-api-specifications)
7. [Detection Engine](#7-detection-engine)
8. [Verification System](#8-verification-system)
9. [Platform Integrations](#9-platform-integrations)
10. [Real-Time Processing Pipeline](#10-real-time-processing-pipeline)
11. [Workflow & Policy Engine](#11-workflow--policy-engine)
12. [Security Architecture](#12-security-architecture)
13. [Deployment Architecture](#13-deployment-architecture)
14. [Performance Requirements](#14-performance-requirements)
15. [Monitoring & Observability](#15-monitoring--observability)
16. [Disaster Recovery](#16-disaster-recovery)
17. [Appendices](#17-appendices)

---

## 1. Executive Summary

### 1.1 Purpose

DeepSafe is an enterprise-grade social engineering defense platform designed to protect organizations from AI-powered fraud attacks during video conferences. The system provides real-time detection of deepfakes (audio and video), social engineering tactics, and enables multi-channel identity verification.

### 1.2 Problem Statement

Modern social engineering attacks increasingly leverage:
- AI-generated voice cloning to impersonate executives
- Deepfake video to create convincing video representations
- Sophisticated manipulation tactics during live video calls
- Urgency-based pressure to bypass normal verification procedures

Traditional security measures are insufficient against these evolving threats, resulting in significant financial losses (average $130K per successful BEC attack).

### 1.3 Solution Overview

DeepSafe provides:
- **Real-time deepfake detection** (<3 second latency)
- **Social engineering pattern recognition** using 6-metric scoring
- **Multi-channel identity verification** (SMS, voice, push, email)
- **Automated workflow triggers** based on risk thresholds
- **Integration with major video platforms** (Zoom, Google Meet, Microsoft Teams)
- **Comprehensive audit trail** for compliance and forensics

### 1.4 MVP Scope

The Minimum Viable Product focuses on:
- **Platforms:** Zoom and Google Meet (Microsoft Teams deferred)
- **Detection:** External AI APIs with local model fallbacks
- **Verification:** SMS, voice callback, and push notifications
- **Dashboard:** Real-time monitoring and incident management

---

## 2. System Overview

### 2.1 High-Level System Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              VIDEO PLATFORMS                                 │
├─────────────────┬─────────────────────────┬─────────────────────────────────┤
│      Zoom       │      Google Meet        │      Microsoft Teams            │
│   Meeting SDK   │   Puppeteer Bot         │      Bot Framework              │
└────────┬────────┴───────────┬─────────────┴────────────────┬────────────────┘
         │                    │                              │
         ▼                    ▼                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          STREAM PROCESSOR                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Audio Buffer │  │ Video Buffer │  │ Transcript   │  │ Metadata     │    │
│  │  (3 sec)     │  │  (5 FPS)     │  │  Aggregator  │  │  Collector   │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
└─────────┼─────────────────┼─────────────────┼─────────────────┼────────────┘
          │                 │                 │                 │
          ▼                 ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DETECTION ENGINE                                    │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────────────┐    │
│  │ Audio Deepfake   │  │ Video Deepfake   │  │ Social Engineering     │    │
│  │   Detection      │  │   Detection      │  │   Detection            │    │
│  │                  │  │                  │  │                        │    │
│  │ • Resemble AI    │  │ • Sensity/GetReal│  │ • 6-Metric Scoring     │    │
│  │ • Spectral       │  │ • Facial Landmark│  │ • GPT-4 Analysis       │    │
│  │ • Prosody        │  │ • Micro-Express  │  │ • Keyword Detection    │    │
│  │ • A/V Sync       │  │ • Lighting       │  │ • Scenario Matching    │    │
│  │ • Wav2Vec (FB)   │  │ • EfficientNet   │  │ • Behavioral Analysis  │    │
│  └────────┬─────────┘  └────────┬─────────┘  └───────────┬────────────┘    │
└───────────┼─────────────────────┼────────────────────────┼─────────────────┘
            │                     │                        │
            └─────────────────────┴────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          RISK AGGREGATOR                                     │
│                                                                              │
│  Composite Score = (Deepfake × 0.40) + (Social Engineering × 0.60)          │
│                                                                              │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐                        │
│  │  LOW    │  │ MEDIUM  │  │  HIGH   │  │CRITICAL │                        │
│  │  0-30%  │  │ 31-60%  │  │ 61-85%  │  │ 86-100% │                        │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘                        │
└───────┼────────────┼────────────┼────────────┼─────────────────────────────┘
        │            │            │            │
        ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          WORKFLOW ENGINE                                     │
│                                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │ Policy Engine   │  │ Approval        │  │ Transaction     │             │
│  │                 │  │ Workflow        │  │ Gate            │             │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘             │
└───────────┼─────────────────────┼───────────────────┼──────────────────────┘
            │                     │                   │
            ▼                     ▼                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       VERIFICATION SERVICE                                   │
│                                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │     SMS      │  │    Voice     │  │    Push      │  │    Email     │    │
│  │   (Twilio)   │  │  (Twilio)    │  │  (Firebase)  │  │  (SendGrid)  │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                                          │
│                                                                              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │
│  │   PostgreSQL     │  │     Redis        │  │    MongoDB       │          │
│  │                  │  │                  │  │                  │          │
│  │ • Users          │  │ • Sessions       │  │ • Transcripts    │          │
│  │ • Companies      │  │ • Active Meetings│  │ • Forensic Data  │          │
│  │ • Meetings       │  │ • Pending Verify │  │ • Analysis       │          │
│  │ • Incidents      │  │ • Rate Limits    │  │   Results        │          │
│  │ • Policies       │  │ • Cache          │  │                  │          │
│  │ • Audit Logs     │  │                  │  │                  │          │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Core Components

| Component | Description | Technology |
|-----------|-------------|------------|
| **API Gateway** | RESTful API + WebSocket for dashboard | FastAPI |
| **Meeting Bot Service** | Platform-specific bots for stream capture | Python + SDKs |
| **Detection Service** | Deepfake + social engineering analysis | Python + PyTorch |
| **Analysis Service** | NLP processing, risk scoring | Python + OpenAI |
| **Verification Service** | Multi-channel OOB verification | Twilio, Firebase |
| **Workflow Service** | Policy engine, approval workflows | Celery |
| **Integration Service** | SSO, SIEM, calendar sync | Python |

### 2.3 Service Communication

```
┌─────────────────────────────────────────────────────────────────┐
│                    MESSAGE BROKER (RabbitMQ)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Queues:                                                        │
│  ├── detection.audio      (Priority: High)                      │
│  ├── detection.video      (Priority: High)                      │
│  ├── analysis.nlp         (Priority: Medium)                    │
│  ├── verification.sms     (Priority: High)                      │
│  ├── verification.voice   (Priority: High)                      │
│  ├── verification.push    (Priority: High)                      │
│  ├── workflow.policy      (Priority: Medium)                    │
│  ├── integration.sso      (Priority: Low)                       │
│  └── integration.siem     (Priority: Low)                       │
│                                                                 │
│  Exchange Types:                                                │
│  ├── direct   - Point-to-point task routing                     │
│  ├── fanout   - Broadcast events (meeting.started, etc.)        │
│  └── topic    - Pattern-based routing (detection.*.complete)    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Architecture

### 3.1 Microservices Architecture

DeepSafe follows a microservices architecture with the following principles:
- **Single Responsibility:** Each service handles one domain
- **Loose Coupling:** Services communicate via message queues
- **High Cohesion:** Related functionality grouped together
- **Independent Deployment:** Services can be deployed independently
- **Fault Isolation:** Service failures don't cascade

### 3.2 Service Definitions

#### 3.2.1 API Service (`src/services/api/`)

**Purpose:** HTTP/WebSocket gateway for dashboard and external integrations

**Endpoints:**
- `/api/v1/auth/*` - Authentication
- `/api/v1/users/*` - User management
- `/api/v1/companies/*` - Company management
- `/api/v1/meetings/*` - Meeting CRUD + monitoring
- `/api/v1/participants/*` - Participant management
- `/api/v1/incidents/*` - Security incident management
- `/api/v1/verifications/*` - Verification triggers/status
- `/api/v1/policies/*` - Policy CRUD
- `/api/v1/dashboard/*` - Analytics and metrics
- `ws://api/v1/ws/meetings/{id}` - Real-time updates

**Dependencies:** PostgreSQL, Redis, MongoDB

#### 3.2.2 Meeting Bot Service (`src/services/meeting_bot/`)

**Purpose:** Connect to video platforms and capture audio/video streams

**Responsibilities:**
- Bot lifecycle management (join/leave meetings)
- Audio stream capture (3-second chunks)
- Video frame capture (configurable FPS)
- Participant tracking
- Overlay rendering (trust badges, alerts)

**Platform-Specific Implementations:**
- `ZoomMeetingBot` - Zoom Meeting SDK
- `GoogleMeetBot` - Puppeteer-based headless browser
- `TeamsMeetingBot` - Microsoft Bot Framework

#### 3.2.3 Detection Service (`src/services/detection/`)

**Purpose:** Analyze audio/video for deepfakes

**Sub-Components:**
- Audio Deepfake Detection
- Video Deepfake Detection
- Audio-Video Sync Analysis

**Processing Model:**
- Receives chunks via RabbitMQ
- Parallel analysis execution
- Results published to `detection.complete` topic

#### 3.2.4 Analysis Service (`src/services/analysis/`)

**Purpose:** NLP analysis and risk score aggregation

**Sub-Components:**
- Transcript Analysis (GPT-4)
- Social Engineering Detection
- Risk Score Aggregator
- Pattern Matching Engine

#### 3.2.5 Verification Service (`src/services/verification/`)

**Purpose:** Multi-channel out-of-band identity verification

**Channels:**
- SMS (6-digit codes via Twilio)
- Voice Callback (IVR via Twilio)
- Push Notification (Firebase FCM)
- Email (SendGrid)

**Verification Flow:**
1. Trigger received from Workflow Service
2. Channel selection based on risk + transaction value
3. Code generation and delivery
4. User response validation
5. Result callback to Workflow Service

#### 3.2.6 Workflow Service (`src/services/workflow/`)

**Purpose:** Policy evaluation and automated response orchestration

**Components:**
- Policy Engine (rule evaluation)
- Approval Workflow (multi-party approval)
- Transaction Gate (block/allow decisions)
- Escalation Manager (severity upgrades)

#### 3.2.7 Integration Service (`src/services/integration/`)

**Purpose:** External system integrations

**Integrations:**
- SSO: Okta, Azure AD, Google Workspace
- SIEM: Splunk, Datadog, Sentinel
- Calendar: Google Calendar, Microsoft Graph
- HR Systems: Workday, BambooHR

### 3.3 Data Flow Diagram

```
Meeting Start
     │
     ▼
┌─────────────────┐
│  Meeting Bot    │──────────────────────────────────────────┐
│  (Platform SDK) │                                          │
└────────┬────────┘                                          │
         │                                                   │
         ▼                                                   │
┌─────────────────┐    ┌─────────────────┐                  │
│  Audio Stream   │    │  Video Stream   │                  │
│  (3 sec chunks) │    │  (5 FPS frames) │                  │
└────────┬────────┘    └────────┬────────┘                  │
         │                      │                           │
         ▼                      ▼                           │
┌────────────────────────────────────────┐                  │
│         STREAM PROCESSOR               │                  │
│                                        │                  │
│  • Buffer Management                   │                  │
│  • Chunk Correlation                   │                  │
│  • Quality Validation                  │                  │
└────────┬────────────────────┬──────────┘                  │
         │                    │                             │
         ▼                    ▼                             │
    ┌─────────┐          ┌─────────┐                       │
    │ Audio   │          │ Video   │                       │
    │Detection│          │Detection│                       │
    │ Queue   │          │ Queue   │                       │
    └────┬────┘          └────┬────┘                       │
         │                    │                             │
         ▼                    ▼                             │
┌─────────────────┐  ┌─────────────────┐                   │
│ Audio Analysis  │  │ Video Analysis  │                   │
│                 │  │                 │                   │
│ • Resemble AI   │  │ • Sensity       │                   │
│ • Spectral      │  │ • Facial        │                   │
│ • Prosody       │  │ • Lighting      │                   │
│ • Wav2Vec       │  │ • EfficientNet  │                   │
└────────┬────────┘  └────────┬────────┘                   │
         │                    │                             │
         └────────┬───────────┘                             │
                  │                                         │
                  ▼                                         │
         ┌───────────────┐                                  │
         │ Risk Aggregator│◄────────────────────────────────┘
         │               │         (Metadata + Transcript)
         │ Composite     │
         │ Score Calc    │
         └───────┬───────┘
                 │
                 ▼
         ┌───────────────┐
         │ Policy Engine │
         │               │
         │ Rule Match?   │
         └───────┬───────┘
                 │
         ┌───────┴───────┐
         │               │
    [No Match]      [Match]
         │               │
         ▼               ▼
    ┌─────────┐   ┌─────────────┐
    │ Continue│   │ Trigger     │
    │ Monitor │   │ Workflow    │
    └─────────┘   └──────┬──────┘
                         │
                         ▼
                  ┌─────────────┐
                  │ Action      │
                  │ Execution   │
                  │             │
                  │ • Alert     │
                  │ • Verify    │
                  │ • Block     │
                  │ • Escalate  │
                  └─────────────┘
```

---

## 4. Technology Stack

### 4.1 Backend Technologies

| Category | Technology | Version | Purpose |
|----------|------------|---------|---------|
| **Language** | Python | 3.11+ | Primary backend language |
| **Framework** | FastAPI | 0.109+ | Async REST API framework |
| **ORM** | SQLAlchemy | 2.0+ | Database ORM with async support |
| **Validation** | Pydantic | 2.5+ | Data validation and serialization |
| **Task Queue** | Celery | 5.3+ | Distributed task processing |
| **Message Broker** | RabbitMQ | 3.12+ | Message queue |
| **Process Manager** | Gunicorn | 21+ | WSGI HTTP Server |
| **ASGI** | Uvicorn | 0.25+ | ASGI server for FastAPI |

### 4.2 Databases

| Database | Purpose | Key Features |
|----------|---------|--------------|
| **PostgreSQL 15** | Relational data | Users, companies, meetings, incidents, policies, audit logs |
| **Redis 7** | Cache + sessions | Active meetings, pending verifications, rate limits, sessions |
| **MongoDB 6** | Document storage | Transcripts, forensic evidence, analysis results |

### 4.3 AI/ML Stack

| Technology | Purpose |
|------------|---------|
| **OpenAI GPT-4** | Social engineering analysis, NLP |
| **Resemble AI** | Audio deepfake detection (primary) |
| **Sensity/GetReal** | Video deepfake detection (primary) |
| **PyTorch** | Local model inference |
| **Wav2Vec 2.0** | Audio deepfake fallback model |
| **EfficientNet-B4** | Video deepfake fallback model |
| **Transformers** | Hugging Face model library |

### 4.4 External Services

| Service | Purpose | Provider |
|---------|---------|----------|
| **SMS** | OTP delivery | Twilio |
| **Voice** | IVR callbacks | Twilio |
| **Push Notifications** | Mobile alerts | Firebase FCM |
| **Email** | Verification emails | SendGrid |
| **SSO** | Identity providers | Okta, Azure AD, Google |
| **SIEM** | Log aggregation | Splunk, Datadog |

### 4.5 Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Containerization** | Docker | Application packaging |
| **Orchestration** | Docker Compose (dev), Kubernetes (prod) | Container management |
| **Load Balancer** | nginx / AWS ALB | Traffic distribution |
| **CDN** | CloudFront | Static asset delivery |
| **Storage** | S3 | Media file storage |
| **Secrets** | AWS Secrets Manager | Credential management |

### 4.6 Development Tools

| Tool | Purpose |
|------|---------|
| **Poetry** | Dependency management |
| **Alembic** | Database migrations |
| **pytest** | Testing framework |
| **Black** | Code formatting |
| **Ruff** | Linting |
| **mypy** | Type checking |
| **pre-commit** | Git hooks |

---

## 5. Database Design

### 5.1 PostgreSQL Schema

#### 5.1.1 Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐
│    companies    │───────│     users       │
│                 │  1:N  │                 │
│ • id (PK)       │       │ • id (PK)       │
│ • name          │       │ • company_id(FK)│
│ • subscription  │       │ • email         │
│ • settings      │       │ • role          │
└────────┬────────┘       │ • sso_provider  │
         │                └─────────────────┘
         │
         │ 1:N
         │
         ▼
┌─────────────────┐       ┌─────────────────┐
│    meetings     │───────│  participants   │
│                 │  1:N  │                 │
│ • id (PK)       │       │ • id (PK)       │
│ • company_id(FK)│       │ • meeting_id(FK)│
│ • platform      │       │ • user_id (FK)  │
│ • status        │       │ • trust_level   │
│ • risk_score    │       │ • risk_scores   │
│ • risk_level    │       │ • is_flagged    │
└────────┬────────┘       └────────┬────────┘
         │                         │
         │ 1:N                     │ 1:N
         ▼                         ▼
┌─────────────────┐       ┌─────────────────┐
│   incidents     │       │  verifications  │
│                 │       │                 │
│ • id (PK)       │       │ • id (PK)       │
│ • meeting_id(FK)│       │ • participant_id│
│ • participant_id│       │ • channel       │
│ • type          │       │ • status        │
│ • severity      │       │ • code          │
│ • status        │       │ • expires_at    │
└─────────────────┘       └─────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐
│ risk_indicators │
│                 │
│ • id (PK)       │
│ • meeting_id(FK)│
│ • incident_id   │
│ • indicator_type│
│ • confidence    │
│ • evidence      │
└─────────────────┘

┌─────────────────┐       ┌─────────────────┐
│    policies     │       │   audit_logs    │
│                 │       │                 │
│ • id (PK)       │       │ • id (PK)       │
│ • company_id(FK)│       │ • company_id(FK)│
│ • type          │       │ • user_id (FK)  │
│ • trigger       │       │ • action        │
│ • conditions    │       │ • target_type   │
│ • actions       │       │ • target_id     │
│ • priority      │       │ • metadata      │
└─────────────────┘       └─────────────────┘
```

#### 5.1.2 Table Specifications

**users**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone_number VARCHAR(20),
    role user_role NOT NULL DEFAULT 'viewer',
    sso_provider VARCHAR(50),
    sso_user_id VARCHAR(255),
    avatar_url VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    is_blacklisted BOOLEAN DEFAULT false,
    is_whitelisted BOOLEAN DEFAULT false,
    blacklist_reason TEXT,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT false,

    CONSTRAINT unique_sso_identity UNIQUE (sso_provider, sso_user_id)
);

CREATE TYPE user_role AS ENUM ('admin', 'security_analyst', 'viewer');
```

**companies**
```sql
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255),
    logo_url VARCHAR(500),
    subscription_tier subscription_tier DEFAULT 'starter',
    subscription_status VARCHAR(50) DEFAULT 'active',
    subscription_expires_at TIMESTAMP WITH TIME ZONE,
    settings JSONB DEFAULT '{}',
    allowed_domains TEXT[],
    max_users INTEGER DEFAULT 10,
    max_meetings_per_month INTEGER DEFAULT 100,
    features_enabled TEXT[],
    webhook_url VARCHAR(500),
    webhook_secret VARCHAR(255),
    siem_integration JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT false
);

CREATE TYPE subscription_tier AS ENUM ('starter', 'professional', 'enterprise');
```

**meetings**
```sql
CREATE TABLE meetings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform meeting_platform NOT NULL,
    platform_meeting_id VARCHAR(255),
    platform_meeting_url VARCHAR(500),
    company_id UUID NOT NULL REFERENCES companies(id),
    title VARCHAR(500),
    description TEXT,
    host_email VARCHAR(255),
    status meeting_status DEFAULT 'scheduled',
    risk_score DECIMAL(5,2) DEFAULT 0,
    risk_level risk_level DEFAULT 'low',
    scheduled_start_at TIMESTAMP WITH TIME ZONE,
    scheduled_end_at TIMESTAMP WITH TIME ZONE,
    actual_start_at TIMESTAMP WITH TIME ZONE,
    actual_end_at TIMESTAMP WITH TIME ZONE,
    participant_count INTEGER DEFAULT 0,
    max_participants INTEGER DEFAULT 0,
    deepfake_detected BOOLEAN DEFAULT false,
    social_engineering_detected BOOLEAN DEFAULT false,
    verification_triggered BOOLEAN DEFAULT false,
    recording_enabled BOOLEAN DEFAULT false,
    recording_url VARCHAR(500),
    bot_participant_id VARCHAR(255),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TYPE meeting_platform AS ENUM ('zoom', 'google_meet', 'teams', 'webex', 'other');
CREATE TYPE meeting_status AS ENUM ('scheduled', 'in_progress', 'completed', 'cancelled');
CREATE TYPE risk_level AS ENUM ('low', 'medium', 'high', 'critical');
```

**participants**
```sql
CREATE TABLE participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID NOT NULL REFERENCES meetings(id),
    user_id UUID REFERENCES users(id),
    display_name VARCHAR(255),
    email VARCHAR(255),
    phone_number VARCHAR(20),
    platform_participant_id VARCHAR(255),
    platform_user_id VARCHAR(255),
    role participant_role DEFAULT 'attendee',
    trust_level trust_level DEFAULT 'unverified',
    avatar_url VARCHAR(500),
    is_verified BOOLEAN DEFAULT false,
    verified_at TIMESTAMP WITH TIME ZONE,
    verification_method VARCHAR(50),
    is_flagged BOOLEAN DEFAULT false,
    flag_reason TEXT,
    deepfake_confidence DECIMAL(5,2),
    social_engineering_score DECIMAL(5,2),
    composite_risk_score DECIMAL(5,2) DEFAULT 0,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    left_at TIMESTAMP WITH TIME ZONE,
    device_type VARCHAR(50),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TYPE participant_role AS ENUM ('host', 'co-host', 'attendee', 'guest');
CREATE TYPE trust_level AS ENUM ('verified', 'known', 'unverified', 'suspicious', 'blacklisted');
```

**incidents**
```sql
CREATE TABLE incidents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID NOT NULL REFERENCES meetings(id),
    participant_id UUID REFERENCES participants(id),
    incident_type incident_type NOT NULL,
    severity incident_severity DEFAULT 'medium',
    status incident_status DEFAULT 'detected',
    title VARCHAR(255) NOT NULL,
    description TEXT,
    confidence_score DECIMAL(5,2),
    meeting_timestamp_seconds INTEGER,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID REFERENCES users(id),
    resolution_notes TEXT,
    evidence_summary JSONB DEFAULT '{}',
    actions_taken JSONB DEFAULT '[]',
    detection_method VARCHAR(100),
    detection_model VARCHAR(100),
    raw_analysis_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TYPE incident_type AS ENUM (
    'audio_deepfake', 'video_deepfake', 'voice_cloning',
    'face_swap', 'lip_sync', 'social_engineering',
    'impersonation', 'phishing_attempt', 'unauthorized_recording',
    'suspicious_behavior', 'policy_violation', 'other'
);
CREATE TYPE incident_severity AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE incident_status AS ENUM (
    'detected', 'investigating', 'resolved', 'false_positive', 'escalated'
);
```

**verifications**
```sql
CREATE TABLE verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    participant_id UUID NOT NULL REFERENCES participants(id),
    incident_id UUID REFERENCES incidents(id),
    verification_type verification_type NOT NULL,
    channel verification_channel NOT NULL,
    status verification_status DEFAULT 'pending',
    destination VARCHAR(255),
    verification_code VARCHAR(10),
    initiated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sent_at TIMESTAMP WITH TIME ZONE,
    verified_at TIMESTAMP WITH TIME ZONE,
    failed_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    failure_reason TEXT,
    transaction_amount DECIMAL(15,2),
    transaction_description TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TYPE verification_type AS ENUM (
    'identity', 'transaction', 'meeting_join', 'high_risk_action'
);
CREATE TYPE verification_channel AS ENUM ('sms', 'voice', 'push', 'email');
CREATE TYPE verification_status AS ENUM (
    'pending', 'sent', 'verified', 'failed', 'expired'
);
```

**risk_indicators**
```sql
CREATE TABLE risk_indicators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    meeting_id UUID NOT NULL REFERENCES meetings(id),
    participant_id UUID REFERENCES participants(id),
    incident_id UUID REFERENCES incidents(id),
    indicator_type indicator_type NOT NULL,
    category indicator_category NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    confidence DECIMAL(5,2) NOT NULL,
    weight DECIMAL(3,2) DEFAULT 1.0,
    evidence JSONB DEFAULT '{}',
    timestamp_seconds INTEGER,
    is_active BOOLEAN DEFAULT true,
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TYPE indicator_type AS ENUM (
    'audio_anomaly', 'video_anomaly', 'behavioral', 'linguistic',
    'metadata', 'identity', 'pattern_match', 'ml_detection'
);
CREATE TYPE indicator_category AS ENUM (
    'deepfake', 'social_engineering', 'impersonation', 'fraud', 'policy'
);
```

**policies**
```sql
CREATE TABLE policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    policy_type policy_type NOT NULL,
    trigger policy_trigger NOT NULL,
    is_enabled BOOLEAN DEFAULT true,
    priority INTEGER DEFAULT 100,
    conditions JSONB DEFAULT '{}',
    actions JSONB DEFAULT '[]',
    min_risk_score DECIMAL(5,2),
    max_risk_score DECIMAL(5,2),
    min_transaction_amount DECIMAL(15,2),
    max_transaction_amount DECIMAL(15,2),
    cooldown_minutes INTEGER DEFAULT 0,
    last_triggered_at TIMESTAMP WITH TIME ZONE,
    trigger_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT false
);

CREATE TYPE policy_type AS ENUM (
    'detection', 'verification', 'notification', 'blocking', 'escalation'
);
CREATE TYPE policy_trigger AS ENUM (
    'risk_threshold', 'incident_detected', 'verification_failed',
    'transaction_requested', 'manual', 'scheduled'
);
```

**audit_logs**
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    user_id UUID REFERENCES users(id),
    meeting_id UUID REFERENCES meetings(id),
    action audit_action NOT NULL,
    target_type VARCHAR(100),
    target_id UUID,
    description TEXT,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TYPE audit_action AS ENUM (
    'user_login', 'user_logout', 'user_created', 'user_updated', 'user_deleted',
    'user_blacklisted', 'user_whitelisted',
    'meeting_created', 'meeting_started', 'meeting_ended',
    'incident_created', 'incident_resolved', 'incident_escalated', 'incident_false_positive',
    'verification_initiated', 'verification_completed', 'verification_failed',
    'policy_created', 'policy_updated', 'policy_deleted', 'policy_triggered',
    'settings_updated', 'api_key_created', 'api_key_revoked'
);
```

### 5.2 Redis Data Structures

#### 5.2.1 Session Management
```
Key: session:{session_id}
Type: Hash
TTL: 24 hours
Fields:
  - user_id: UUID
  - company_id: UUID
  - email: string
  - role: string
  - created_at: timestamp
  - last_activity: timestamp
```

#### 5.2.2 Active Meeting State
```
Key: meeting:active:{meeting_id}
Type: Hash
TTL: Meeting duration + 1 hour
Fields:
  - status: string
  - risk_score: float
  - risk_level: string
  - participant_count: int
  - deepfake_detected: bool
  - se_detected: bool
  - last_analysis_at: timestamp
  - alerts_sent: int
```

#### 5.2.3 Pending Verification
```
Key: verification:pending:{verification_id}
Type: Hash
TTL: 5 minutes
Fields:
  - code: string (encrypted)
  - participant_id: UUID
  - channel: string
  - attempts: int
  - max_attempts: int
  - created_at: timestamp
```

#### 5.2.4 Rate Limiting
```
Key: ratelimit:{identifier}:{endpoint}
Type: String (counter)
TTL: 60 seconds
Value: Request count
```

#### 5.2.5 Detection Results Cache
```
Key: detection:result:{meeting_id}:{participant_id}:{timestamp}
Type: Hash
TTL: 5 minutes
Fields:
  - audio_score: float
  - video_score: float
  - se_score: float
  - composite_score: float
```

### 5.3 MongoDB Collections

#### 5.3.1 Transcripts Collection
```javascript
{
  _id: ObjectId,
  meeting_id: "uuid-string",
  participant_id: "uuid-string",
  segments: [
    {
      segment_id: "uuid-string",
      speaker_id: "uuid-string",
      speaker_name: "string",
      text: "string",
      start_time: 0.0,  // seconds from meeting start
      end_time: 5.0,
      confidence: 0.95,
      language: "en-US",
      risk_analysis: {
        keywords_detected: ["urgent", "wire transfer"],
        scenario_match: "bec_cfo_fraud",
        scenario_confidence: 0.78,
        gpt4_analysis: {
          manipulation_score: 0.65,
          urgency_level: "high",
          authority_claim: true,
          summary: "string"
        },
        composite_score: 0.72
      },
      created_at: ISODate
    }
  ],
  full_text: "string",  // aggregated transcript
  word_count: 1500,
  duration_seconds: 300,
  created_at: ISODate,
  updated_at: ISODate
}
```

**Indexes:**
- `{ meeting_id: 1 }`
- `{ participant_id: 1 }`
- `{ "segments.start_time": 1 }`
- `{ "segments.risk_analysis.composite_score": -1 }`

#### 5.3.2 Forensic Evidence Collection
```javascript
{
  _id: ObjectId,
  meeting_id: "uuid-string",
  incident_id: "uuid-string",
  participant_id: "uuid-string",
  evidence_type: "audio_analysis" | "video_analysis" | "combined",

  audio_analysis: {
    sample_rate: 16000,
    duration_ms: 3000,
    channels: 1,

    resemble_ai: {
      is_synthetic: true,
      confidence: 0.92,
      model_detected: "elevenlabs_v2",
      raw_response: {}
    },

    spectral_analysis: {
      synthetic_markers_detected: true,
      artifact_frequencies: [440, 880, 1320],
      formant_irregularities: 3,
      spectral_flatness: 0.45,
      confidence: 0.78
    },

    prosody_analysis: {
      pitch_variance: 0.12,
      energy_variance: 0.08,
      speaking_rate: 145,  // words per minute
      pause_pattern_score: 0.65,
      emotion_consistency: 0.72,
      confidence: 0.68
    },

    av_sync: {
      lip_sync_offset_ms: 85,
      is_synced: false,  // > 42ms threshold
      confidence: 0.95
    },

    wav2vec_fallback: {
      synthetic_probability: 0.88,
      model_version: "wav2vec2-base-960h",
      inference_time_ms: 150
    }
  },

  video_analysis: {
    resolution: "1920x1080",
    fps: 30,
    codec: "h264",

    sensity_result: {
      is_deepfake: true,
      confidence: 0.89,
      manipulation_type: "face_swap",
      model_detected: "faceswap_v3",
      raw_response: {}
    },

    facial_landmarks: {
      inconsistency_score: 0.72,
      landmark_jitter: 0.15,
      face_boundary_artifacts: true,
      confidence: 0.81
    },

    micro_expressions: {
      blink_rate: 12,  // per minute
      blink_regularity: 0.95,  // too regular = suspicious
      expression_latency_ms: 200,
      emotion_transition_score: 0.45,
      confidence: 0.67
    },

    lighting_analysis: {
      shadow_consistency: 0.82,
      reflection_patterns: "inconsistent",
      color_temperature_variance: 0.35,
      confidence: 0.75
    },

    virtual_camera: {
      detected: true,
      software: "OBS Virtual Camera",
      confidence: 0.98
    },

    efficientnet_fallback: {
      deepfake_probability: 0.85,
      model_version: "efficientnet-b4-ff++",
      inference_time_ms: 200
    }
  },

  composite_result: {
    is_deepfake: true,
    overall_confidence: 0.91,
    primary_indicator: "audio_resemble_ai",
    contributing_factors: [
      "spectral_synthetic_markers",
      "av_sync_mismatch",
      "facial_landmark_jitter"
    ]
  },

  raw_media_references: {
    audio_chunk_s3: "s3://deepsafe-evidence/audio/xxx.wav",
    video_frames_s3: "s3://deepsafe-evidence/video/xxx/",
    retention_days: 90
  },

  created_at: ISODate,
  analyzed_at: ISODate
}
```

**Indexes:**
- `{ meeting_id: 1 }`
- `{ incident_id: 1 }`
- `{ "composite_result.overall_confidence": -1 }`
- `{ created_at: -1 }`

---

## 6. API Specifications

### 6.1 API Design Principles

- **RESTful:** Resource-oriented URLs with proper HTTP methods
- **Versioned:** `/api/v1/` prefix for all endpoints
- **Authenticated:** JWT Bearer tokens required for most endpoints
- **Rate Limited:** Per-user and per-company rate limits
- **Paginated:** Cursor-based pagination for list endpoints
- **HATEOAS:** Links included in responses for discoverability

### 6.2 Authentication Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     AUTHENTICATION FLOW                         │
└─────────────────────────────────────────────────────────────────┘

1. Standard Login:
   POST /api/v1/auth/login
   Body: { email, password }
   Response: { access_token, refresh_token, expires_in }

2. SSO Login:
   GET /api/v1/auth/sso/{provider}
   → Redirects to IdP
   → Callback: /api/v1/auth/sso/{provider}/callback
   Response: { access_token, refresh_token, expires_in }

3. Token Refresh:
   POST /api/v1/auth/refresh
   Body: { refresh_token }
   Response: { access_token, refresh_token, expires_in }

4. Logout:
   POST /api/v1/auth/logout
   Header: Authorization: Bearer {token}
   Response: { success: true }
```

### 6.3 API Endpoints Summary

#### Authentication (`/api/v1/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/login` | Email/password login |
| POST | `/refresh` | Refresh access token |
| POST | `/logout` | Invalidate session |
| POST | `/change-password` | Change password |
| GET | `/sso/{provider}` | Initiate SSO flow |
| GET | `/sso/{provider}/callback` | SSO callback |
| GET | `/me` | Get current user |

#### Users (`/api/v1/users`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List users (paginated) |
| POST | `/` | Create user (admin) |
| GET | `/{id}` | Get user details |
| PATCH | `/{id}` | Update user |
| DELETE | `/{id}` | Delete user (soft) |
| POST | `/{id}/blacklist` | Blacklist user |
| POST | `/{id}/whitelist` | Whitelist user |

#### Companies (`/api/v1/companies`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List companies (super admin) |
| POST | `/` | Create company |
| GET | `/{id}` | Get company details |
| PATCH | `/{id}` | Update company |
| GET | `/{id}/settings` | Get company settings |
| PATCH | `/{id}/settings` | Update settings |

#### Meetings (`/api/v1/meetings`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List meetings (paginated) |
| POST | `/` | Register new meeting |
| GET | `/active` | List active meetings |
| GET | `/stats` | Dashboard statistics |
| GET | `/{id}` | Get meeting details |
| PATCH | `/{id}` | Update meeting |
| POST | `/{id}/start` | Mark meeting started |
| POST | `/{id}/end` | Mark meeting ended |
| POST | `/{id}/risk` | Update risk score |
| GET | `/{id}/transcript` | Get transcript |
| GET | `/{id}/forensics` | Get forensic evidence |

#### Participants (`/api/v1/participants`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List participants |
| POST | `/` | Add participant |
| GET | `/{id}` | Get participant details |
| PATCH | `/{id}` | Update participant |
| POST | `/{id}/risk` | Update risk scores |
| POST | `/{id}/verify` | Mark as verified |
| POST | `/{id}/leave` | Mark as left |

#### Incidents (`/api/v1/incidents`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List incidents |
| POST | `/` | Create incident |
| GET | `/stats` | Incident statistics |
| GET | `/{id}` | Get incident details |
| PATCH | `/{id}` | Update incident |
| POST | `/{id}/resolve` | Resolve incident |
| POST | `/{id}/escalate` | Escalate severity |
| POST | `/{id}/investigate` | Start investigation |

#### Verifications (`/api/v1/verifications`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List verifications |
| POST | `/` | Initiate verification |
| GET | `/stats` | Verification statistics |
| GET | `/{id}` | Get verification details |
| POST | `/{id}/check` | Submit verification code |
| POST | `/{id}/resend` | Resend code |
| POST | `/{id}/cancel` | Cancel verification |

#### Policies (`/api/v1/policies`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | List policies |
| POST | `/` | Create policy |
| POST | `/defaults` | Create default policies |
| GET | `/{id}` | Get policy details |
| PATCH | `/{id}` | Update policy |
| DELETE | `/{id}` | Delete policy |
| POST | `/{id}/enable` | Enable policy |
| POST | `/{id}/disable` | Disable policy |

#### Dashboard (`/api/v1/dashboard`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/overview` | Dashboard overview |
| GET | `/threats` | Threat timeline |
| GET | `/analytics` | Analytics data |
| GET | `/reports` | Generate reports |

### 6.4 WebSocket API

**Endpoint:** `ws://api/v1/ws/meetings/{meeting_id}`

**Events (Server → Client):**
```javascript
// Risk score update
{
  "type": "risk_update",
  "data": {
    "meeting_id": "uuid",
    "risk_score": 72.5,
    "risk_level": "high",
    "participant_id": "uuid",
    "timestamp": "2025-12-17T10:30:00Z"
  }
}

// Incident detected
{
  "type": "incident_detected",
  "data": {
    "incident_id": "uuid",
    "incident_type": "audio_deepfake",
    "severity": "high",
    "confidence": 0.92,
    "participant_id": "uuid",
    "title": "Potential voice cloning detected",
    "timestamp": "2025-12-17T10:30:00Z"
  }
}

// Verification required
{
  "type": "verification_required",
  "data": {
    "verification_id": "uuid",
    "participant_id": "uuid",
    "channel": "sms",
    "reason": "High risk transaction detected"
  }
}

// Participant update
{
  "type": "participant_update",
  "data": {
    "participant_id": "uuid",
    "trust_level": "suspicious",
    "is_flagged": true,
    "flag_reason": "Multiple detection triggers"
  }
}

// Meeting status update
{
  "type": "meeting_status",
  "data": {
    "meeting_id": "uuid",
    "status": "in_progress",
    "participant_count": 5
  }
}
```

### 6.5 Response Formats

**Success Response:**
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "request_id": "uuid",
    "timestamp": "2025-12-17T10:30:00Z"
  }
}
```

**Paginated Response:**
```json
{
  "items": [ ... ],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "pages": 8,
  "has_next": true,
  "has_prev": false
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  },
  "meta": {
    "request_id": "uuid",
    "timestamp": "2025-12-17T10:30:00Z"
  }
}
```

### 6.6 Rate Limits

| Tier | Requests/Minute | Burst |
|------|-----------------|-------|
| Starter | 60 | 100 |
| Professional | 300 | 500 |
| Enterprise | 1000 | 2000 |

Rate limit headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1702814400
```

---

## 7. Detection Engine

### 7.1 Overview

The Detection Engine is the core analytical component responsible for identifying deepfakes and social engineering attacks in real-time.

### 7.2 Audio Deepfake Detection

#### 7.2.1 Detection Pipeline

```
Audio Input (3-sec chunk)
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AUDIO PREPROCESSING                          │
│  • Sample rate normalization (16kHz)                            │
│  • Noise reduction                                              │
│  • Voice activity detection                                     │
│  • Speaker diarization                                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Resemble AI API │ │ Spectral        │ │ Prosody         │
│ (Primary)       │ │ Analysis        │ │ Analysis        │
│                 │ │                 │ │                 │
│ • API call      │ │ • FFT           │ │ • Pitch         │
│ • Model detect  │ │ • Formants      │ │ • Energy        │
│ • Confidence    │ │ • Artifacts     │ │ • Pauses        │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ A/V Sync Check  │
                    │                 │
                    │ • 42ms threshold│
                    │ • Lip movement  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Wav2Vec Fallback│
                    │ (if APIs fail)  │
                    │                 │
                    │ • Local model   │
                    │ • Fine-tuned    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Score Fusion   │
                    │                 │
                    │ Final Score =   │
                    │ weighted avg    │
                    └─────────────────┘
```

#### 7.2.2 Detection Methods

**1. Resemble AI API (Weight: 0.35)**
```python
class ResembleAIClient:
    async def analyze(self, audio_bytes: bytes) -> ResembleResult:
        """
        Returns:
            is_synthetic: bool
            confidence: float (0-1)
            model_detected: Optional[str]
            artifacts: List[str]
        """
```

**2. Spectral Analysis (Weight: 0.25)**
- Fast Fourier Transform (FFT) for frequency analysis
- Formant detection (F1, F2, F3)
- Synthetic artifact detection at specific frequencies
- Spectral flatness calculation

**3. Prosody Analysis (Weight: 0.20)**
- Pitch variance (synthetic speech often has lower variance)
- Energy patterns (unnatural consistency)
- Pause patterns (timing irregularities)
- Speaking rate analysis

**4. Audio-Video Sync (Weight: 0.20)**
- Lip movement correlation with audio
- **42ms threshold** for sync detection
- Frame-by-frame analysis

#### 7.2.3 Scoring Formula

```python
audio_deepfake_score = (
    resemble_score * 0.35 +
    spectral_score * 0.25 +
    prosody_score * 0.20 +
    av_sync_score * 0.20
)

# If primary API fails, use Wav2Vec fallback
if resemble_failed:
    audio_deepfake_score = wav2vec_score * 0.70 + local_analysis * 0.30
```

### 7.3 Video Deepfake Detection

#### 7.3.1 Detection Pipeline

```
Video Input (5 FPS frames)
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VIDEO PREPROCESSING                          │
│  • Frame extraction                                             │
│  • Face detection (MTCNN)                                       │
│  • Face alignment                                               │
│  • Resolution normalization                                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Sensity/GetReal │ │ Facial Landmark │ │ Lighting        │
│ API (Primary)   │ │ Analysis        │ │ Analysis        │
│                 │ │                 │ │                 │
│ • API call      │ │ • 68 landmarks  │ │ • Shadows       │
│ • Manipulation  │ │ • Jitter detect │ │ • Reflections   │
│ • Confidence    │ │ • Boundary      │ │ • Color temp    │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Micro-Expression│ │ Virtual Camera  │ │ EfficientNet    │
│ Analysis        │ │ Detection       │ │ Fallback        │
│                 │ │                 │ │                 │
│ • Blink rate    │ │ • OBS, vCam     │ │ • Local model   │
│ • Emotion       │ │ • Snap Camera   │ │ • FF++ trained  │
│ • Latency       │ │ • ManyCam       │ │                 │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Score Fusion    │
                    └─────────────────┘
```

#### 7.3.2 Detection Methods

**1. Sensity/GetReal API (Weight: 0.30)**
- Face swap detection
- Lip sync detection
- Full face manipulation detection

**2. Facial Landmark Analysis (Weight: 0.20)**
- 68-point landmark detection
- Temporal jitter analysis
- Face boundary artifact detection

**3. Micro-Expression Analysis (Weight: 0.15)**
- Blink rate monitoring (normal: 15-20/min)
- Blink regularity (too regular = synthetic)
- Emotion transition timing

**4. Lighting Analysis (Weight: 0.15)**
- Shadow direction consistency
- Reflection pattern analysis
- Color temperature variance

**5. Virtual Camera Detection (Weight: 0.20)**
- Known virtual camera signatures
- Frame metadata analysis
- Encoding artifact detection

#### 7.3.3 Scoring Formula

```python
video_deepfake_score = (
    sensity_score * 0.30 +
    landmark_score * 0.20 +
    micro_expression_score * 0.15 +
    lighting_score * 0.15 +
    virtual_camera_score * 0.20
)

# Fallback when primary API unavailable
if sensity_failed:
    video_deepfake_score = efficientnet_score * 0.65 + local_analysis * 0.35
```

### 7.4 Social Engineering Detection

#### 7.4.1 6-Metric Scoring System

```
┌─────────────────────────────────────────────────────────────────┐
│                SOCIAL ENGINEERING SCORING                        │
│                                                                  │
│  ┌──────────────────┐                                           │
│  │ 1. SCENARIO      │ Weight: 20%                               │
│  │    DETECTION     │                                           │
│  │                  │ • BEC/CEO Fraud patterns                  │
│  │                  │ • Vendor impersonation                    │
│  │                  │ • IT support scams                        │
│  │                  │ • Emergency scenarios                     │
│  └──────────────────┘                                           │
│                                                                  │
│  ┌──────────────────┐                                           │
│  │ 2. KEYWORD       │ Weight: 20%                               │
│  │    ANALYSIS      │                                           │
│  │                  │ • Urgency triggers                        │
│  │                  │ • Financial terms                         │
│  │                  │ • Authority claims                        │
│  │                  │ • Confidentiality requests                │
│  └──────────────────┘                                           │
│                                                                  │
│  ┌──────────────────┐                                           │
│  │ 3. GPT-4         │ Weight: 20%                               │
│  │    ANALYSIS      │                                           │
│  │                  │ • Context understanding                   │
│  │                  │ • Manipulation tactics                    │
│  │                  │ • Emotional pressure                      │
│  │                  │ • Logical inconsistencies                 │
│  └──────────────────┘                                           │
│                                                                  │
│  ┌──────────────────┐                                           │
│  │ 4. PARTICIPANT   │ Weight: 15%                               │
│  │    VALIDATION    │                                           │
│  │                  │ • Email domain verification               │
│  │                  │ • Calendar invite match                   │
│  │                  │ • Directory lookup                        │
│  │                  │ • Historical presence                     │
│  └──────────────────┘                                           │
│                                                                  │
│  ┌──────────────────┐                                           │
│  │ 5. METADATA      │ Weight: 10%                               │
│  │    ANALYSIS      │                                           │
│  │                  │ • Join timing anomalies                   │
│  │                  │ • Device fingerprint                      │
│  │                  │ • Network location                        │
│  │                  │ • Platform account age                    │
│  └──────────────────┘                                           │
│                                                                  │
│  ┌──────────────────┐                                           │
│  │ 6. BEHAVIORAL    │ Weight: 15%                               │
│  │    ANALYSIS      │                                           │
│  │                  │ • Conversation steering                   │
│  │                  │ • Resistance to verification              │
│  │                  │ • Time pressure tactics                   │
│  │                  │ • Information gathering patterns          │
│  └──────────────────┘                                           │
└─────────────────────────────────────────────────────────────────┘
```

#### 7.4.2 Scenario Detection Patterns

**BEC/CEO Fraud:**
- Claims of being executive/authority figure
- Requests for wire transfers or sensitive data
- Urgency + confidentiality combination
- Bypass normal procedures

**Vendor Impersonation:**
- Invoice/payment discussions
- Bank detail changes
- Fake urgency about overdue payments
- New contact from "known" vendor

**IT Support Scam:**
- Claims of security issues
- Requests for credentials
- Remote access requests
- Fake system alerts

**Emergency Scenarios:**
- Personal emergencies requiring money
- Time-sensitive opportunities
- Threats or legal consequences
- Emotional manipulation

#### 7.4.3 Keyword Categories

```python
URGENCY_KEYWORDS = [
    "urgent", "immediately", "right now", "asap",
    "time sensitive", "deadline", "can't wait",
    "before end of day", "within the hour"
]

FINANCIAL_KEYWORDS = [
    "wire transfer", "bank details", "routing number",
    "invoice", "payment", "bitcoin", "cryptocurrency",
    "gift cards", "account number"
]

AUTHORITY_KEYWORDS = [
    "ceo", "cfo", "president", "director",
    "don't tell anyone", "confidential", "between us",
    "i'm authorizing", "special approval"
]

PRESSURE_KEYWORDS = [
    "trust me", "don't verify", "skip the process",
    "just this once", "i'll explain later",
    "don't ask questions"
]
```

#### 7.4.4 GPT-4 Analysis Prompt

```python
ANALYSIS_PROMPT = """
Analyze the following meeting transcript segment for social engineering indicators.

Transcript:
{transcript}

Participant claiming to be: {claimed_identity}
Meeting context: {meeting_context}

Evaluate on a scale of 0-100 for each:
1. Manipulation tactics (pressure, urgency, authority abuse)
2. Logical inconsistencies in claims
3. Emotional manipulation attempts
4. Request reasonableness (normal vs suspicious)
5. Identity verification resistance

Provide:
- Overall risk score (0-100)
- Key concerns identified
- Recommended actions
- Confidence level

Format as JSON.
"""
```

#### 7.4.5 Social Engineering Score Formula

```python
se_score = (
    scenario_score * 0.20 +
    keyword_score * 0.20 +
    gpt4_score * 0.20 +
    participant_validation_score * 0.15 +
    metadata_score * 0.10 +
    behavioral_score * 0.15
)
```

### 7.5 Risk Score Aggregation

#### 7.5.1 Composite Score Calculation

```python
def calculate_composite_score(
    audio_deepfake_score: float,
    video_deepfake_score: float,
    social_engineering_score: float
) -> float:
    """
    Combine all detection scores into a single risk score.

    Weighting:
    - Deepfake (audio + video avg): 40%
    - Social Engineering: 60%

    Rationale: Social engineering is the actual attack vector;
    deepfakes are an enabling technology.
    """
    deepfake_score = (audio_deepfake_score + video_deepfake_score) / 2

    composite = (
        deepfake_score * 0.40 +
        social_engineering_score * 0.60
    )

    # Apply multiplier if both deepfake AND SE detected
    if deepfake_score > 50 and social_engineering_score > 50:
        composite = min(100, composite * 1.2)

    return round(composite, 2)
```

#### 7.5.2 Risk Level Classification

| Score Range | Risk Level | Color | Actions |
|-------------|------------|-------|---------|
| 0-30 | LOW | Green | Normal monitoring |
| 31-60 | MEDIUM | Yellow | Enhanced monitoring, passive alerts |
| 61-85 | HIGH | Orange | Active verification, notifications |
| 86-100 | CRITICAL | Red | Immediate intervention, multi-channel verification |

---

## 8. Verification System

### 8.1 Overview

The Verification System provides out-of-band identity confirmation when high-risk situations are detected.

### 8.2 Verification Channels

#### 8.2.1 SMS Verification (Twilio)
```python
class SMSVerifier:
    async def send_verification(
        self,
        phone_number: str,
        code: str,
        context: str
    ) -> bool:
        """
        Send 6-digit OTP via Twilio SMS.

        Message template:
        "DeepSafe Security Alert: Your verification code is {code}.
         Meeting: {meeting_title}
         If you didn't request this, contact security immediately."
        """
```

#### 8.2.2 Voice Verification (Twilio)
```python
class VoiceVerifier:
    async def initiate_callback(
        self,
        phone_number: str,
        code: str,
        participant_name: str
    ) -> bool:
        """
        Initiate IVR callback for voice verification.

        Flow:
        1. Call registered phone number
        2. Verify identity with security questions
        3. Read verification code
        4. Confirm receipt via keypad
        """
```

#### 8.2.3 Push Notification (Firebase)
```python
class PushVerifier:
    async def send_push(
        self,
        device_token: str,
        verification_data: dict
    ) -> bool:
        """
        Send push notification with action buttons.

        Notification:
        - Title: "Identity Verification Required"
        - Body: "Confirm your identity for meeting: {title}"
        - Actions: [Approve] [Deny] [Not Me]
        """
```

### 8.3 Verification Matrix

```
┌─────────────────────────────────────────────────────────────────┐
│              VERIFICATION CHANNEL SELECTION MATRIX               │
├─────────────────┬────────────────┬──────────────────────────────┤
│ Transaction     │ Risk Level     │ Verification Channels         │
│ Amount          │                │                               │
├─────────────────┼────────────────┼──────────────────────────────┤
│ < $5,000        │ Any            │ SMS only                      │
├─────────────────┼────────────────┼──────────────────────────────┤
│ $5,000 - $25K   │ Low (0-60%)    │ SMS + Email                   │
│                 │ High (61-85%)  │ SMS + Push                    │
│                 │ Critical (>85%)│ SMS + Callback + Dual Approval│
├─────────────────┼────────────────┼──────────────────────────────┤
│ $25,000 - $100K │ Any            │ Callback + Push + Dual Approval│
├─────────────────┼────────────────┼──────────────────────────────┤
│ > $100,000      │ Any            │ All channels + 24-hour hold   │
└─────────────────┴────────────────┴──────────────────────────────┘
```

### 8.4 Verification Flow

```
Detection Trigger
       │
       ▼
┌─────────────────┐
│ Risk Assessment │
│                 │
│ • Risk score    │
│ • Transaction $ │
│ • User history  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Channel Select  │
│                 │
│ Matrix lookup   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│ Generate Code   │────▶│ Store in Redis  │
│ (6 digits)      │     │ (TTL: 5 min)    │
└────────┬────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐
│ Send via        │
│ Channel(s)      │
│                 │
│ • SMS           │
│ • Voice         │
│ • Push          │
│ • Email         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Await Response  │
│                 │
│ Timeout: 5 min  │
│ Max attempts: 3 │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
[Success]  [Failure]
    │         │
    ▼         ▼
┌─────────┐ ┌─────────┐
│ Proceed │ │ Block + │
│ Meeting │ │ Alert   │
└─────────┘ └─────────┘
```

### 8.5 Code Generation

```python
def generate_verification_code(length: int = 6) -> str:
    """
    Generate cryptographically secure verification code.

    Security requirements:
    - Use secrets module (not random)
    - 6 digits = 1M combinations
    - TTL of 5 minutes
    - Max 3 attempts before lockout
    """
    return "".join(str(secrets.randbelow(10)) for _ in range(length))
```

---

## 9. Platform Integrations

### 9.1 Common Interface

All platform bots implement the `IMeetingBot` interface:

```python
from typing import Protocol, Callable, List
from abc import abstractmethod

class IMeetingBot(Protocol):
    @abstractmethod
    async def connect(
        self,
        meeting_id: str,
        credentials: BotCredentials
    ) -> None:
        """Join a meeting as a bot participant."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Leave the meeting and clean up resources."""

    @abstractmethod
    def subscribe_to_audio_stream(
        self,
        callback: Callable[[bytes, str], None]
    ) -> None:
        """Subscribe to audio stream (3-second chunks)."""

    @abstractmethod
    def subscribe_to_video_stream(
        self,
        callback: Callable[[bytes, str, int], None]
    ) -> None:
        """Subscribe to video frames."""

    @abstractmethod
    async def get_participants(self) -> List[Participant]:
        """Get current participant list."""

    @abstractmethod
    async def remove_participant(
        self,
        participant_id: str
    ) -> bool:
        """Remove a participant (requires host permissions)."""

    @abstractmethod
    async def show_trust_badge(
        self,
        participant_id: str,
        badge: TrustBadge
    ) -> None:
        """Display trust badge overlay for participant."""

    @abstractmethod
    async def show_alert(
        self,
        config: AlertConfig
    ) -> None:
        """Display alert overlay in meeting."""
```

### 9.2 Zoom Integration

#### 9.2.1 Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                      ZOOM INTEGRATION                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐                     │
│  │ Zoom Apps SDK   │    │ Zoom Meeting    │                     │
│  │ (In-meeting)    │    │ SDK (Bot)       │                     │
│  │                 │    │                 │                     │
│  │ • Overlay UI    │    │ • Join meeting  │                     │
│  │ • Trust badges  │    │ • Audio capture │                     │
│  │ • Alert popups  │    │ • Video capture │                     │
│  │ • Side panel    │    │ • Participant   │                     │
│  └────────┬────────┘    └────────┬────────┘                     │
│           │                      │                               │
│           │    ┌─────────────────┤                               │
│           │    │                 │                               │
│           ▼    ▼                 ▼                               │
│  ┌─────────────────┐    ┌─────────────────┐                     │
│  │ Zoom Webhooks   │    │ Zoom REST API   │                     │
│  │                 │    │                 │                     │
│  │ • meeting.start │    │ • User info     │                     │
│  │ • meeting.end   │    │ • Meeting mgmt  │                     │
│  │ • participant.* │    │ • Recording     │                     │
│  └─────────────────┘    └─────────────────┘                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 9.2.2 Required Credentials
- Zoom App Client ID & Secret
- Zoom Meeting SDK App Key & Secret
- Webhook verification token
- OAuth scopes: `meeting:read`, `meeting:write`, `user:read`

#### 9.2.3 Key Files
- `src/integrations/zoom/auth/oauth.py` - OAuth 2.0 flow
- `src/integrations/zoom/bot/ZoomMeetingBot.py` - Bot implementation
- `src/integrations/zoom/bot/ZoomAudioCapture.py` - Audio stream handler
- `src/integrations/zoom/bot/ZoomVideoCapture.py` - Video frame handler
- `src/integrations/zoom/webhooks/handler.py` - Webhook processor
- `src/integrations/zoom/overlay/ZoomAppsOverlay.tsx` - React overlay

### 9.3 Google Meet Integration

#### 9.3.1 Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                   GOOGLE MEET INTEGRATION                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐                     │
│  │ Meet Add-ons    │    │ Puppeteer Bot   │                     │
│  │ SDK             │    │ (Headless)      │                     │
│  │                 │    │                 │                     │
│  │ • Side panel    │    │ • Join via URL  │                     │
│  │ • Main stage    │    │ • Audio capture │                     │
│  │ • Activity bar  │    │ • Video capture │                     │
│  └────────┬────────┘    └────────┬────────┘                     │
│           │                      │                               │
│           │    ┌─────────────────┤                               │
│           │    │                 │                               │
│           ▼    ▼                 ▼                               │
│  ┌─────────────────┐    ┌─────────────────┐                     │
│  │ Google Calendar │    │ Chrome Extension│                     │
│  │ API             │    │ (Fallback)      │                     │
│  │                 │    │                 │                     │
│  │ • Meeting sync  │    │ • Overlay inject│                     │
│  │ • Attendee list │    │ • Trust badges  │                     │
│  └─────────────────┘    └─────────────────┘                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 9.3.2 Bot Implementation
```python
class GoogleMeetBot:
    """
    Puppeteer-based bot for Google Meet.

    Uses headless Chrome to:
    - Join meetings via URL
    - Capture audio via Web Audio API
    - Capture video via canvas
    - Monitor participant changes via DOM observation
    """

    async def connect(self, meeting_url: str):
        self.browser = await pyppeteer.launch(
            headless=True,
            args=[
                '--use-fake-ui-for-media-stream',
                '--use-fake-device-for-media-stream',
                '--disable-features=WebRtcHideLocalIpsWithMdns'
            ]
        )
        self.page = await self.browser.newPage()
        await self.page.goto(meeting_url)
        # ... handle join flow
```

### 9.4 Microsoft Teams Integration

#### 9.4.1 Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                 MICROSOFT TEAMS INTEGRATION                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐                     │
│  │ Teams Apps SDK  │    │ Bot Framework   │                     │
│  │                 │    │                 │                     │
│  │ • Tab app       │    │ • Meeting bot   │                     │
│  │ • Meeting stage │    │ • Proactive msg │                     │
│  │ • Side panel    │    │ • Adaptive cards│                     │
│  └────────┬────────┘    └────────┬────────┘                     │
│           │                      │                               │
│           │    ┌─────────────────┤                               │
│           │    │                 │                               │
│           ▼    ▼                 ▼                               │
│  ┌─────────────────┐    ┌─────────────────┐                     │
│  │ Microsoft Graph │    │ Azure Comm Svc  │                     │
│  │ API             │    │                 │                     │
│  │                 │    │ • Media streams │                     │
│  │ • Meeting info  │    │ • Recording     │                     │
│  │ • User profiles │    │                 │                     │
│  └─────────────────┘    └─────────────────┘                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

#### 9.4.2 Adaptive Cards for Alerts
```json
{
  "type": "AdaptiveCard",
  "version": "1.4",
  "body": [
    {
      "type": "Container",
      "style": "attention",
      "items": [
        {
          "type": "TextBlock",
          "text": "⚠️ Security Alert",
          "weight": "bolder",
          "size": "large"
        },
        {
          "type": "TextBlock",
          "text": "Potential deepfake detected for participant: John Doe",
          "wrap": true
        },
        {
          "type": "FactSet",
          "facts": [
            {"title": "Confidence:", "value": "92%"},
            {"title": "Type:", "value": "Audio Deepfake"},
            {"title": "Time:", "value": "10:32:15 AM"}
          ]
        }
      ]
    }
  ],
  "actions": [
    {"type": "Action.Submit", "title": "Verify Identity", "data": {"action": "verify"}},
    {"type": "Action.Submit", "title": "Remove Participant", "data": {"action": "remove"}},
    {"type": "Action.Submit", "title": "Dismiss", "data": {"action": "dismiss"}}
  ]
}
```

---

## 10. Real-Time Processing Pipeline

### 10.1 Stream Processor Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    STREAM PROCESSOR                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                     INPUT BUFFERS                            ││
│  │                                                              ││
│  │  ┌──────────────────┐  ┌──────────────────┐                 ││
│  │  │ Audio Ring Buffer│  │ Video Frame Queue│                 ││
│  │  │                  │  │                  │                 ││
│  │  │ Size: 3 seconds  │  │ Size: 30 frames  │                 ││
│  │  │ Format: PCM 16k  │  │ FPS: 5           │                 ││
│  │  └──────────────────┘  └──────────────────┘                 ││
│  └─────────────────────────────────────────────────────────────┘│
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                   CHUNK DISPATCHER                           ││
│  │                                                              ││
│  │  • Correlate audio/video by timestamp                       ││
│  │  • Quality validation                                       ││
│  │  • Participant ID assignment                                ││
│  │  • Publish to detection queues                              ││
│  └─────────────────────────────────────────────────────────────┘│
│                              │                                   │
│              ┌───────────────┼───────────────┐                   │
│              │               │               │                   │
│              ▼               ▼               ▼                   │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐          │
│  │ Audio Queue   │ │ Video Queue   │ │ Transcript    │          │
│  │               │ │               │ │ Queue         │          │
│  │ detection.    │ │ detection.    │ │ analysis.     │          │
│  │ audio         │ │ video         │ │ nlp           │          │
│  └───────┬───────┘ └───────┬───────┘ └───────┬───────┘          │
│          │                 │                 │                   │
│          │     ┌───────────┴───────────┐     │                   │
│          │     │                       │     │                   │
│          ▼     ▼                       ▼     ▼                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                   RESULT AGGREGATOR                          ││
│  │                                                              ││
│  │  • Collect detection results                                ││
│  │  • Calculate composite score                                ││
│  │  • Trigger policies                                         ││
│  │  • Publish WebSocket updates                                ││
│  └─────────────────────────────────────────────────────────────┘│
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                   ACTION EXECUTOR                            ││
│  │                                                              ││
│  │  • Send alerts                                              ││
│  │  • Trigger verifications                                    ││
│  │  • Update database                                          ││
│  │  • Log to MongoDB                                           ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 10.2 Celery Task Queues

```python
# Queue Configuration
CELERY_TASK_QUEUES = {
    'detection.audio': {
        'exchange': 'detection',
        'routing_key': 'detection.audio',
        'queue_arguments': {'x-max-priority': 10}
    },
    'detection.video': {
        'exchange': 'detection',
        'routing_key': 'detection.video',
        'queue_arguments': {'x-max-priority': 10}
    },
    'analysis.nlp': {
        'exchange': 'analysis',
        'routing_key': 'analysis.nlp',
    },
    'verification.sms': {
        'exchange': 'verification',
        'routing_key': 'verification.sms',
        'queue_arguments': {'x-max-priority': 10}
    },
    'verification.voice': {
        'exchange': 'verification',
        'routing_key': 'verification.voice',
        'queue_arguments': {'x-max-priority': 10}
    },
    'workflow.policy': {
        'exchange': 'workflow',
        'routing_key': 'workflow.policy',
    },
}

# Worker Configuration
CELERY_WORKER_POOLS = {
    'detection': {'concurrency': 8, 'pool': 'prefork'},
    'analysis': {'concurrency': 4, 'pool': 'prefork'},
    'verification': {'concurrency': 4, 'pool': 'gevent'},
    'workflow': {'concurrency': 2, 'pool': 'prefork'},
}
```

### 10.3 Processing Latency Budget

```
┌─────────────────────────────────────────────────────────────────┐
│              END-TO-END LATENCY BUDGET (< 5 seconds)            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Audio Capture        │ 3000ms │ ████████████████████░░░░░░░░░  │
│  (3-second chunk)     │        │                                │
│                       │        │                                │
│  Queue Dispatch       │  100ms │ ░                              │
│                       │        │                                │
│  Audio Detection      │  800ms │ █████░░░░░░░░░░░░░░░░░░░░░░░░  │
│  (parallel)           │        │                                │
│                       │        │                                │
│  Video Detection      │  900ms │ ██████░░░░░░░░░░░░░░░░░░░░░░░  │
│  (parallel)           │        │                                │
│                       │        │                                │
│  NLP Analysis         │  600ms │ ████░░░░░░░░░░░░░░░░░░░░░░░░░  │
│  (parallel)           │        │                                │
│                       │        │                                │
│  Score Aggregation    │   50ms │ ░                              │
│                       │        │                                │
│  Policy Evaluation    │   50ms │ ░                              │
│                       │        │                                │
│  WebSocket Publish    │   50ms │ ░                              │
│                       │        │                                │
├─────────────────────────────────────────────────────────────────┤
│  TOTAL (worst case)   │ 4550ms │ ██████████████████████████████ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 11. Workflow & Policy Engine

### 11.1 Policy Configuration Schema

```python
@dataclass
class PolicyConfig:
    name: str
    description: str
    policy_type: PolicyType  # detection, verification, notification, blocking
    trigger: PolicyTrigger  # risk_threshold, incident_detected, etc.
    is_enabled: bool = True
    priority: int = 100  # Lower = higher priority

    conditions: PolicyConditions
    actions: List[PolicyAction]

    min_risk_score: Optional[float] = None
    max_risk_score: Optional[float] = None
    min_transaction_amount: Optional[float] = None
    max_transaction_amount: Optional[float] = None

    cooldown_minutes: int = 0  # Prevent repeated triggers

@dataclass
class PolicyConditions:
    risk_level: Optional[List[RiskLevel]] = None
    incident_types: Optional[List[IncidentType]] = None
    participant_trust_levels: Optional[List[TrustLevel]] = None
    meeting_platforms: Optional[List[MeetingPlatform]] = None
    time_conditions: Optional[TimeConditions] = None
    custom_rules: Optional[Dict[str, Any]] = None

@dataclass
class PolicyAction:
    action_type: ActionType  # alert, verify, block, escalate, notify, webhook
    config: Dict[str, Any]
    delay_seconds: int = 0
    retry_count: int = 0
```

### 11.2 Default Policies

```python
DEFAULT_POLICIES = [
    # Low Risk Monitoring
    PolicyConfig(
        name="low_risk_monitoring",
        description="Passive monitoring for low-risk meetings",
        policy_type=PolicyType.DETECTION,
        trigger=PolicyTrigger.RISK_THRESHOLD,
        min_risk_score=0,
        max_risk_score=30,
        conditions=PolicyConditions(risk_level=[RiskLevel.LOW]),
        actions=[
            PolicyAction(action_type=ActionType.LOG, config={"level": "info"})
        ]
    ),

    # Medium Risk Alert
    PolicyConfig(
        name="medium_risk_alert",
        description="Passive alert for medium-risk situations",
        policy_type=PolicyType.NOTIFICATION,
        trigger=PolicyTrigger.RISK_THRESHOLD,
        min_risk_score=31,
        max_risk_score=60,
        conditions=PolicyConditions(risk_level=[RiskLevel.MEDIUM]),
        actions=[
            PolicyAction(
                action_type=ActionType.ALERT,
                config={
                    "type": "passive",
                    "channels": ["dashboard", "overlay"],
                    "message_template": "Medium risk detected: {summary}"
                }
            )
        ],
        cooldown_minutes=5
    ),

    # High Risk Verification
    PolicyConfig(
        name="high_risk_verification",
        description="Trigger verification for high-risk situations",
        policy_type=PolicyType.VERIFICATION,
        trigger=PolicyTrigger.RISK_THRESHOLD,
        min_risk_score=61,
        max_risk_score=85,
        conditions=PolicyConditions(risk_level=[RiskLevel.HIGH]),
        actions=[
            PolicyAction(
                action_type=ActionType.ALERT,
                config={
                    "type": "active",
                    "channels": ["dashboard", "overlay", "push"],
                    "message_template": "⚠️ High risk: {summary}"
                }
            ),
            PolicyAction(
                action_type=ActionType.VERIFY,
                config={
                    "channels": ["sms"],
                    "message_template": "Verify identity for meeting: {meeting_title}"
                }
            )
        ],
        cooldown_minutes=10
    ),

    # Critical Risk Intervention
    PolicyConfig(
        name="critical_risk_intervention",
        description="Immediate intervention for critical-risk situations",
        policy_type=PolicyType.BLOCKING,
        trigger=PolicyTrigger.RISK_THRESHOLD,
        min_risk_score=86,
        max_risk_score=100,
        conditions=PolicyConditions(risk_level=[RiskLevel.CRITICAL]),
        actions=[
            PolicyAction(
                action_type=ActionType.ALERT,
                config={
                    "type": "blocking",
                    "channels": ["dashboard", "overlay", "push", "sms"],
                    "message_template": "🚨 CRITICAL: {summary}"
                }
            ),
            PolicyAction(
                action_type=ActionType.VERIFY,
                config={
                    "channels": ["sms", "voice", "push"],
                    "require_all": True,
                    "message_template": "Urgent verification required"
                }
            ),
            PolicyAction(
                action_type=ActionType.NOTIFY,
                config={
                    "recipients": ["security_team", "it_admin"],
                    "channels": ["email", "slack"],
                    "message_template": "Critical alert: {full_details}"
                }
            ),
            PolicyAction(
                action_type=ActionType.BLOCK,
                config={
                    "block_type": "screen_share",
                    "duration_seconds": 300,
                    "message": "Screen sharing paused pending verification"
                }
            )
        ]
    ),

    # Deepfake Detection
    PolicyConfig(
        name="deepfake_detected",
        description="Respond to confirmed deepfake detection",
        policy_type=PolicyType.DETECTION,
        trigger=PolicyTrigger.INCIDENT_DETECTED,
        conditions=PolicyConditions(
            incident_types=[
                IncidentType.AUDIO_DEEPFAKE,
                IncidentType.VIDEO_DEEPFAKE,
                IncidentType.VOICE_CLONING,
                IncidentType.FACE_SWAP
            ]
        ),
        actions=[
            PolicyAction(
                action_type=ActionType.FLAG,
                config={"flag_reason": "Deepfake detected"}
            ),
            PolicyAction(
                action_type=ActionType.VERIFY,
                config={"channels": ["sms", "push"]}
            ),
            PolicyAction(
                action_type=ActionType.RECORD,
                config={"retention_days": 90}
            )
        ]
    ),

    # High-Value Transaction
    PolicyConfig(
        name="high_value_transaction",
        description="Extra verification for high-value transactions",
        policy_type=PolicyType.VERIFICATION,
        trigger=PolicyTrigger.TRANSACTION_REQUESTED,
        min_transaction_amount=25000,
        actions=[
            PolicyAction(
                action_type=ActionType.VERIFY,
                config={
                    "channels": ["voice", "push"],
                    "require_dual_approval": True
                }
            ),
            PolicyAction(
                action_type=ActionType.HOLD,
                config={
                    "hold_type": "transaction",
                    "duration_hours": 24,
                    "condition": "amount > 100000"
                }
            )
        ]
    )
]
```

### 11.3 Policy Evaluation Flow

```python
async def evaluate_policies(
    meeting_id: str,
    participant_id: str,
    context: PolicyContext
) -> List[PolicyAction]:
    """
    Evaluate all matching policies and return actions to execute.

    Steps:
    1. Get enabled policies for company (sorted by priority)
    2. Filter by trigger type
    3. Evaluate conditions
    4. Check cooldowns
    5. Return matched actions
    """
    company_id = context.company_id

    # Get policies
    policies = await get_enabled_policies(company_id)
    policies = sorted(policies, key=lambda p: p.priority)

    matched_actions = []

    for policy in policies:
        # Check trigger
        if not matches_trigger(policy, context):
            continue

        # Check conditions
        if not evaluate_conditions(policy.conditions, context):
            continue

        # Check cooldown
        if is_in_cooldown(policy, meeting_id):
            continue

        # Add actions
        matched_actions.extend(policy.actions)

        # Record trigger
        await record_policy_trigger(policy, meeting_id)

    return matched_actions
```

---

## 12. Security Architecture

### 12.1 Authentication & Authorization

#### 12.1.1 JWT Token Structure
```python
ACCESS_TOKEN_PAYLOAD = {
    "sub": "user_id",  # Subject (user ID)
    "email": "user@example.com",
    "company_id": "uuid",
    "role": "admin",  # admin, security_analyst, viewer
    "type": "access",
    "iat": 1702814400,  # Issued at
    "exp": 1702818000,  # Expiry (1 hour)
    "jti": "unique_token_id"  # JWT ID for revocation
}

REFRESH_TOKEN_PAYLOAD = {
    "sub": "user_id",
    "type": "refresh",
    "iat": 1702814400,
    "exp": 1703419200,  # 7 days
    "jti": "unique_token_id"
}
```

#### 12.1.2 Role-Based Access Control
```python
ROLE_PERMISSIONS = {
    "admin": [
        "users:*",
        "companies:*",
        "meetings:*",
        "incidents:*",
        "policies:*",
        "settings:*"
    ],
    "security_analyst": [
        "users:read",
        "meetings:*",
        "incidents:*",
        "policies:read",
        "verifications:*"
    ],
    "viewer": [
        "users:read:self",
        "meetings:read",
        "incidents:read",
        "dashboard:read"
    ]
}
```

### 12.2 Data Encryption

#### 12.2.1 At Rest
- **PostgreSQL:** TDE (Transparent Data Encryption) via AWS RDS
- **MongoDB:** Encrypted storage engine
- **Redis:** Not encrypted (ephemeral data)
- **S3:** Server-side encryption (SSE-S3)

#### 12.2.2 In Transit
- TLS 1.3 for all HTTP/WebSocket connections
- mTLS for internal service communication
- Encrypted RabbitMQ connections (AMQPS)

#### 12.2.3 Sensitive Fields
```python
ENCRYPTED_FIELDS = [
    "users.password_hash",  # bcrypt
    "verifications.verification_code",  # AES-256
    "companies.webhook_secret",  # AES-256
    "companies.siem_integration.api_key"  # AES-256
]
```

### 12.3 API Security

#### 12.3.1 Rate Limiting
- Per-user limits based on subscription tier
- Per-endpoint limits for sensitive operations
- Distributed rate limiting via Redis

#### 12.3.2 Input Validation
- Pydantic models for all request bodies
- Path parameter validation
- Query parameter sanitization
- File upload validation (MIME type, size)

#### 12.3.3 Output Sanitization
- No stack traces in production errors
- Sensitive field redaction in logs
- Response schema validation

### 12.4 Audit Logging

All security-relevant actions are logged:
- Authentication events (login, logout, token refresh)
- Authorization failures
- Data access (read sensitive data)
- Data modifications (create, update, delete)
- Policy triggers and actions
- Verification events

---

## 13. Deployment Architecture

### 13.1 Container Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    KUBERNETES CLUSTER                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    INGRESS (nginx)                           ││
│  │                                                              ││
│  │  api.deepsafe.io ──────────▶ api-service                    ││
│  │  ws.deepsafe.io ───────────▶ websocket-service              ││
│  │  dashboard.deepsafe.io ────▶ frontend-service               ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ api-service     │  │ meeting-bot     │  │ detection       │ │
│  │                 │  │ service         │  │ service         │ │
│  │ Replicas: 3     │  │ Replicas: 5     │  │ Replicas: 4     │ │
│  │ CPU: 1          │  │ CPU: 2          │  │ CPU: 4          │ │
│  │ RAM: 2GB        │  │ RAM: 4GB        │  │ RAM: 8GB (GPU)  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ verification    │  │ workflow        │  │ integration     │ │
│  │ service         │  │ service         │  │ service         │ │
│  │                 │  │                 │  │                 │ │
│  │ Replicas: 2     │  │ Replicas: 2     │  │ Replicas: 2     │ │
│  │ CPU: 1          │  │ CPU: 1          │  │ CPU: 1          │ │
│  │ RAM: 1GB        │  │ RAM: 1GB        │  │ RAM: 1GB        │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ celery-worker   │  │ celery-beat     │  │ flower          │ │
│  │                 │  │                 │  │                 │ │
│  │ Replicas: 8     │  │ Replicas: 1     │  │ Replicas: 1     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MANAGED SERVICES                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ RDS PostgreSQL  │  │ ElastiCache     │  │ DocumentDB      │ │
│  │ (Multi-AZ)      │  │ Redis Cluster   │  │ (MongoDB)       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Amazon MQ       │  │ S3              │  │ CloudWatch      │ │
│  │ (RabbitMQ)      │  │ (Media Storage) │  │ (Monitoring)    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 13.2 Docker Compose (Development)

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://deepsafe:deepsafe@postgres:5432/deepsafe
      - REDIS_URL=redis://redis:6379/0
      - MONGODB_URL=mongodb://mongo:27017/deepsafe
      - RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/
    depends_on:
      - postgres
      - redis
      - mongo
      - rabbitmq

  celery-worker:
    build:
      context: .
      dockerfile: Dockerfile.worker
    command: celery -A src.shared.messaging.celery worker -l info
    depends_on:
      - rabbitmq
      - redis

  celery-beat:
    build:
      context: .
      dockerfile: Dockerfile.worker
    command: celery -A src.shared.messaging.celery beat -l info
    depends_on:
      - rabbitmq
      - redis

  postgres:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    environment:
      - POSTGRES_USER=deepsafe
      - POSTGRES_PASSWORD=deepsafe
      - POSTGRES_DB=deepsafe
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  mongo:
    image: mongo:6
    volumes:
      - mongo_data:/data/db
    ports:
      - "27017:27017"

  rabbitmq:
    image: rabbitmq:3.12-management
    ports:
      - "5672:5672"
      - "15672:15672"

  flower:
    image: mher/flower
    command: celery flower --broker=amqp://guest:guest@rabbitmq:5672/
    ports:
      - "5555:5555"
    depends_on:
      - rabbitmq

volumes:
  postgres_data:
  mongo_data:
```

---

## 14. Performance Requirements

### 14.1 Latency Requirements

| Operation | Target (p95) | Maximum |
|-----------|--------------|---------|
| Audio deepfake detection | 800ms | 1500ms |
| Video deepfake detection | 900ms | 2000ms |
| Social engineering analysis | 600ms | 1200ms |
| **Total detection pipeline** | **<3 seconds** | **5 seconds** |
| Risk score calculation | 50ms | 100ms |
| Policy evaluation | 50ms | 100ms |
| WebSocket broadcast | 50ms | 100ms |
| **Alert generation (total)** | **<5 seconds** | **8 seconds** |
| SMS delivery | 5 seconds | 10 seconds |
| API GET requests | 100ms | 200ms |
| API POST requests | 200ms | 500ms |

### 14.2 Throughput Requirements

| Metric | Target |
|--------|--------|
| Concurrent meetings | 100+ |
| Participants per meeting | 50+ |
| Audio chunks per second | 500 |
| Video frames per second | 2500 |
| API requests per second | 1000 |
| WebSocket connections | 5000 |

### 14.3 Availability Requirements

| Metric | Target |
|--------|--------|
| Uptime SLA | 99.9% |
| Max planned downtime | 4 hours/month |
| RTO (Recovery Time Objective) | 15 minutes |
| RPO (Recovery Point Objective) | 1 minute |

---

## 15. Monitoring & Observability

### 15.1 Metrics (Prometheus/Datadog)

```python
CUSTOM_METRICS = [
    # Detection metrics
    "deepsafe.detection.audio.latency",
    "deepsafe.detection.audio.success_rate",
    "deepsafe.detection.video.latency",
    "deepsafe.detection.video.success_rate",
    "deepsafe.detection.score.distribution",

    # Meeting metrics
    "deepsafe.meetings.active.count",
    "deepsafe.meetings.participants.count",
    "deepsafe.meetings.incidents.count",

    # Verification metrics
    "deepsafe.verification.sent.count",
    "deepsafe.verification.success_rate",
    "deepsafe.verification.latency",

    # API metrics
    "deepsafe.api.requests.total",
    "deepsafe.api.latency.histogram",
    "deepsafe.api.errors.count",

    # Queue metrics
    "deepsafe.celery.queue.depth",
    "deepsafe.celery.task.success_rate",
    "deepsafe.celery.task.duration"
]
```

### 15.2 Logging (Structured JSON)

```python
LOG_FORMAT = {
    "timestamp": "2025-12-17T10:30:00.000Z",
    "level": "INFO",
    "service": "api",
    "request_id": "uuid",
    "user_id": "uuid",
    "company_id": "uuid",
    "message": "User logged in",
    "extra": {
        "ip_address": "1.2.3.4",
        "user_agent": "Mozilla/5.0..."
    }
}
```

### 15.3 Alerting Rules

| Alert | Condition | Severity |
|-------|-----------|----------|
| API Error Rate High | error_rate > 5% for 5 minutes | Critical |
| Detection Latency High | p95 > 5 seconds for 5 minutes | Warning |
| Queue Depth High | depth > 1000 for 5 minutes | Warning |
| Database Connection Pool Exhausted | available < 5 | Critical |
| Redis Memory High | usage > 80% | Warning |
| Failed Verifications High | failure_rate > 20% for 10 minutes | Warning |

---

## 16. Disaster Recovery

### 16.1 Backup Strategy

| Data | Frequency | Retention | Location |
|------|-----------|-----------|----------|
| PostgreSQL | Continuous + Daily snapshot | 30 days | S3 Cross-region |
| MongoDB | Hourly | 7 days | S3 Cross-region |
| Redis | Not backed up (ephemeral) | - | - |
| Media files | At creation | 90 days | S3 Cross-region |
| Configuration | On change | 90 days | Git + S3 |

### 16.2 Recovery Procedures

1. **Database Recovery**
   - Restore from latest RDS snapshot
   - Apply transaction logs for point-in-time recovery
   - Verify data integrity
   - Update connection strings

2. **Application Recovery**
   - Deploy from container registry
   - Apply latest configuration
   - Verify health checks
   - Enable traffic

3. **Full Region Failover**
   - Activate standby region
   - Update DNS records
   - Verify all services healthy
   - Notify customers

---

## 17. Appendices

### 17.1 Glossary

| Term | Definition |
|------|------------|
| **BEC** | Business Email Compromise - social engineering attacks targeting business transactions |
| **Deepfake** | AI-generated synthetic media (audio or video) |
| **OOB** | Out-of-Band - verification through a separate channel |
| **Risk Score** | Composite score (0-100) indicating threat level |
| **Trust Level** | Participant verification status (verified, known, unverified, suspicious, blacklisted) |

### 17.2 External API Dependencies

| API | Purpose | Fallback |
|-----|---------|----------|
| Resemble AI | Audio deepfake detection | Wav2Vec 2.0 local model |
| Sensity/GetReal | Video deepfake detection | EfficientNet-B4 local model |
| OpenAI GPT-4 | Social engineering analysis | Rule-based analysis |
| Twilio | SMS/Voice verification | Alternative provider |
| Firebase FCM | Push notifications | Alternative provider |
| SendGrid | Email notifications | Alternative provider |

### 17.3 Configuration Reference

See `src/shared/config/settings.py` for complete configuration options.

### 17.4 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-17 | Initial release |

---

**Document End**

*This document is the source of truth for the DeepSafe system architecture and specifications. All implementation decisions should align with the specifications defined herein.*
