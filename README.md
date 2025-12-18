# DeepSafe

**The First Social Engineering Defense Platform for Video Conferencing**

DeepSafe protects organizations from AI-powered fraud attacks during video conferences by combining real-time deepfake detection, social engineering pattern recognition, and multi-channel identity verification.

> **Core Principle:** "Even if the deepfake is perfect, the attack still fails at verification."

---

## The Problem

Modern social engineering attacks increasingly leverage:
- AI-generated voice cloning to impersonate executives
- Deepfake video to create convincing visual representations
- Sophisticated manipulation tactics during live video calls
- Urgency-based pressure to bypass normal verification procedures

Traditional security measures are insufficient against these evolving threats, resulting in significant financial losses (average $130K per successful BEC attack).

## The Solution

DeepSafe provides:
- **Real-time deepfake detection** (<3 second latency)
- **Social engineering pattern recognition** using 6-metric scoring
- **Multi-channel identity verification** (SMS, voice, push, email)
- **Automated workflow triggers** based on risk thresholds
- **Integration with major video platforms** (Zoom, Google Meet, Microsoft Teams)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   VIDEO CONFERENCING PLATFORMS                   │
│              (Zoom, Google Meet, Microsoft Teams)                │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Meeting Bots      │
                    │  (Stream Capture)    │
                    └──────────┬───────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
         ┌──────────────────┐  ┌──────────────────┐
         │ Detection Engine │  │   Verification   │
         │ • Audio deepfake │  │   • SMS/Twilio   │
         │ • Video deepfake │  │   • Voice call   │
         │ • Social eng.    │  │   • Push notify  │
         └────────┬─────────┘  └────────┬─────────┘
                  │                     │
                  └──────────┬──────────┘
                             ▼
                  ┌──────────────────────┐
                  │   Risk Aggregation   │
                  │   Alert Generation   │
                  └──────────┬───────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
    ┌─────────┐       ┌──────────┐       ┌──────────────┐
    │WebSocket│       │ Database │       │  Dashboard   │
    │ Alerts  │       │PostgreSQL│       │  (React UI)  │
    └─────────┘       └──────────┘       └──────────────┘
```

---

## Project Structure

```
deepsafe/
├── backend/                 # FastAPI backend services
│   ├── src/
│   │   ├── services/        # Core services
│   │   │   ├── api/         # FastAPI application & routers
│   │   │   ├── detection/   # Deepfake & social engineering detection
│   │   │   ├── verification/# Multi-channel identity verification
│   │   │   └── stream/      # Real-time stream processing
│   │   ├── integrations/    # Platform integrations (Zoom, Meet)
│   │   ├── shared/          # Shared utilities, models, config
│   │   └── migrations/      # Database migrations (Alembic)
│   ├── tests/               # Test suites
│   ├── docker-compose.yml   # Local development services
│   └── Dockerfile           # Container configuration
│
├── deepsafe-app/            # React frontend dashboard
│   ├── src/
│   │   ├── pages/           # Page components
│   │   ├── components/      # Reusable UI components
│   │   ├── theme/           # Design system & theming
│   │   ├── types/           # TypeScript definitions
│   │   └── data/            # Mock data layer
│   └── docs/                # Frontend documentation
│
├── docs/                    # Project documentation
│   ├── deepsafe-prd.md      # Product requirements
│   ├── technical-design-document.md
│   ├── branding-guidelines.md
│   └── implementation-journal.md
│
└── scripts/                 # Development utilities
    └── timetracker.py       # Time tracking CLI
```

---

## Technology Stack

### Backend

| Layer | Technology |
|-------|------------|
| Framework | FastAPI 0.109 |
| Language | Python 3.11 |
| Database | PostgreSQL 15 (SQLAlchemy 2.0) |
| Cache | Redis 7 |
| Document Store | MongoDB 6 |
| Task Queue | Celery 5.3 + RabbitMQ |
| Auth | JWT + OAuth + RBAC |

### Frontend

| Category | Technology |
|----------|------------|
| Framework | React 19.2 |
| Language | TypeScript 5.9 |
| UI Library | Material-UI 7.3 |
| State | Redux Toolkit 2.11 |
| Data Fetching | React Query 5.90 |
| Build Tool | Vite 7.2 |

### External Integrations

| Purpose | Service |
|---------|---------|
| Voice/SMS | Twilio |
| Audio Deepfake | Resemble AI |
| Video Deepfake | Sensity / GetReal |
| AI Analysis | OpenAI GPT-4 |
| Video Platforms | Zoom SDK, Google Meet API |

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ and npm 9+
- Python 3.11+

### Backend Setup

```bash
# Navigate to backend
cd backend

# Start all services with Docker
docker-compose up -d

# Run database migrations
docker-compose exec api alembic upgrade head

# API available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Frontend Setup

```bash
# Navigate to frontend
cd deepsafe-app

# Install dependencies
npm install

# Start development server
npm run dev

# Dashboard available at http://localhost:5173
```

---

## Detection Engines

### Audio Deepfake Detection
- **Resemble AI** - Voice cloning detection API
- **Spectral Analysis** - Frequency pattern anomalies
- **Prosody Analysis** - Speech rhythm and intonation
- **A/V Sync Detection** - Audio-video synchronization

### Video Deepfake Detection
- **Sensity/GetReal** - Video deepfake API
- **Facial Landmarks** - Face geometry analysis
- **Micro-expressions** - Subtle facial movements
- **Lighting Analysis** - Illumination consistency
- **Virtual Camera Detection** - Fake video source detection

### Social Engineering Detection
6-metric scoring system:
1. **Urgency** - Time pressure tactics
2. **Authority** - Impersonating leadership
3. **Impersonation** - Identity spoofing
4. **Threat** - Fear-based manipulation
5. **Emotional Trigger** - Emotional exploitation
6. **Unusual Request** - Out-of-policy requests

### Risk Scoring Weights

| Factor | Weight |
|--------|--------|
| Audio Deepfake | 25% |
| Video Deepfake | 25% |
| Social Engineering | 20% |
| Voice Mismatch | 15% |
| Facial Anomaly | 10% |
| A/V Sync | 5% |

---

## Verification System

Multi-channel identity verification triggered by risk thresholds:

| Channel | Provider | Use Case |
|---------|----------|----------|
| SMS | Twilio | Quick code verification |
| Voice | Twilio | Callback confirmation |
| Push | Custom | Mobile app verification |
| Email | SendGrid | Email code verification |

---

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | User authentication |
| GET | `/api/meetings` | List monitored meetings |
| GET | `/api/meetings/{id}` | Meeting details & forensics |
| GET | `/api/participants` | Participant monitoring |
| GET | `/api/incidents` | Security incidents |
| POST | `/api/verifications` | Trigger verification |
| WS | `/ws/meetings/{id}` | Real-time meeting updates |

### Health & Monitoring

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Service health check |
| GET | `/health/db` | Database connectivity |
| GET | `/health/redis` | Redis connectivity |
| GET | `/metrics` | Prometheus metrics |

---

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
docker-compose exec api pytest

# Run with coverage
docker-compose exec api pytest --cov=src --cov-report=html

# Run specific test module
docker-compose exec api pytest tests/unit/detection/
```

**Current Status:** 586+ passing tests, >90% coverage target

### Frontend Tests

```bash
cd deepsafe-app

# Run linting
npm run lint

# Build check
npm run build
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [Product Requirements](docs/deepsafe-prd.md) | Features, positioning, roadmap |
| [Technical Design](docs/technical-design-document.md) | Architecture, APIs, data models |
| [Branding Guidelines](docs/branding-guidelines.md) | Colors, typography, logos |
| [App Tech Requirements](docs/app-tech-requirements.md) | Frontend specifications |
| [Dashboard Tech Requirements](docs/dashboard-tech-requirements.md) | Dashboard specifications |
| [Implementation Journal](docs/implementation-journal.md) | Development progress |

### Frontend Documentation

| Document | Description |
|----------|-------------|
| [README](deepsafe-app/README.md) | Frontend quick start |
| [Features](deepsafe-app/docs/FEATURES.md) | Feature descriptions |
| [User Guide](deepsafe-app/docs/USER_GUIDE.md) | End-user documentation |
| [Architecture](deepsafe-app/docs/ARCHITECTURE.md) | Frontend architecture |

---

## Development Services

Docker Compose provides all required services:

| Service | Port | Description |
|---------|------|-------------|
| api | 8000 | FastAPI application |
| postgres | 5432 | Primary database |
| redis | 6379 | Cache & sessions |
| mongo | 27017 | Document storage |
| rabbitmq | 5672, 15672 | Message broker |
| flower | 5555 | Celery monitoring |

---

## Environment Variables

### Backend

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/deepsafe
REDIS_URL=redis://localhost:6379/0
MONGODB_URL=mongodb://localhost:27017/deepsafe

# Security
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256

# External APIs
OPENAI_API_KEY=sk-...
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
RESEMBLE_API_KEY=...
SENSITY_API_KEY=...

# Platform Integrations
ZOOM_CLIENT_ID=...
ZOOM_CLIENT_SECRET=...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

### Frontend

```env
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws
```

---

## Implementation Status

| Phase | Status | Description |
|-------|--------|-------------|
| 1. Foundation | Complete | Project structure, database models, config |
| 2. API Service | Complete | FastAPI app, auth, routers, WebSocket |
| 3. Detection Engine | Complete | Audio, video, social engineering detection |
| 4. Verification | Complete | SMS, voice, push, email verification |
| 5. Platform Integration | Complete | Zoom, Google Meet bots |
| 6. Stream Processing | In Progress | Real-time pipeline |
| 7. Workflow Engine | Pending | Policy enforcement |
| 8. SSO/SIEM | Pending | Enterprise integrations |
| 9. Infrastructure | Pending | Production deployment |
| 10. Testing | Ongoing | E2E, load testing |

---

## License

Proprietary - DeepSafe Inc.

---

## Contributing

1. Create a feature branch from `main`
2. Make changes with tests
3. Submit a pull request
4. Ensure CI passes

For questions, contact the DeepSafe engineering team.
