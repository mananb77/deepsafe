# DeepSafe External Services and API Keys Inventory

**Last Updated:** 2026-02-23
**Classification:** Internal — Confidential

---

## Executive Summary

DeepSafe integrates with 15+ external services spanning AI/ML detection, communication, video platforms, infrastructure, and monitoring. This document catalogs every required API key, credential, and integration with estimated costs at MVP, production, and enterprise scale.

---

## 1. Communication APIs

### 1.1 Twilio (SMS & Voice Verification)

**Used for:** SMS OTP codes, automated voice call verification, callback flows for high-risk transactions.

**Referenced in:**
- `backend/.env.example`
- `backend/src/shared/config/settings.py`
- `backend/src/services/verification/sms_verifier.py`
- `backend/src/services/verification/voice_verifier.py`
- `detection.ipynb`

**Required Credentials:**
| Key | Description |
|-----|-------------|
| `TWILIO_ACCOUNT_SID` | Unique account identifier |
| `TWILIO_AUTH_TOKEN` | Authentication token |
| `TWILIO_PHONE_NUMBER` | From number for SMS/Voice (e.g., +1234567890) |
| `TWILIO_VERIFY_SERVICE_SID` | Optional: Twilio Verify service for managed OTP |

**Pricing:**
- Free tier: $15 trial credit
- SMS: $0.0075/message | Voice: $0.029/min
- **Est. startup:** ~$100/month (10K SMS + 1K voice calls)

**Sign-up:** https://www.twilio.com/try-twilio

---

### 1.2 SendGrid (Email Verification)

**Used for:** Email verification codes, branded notification emails for executives during high-risk approvals.

**Referenced in:**
- `backend/.env.example`
- `backend/src/services/verification/email_verifier.py`

**Required Credentials:**
| Key | Description |
|-----|-------------|
| `SENDGRID_API_KEY` | API key |
| `EMAIL_FROM` | Sender address (e.g., noreply@deepsafe.ai) |

**Pricing:**
- Free tier: 100 emails/day
- Pro: $80/month (100K emails/month)
- **Est. startup:** ~$80/month

**Sign-up:** https://sendgrid.com/pricing/

---

### 1.3 Firebase Cloud Messaging (Push Notifications)

**Used for:** Mobile push verification — sends approve/deny prompts to executives' devices with biometric auth (Face ID / Touch ID).

**Referenced in:**
- `backend/.env.example`
- `backend/src/services/verification/push_verifier.py`

**Required Credentials:**
| Key | Description |
|-----|-------------|
| `FIREBASE_PROJECT_ID` | Google Cloud project ID |
| `FIREBASE_CREDENTIALS_JSON` | Path to service account JSON key file |

**Pricing:**
- Free tier: Unlimited notifications
- **Est. startup:** $0/month

**Sign-up:** https://firebase.google.com/pricing/

---

## 2. Video Conferencing Platform Integrations

### 2.1 Zoom OAuth & Meeting Bot

**Used for:** OAuth authorization, meeting bot that joins calls to capture audio/video streams, webhook events for meeting lifecycle.

**Referenced in:**
- `backend/.env.example`
- `backend/src/shared/config/settings.py`
- `backend/src/integrations/zoom/auth/oauth.py`
- `backend/src/integrations/zoom/bot/meeting_bot.py`
- `backend/src/integrations/zoom/webhooks/handler.py`

**Required Credentials:**
| Key | Description |
|-----|-------------|
| `ZOOM_CLIENT_ID` | OAuth client ID |
| `ZOOM_CLIENT_SECRET` | OAuth client secret |
| `ZOOM_BOT_JID` | Bot Jabber ID for server-to-server OAuth |
| `ZOOM_WEBHOOK_SECRET` | Webhook signature validation secret |

**Pricing:**
- Free tier: Basic meetings (40-min group limit)
- Pro: $15.99/month | Business: $269.99/month
- **Est. startup:** ~$16–270/month

**Sign-up:** https://developers.zoom.us/docs/integrations/oauth/

---

### 2.2 Google Meet OAuth & Calendar Integration

**Used for:** OAuth authorization, Google Meet bot, Google Calendar sync for auto-scheduling bot joins.

**Referenced in:**
- `backend/.env.example`
- `backend/src/integrations/google_meet/auth/oauth.py`
- `backend/src/integrations/google_meet/bot/meeting_bot.py`
- `backend/src/integrations/google_meet/calendar/sync.py`

**Required Credentials:**
| Key | Description |
|-----|-------------|
| `GOOGLE_CLIENT_ID` | OAuth 2.0 client ID |
| `GOOGLE_CLIENT_SECRET` | OAuth 2.0 client secret |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Path to service account JSON (for domain-wide delegation) |

**Required OAuth Scopes:**
- `https://www.googleapis.com/auth/meetings.space.readonly`
- `https://www.googleapis.com/auth/calendar.readonly`
- `https://www.googleapis.com/auth/calendar.events`
- `openid`, `email`, `profile`

**Pricing:**
- Google Workspace: $6–18/user/month
- **Est. startup:** ~$18/month

**Sign-up:** https://developers.google.com/meet/api

---

## 3. AI/ML & Detection APIs

### 3.1 OpenAI GPT-4 (Social Engineering Analysis)

**Used for:** Real-time NLP analysis of meeting conversations, intent classification, manipulation tactic detection (urgency, authority, reciprocity). Contributes 20% weight to overall risk score.

**Referenced in:**
- `backend/src/shared/config/settings.py`
- `backend/src/services/detection/social_engineering/gpt4_analyzer.py`
- `detection.ipynb`

**Required Credentials:**
| Key | Description |
|-----|-------------|
| `OPENAI_API_KEY` | API key |

**Configuration:**
| Key | Default |
|-----|---------|
| `OPENAI_MODEL` | `gpt-4-turbo-preview` |
| `OPENAI_MAX_TOKENS` | `1000` |
| `OPENAI_TEMPERATURE` | `0.3` |

**Pricing:**
- No free tier (credit card required)
- GPT-4 Turbo: $0.01/1K input tokens, $0.03/1K output tokens
- **Est. startup:** ~$75/month (10K conversations × 500 avg tokens)

**Sign-up:** https://platform.openai.com/

---

### 3.2 Resemble AI (Audio Deepfake Detection)

**Used for:** Voice cloning detection, voice print comparison, synthetic speech identification. Primary audio detection signal (25% of risk score).

**Referenced in:**
- `backend/src/shared/config/settings.py`
- `backend/src/services/detection/audio/resemble_client.py`

**Required Credentials:**
| Key | Description |
|-----|-------------|
| `RESEMBLE_API_KEY` | API key |

**Pricing:**
- Starter: $99/month (10K audio analyses)
- Growth: $499/month (100K analyses)
- **Est. startup:** ~$99/month

**Sign-up:** https://www.resembleai.com/

---

### 3.3 Sensity / GetReal AI (Video Deepfake Detection)

**Used for:** Video deepfake detection — face swaps, lip-sync manipulation, GAN-generated faces. Primary video detection signal (25% of risk score).

**Referenced in:**
- `backend/src/shared/config/settings.py`
- `backend/src/services/detection/video/sensity_client.py`

**Required Credentials:**
| Key | Description |
|-----|-------------|
| `SENSITY_API_KEY` | API key |

**Pricing:**
- Pro: $199–499/month
- Enterprise: Custom pricing
- **Est. startup:** ~$199/month

**Sign-up:** https://www.sensity.ai/

---

### 3.4 Google Cloud Speech-to-Text (Transcription)

**Used for:** Real-time audio transcription from meeting participants for NLP analysis pipeline.

**Referenced in:**
- `backend/pyproject.toml` (`google-cloud-speech = "^2.24.0"`)
- `detection.ipynb`

**Required Credentials:**
| Key | Description |
|-----|-------------|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Service account for GCP |

**Pricing:**
- Free tier: 60 min/month
- Streaming: $0.024 per 15 seconds
- **Est. startup:** ~$50–150/month

**Sign-up:** https://cloud.google.com/speech-to-text/pricing

---

## 4. Infrastructure & Data Storage

### 4.1 PostgreSQL

**Used for:** Users, meetings, incidents, policies, verifications, audit logs (all structured data).

**Referenced in:** `backend/docker-compose.yml`, `backend/src/shared/database/postgres.py`

| Key | Description |
|-----|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@host:5432/deepsafe` |
| `DATABASE_POOL_SIZE` | Default: 20 |
| `DATABASE_MAX_OVERFLOW` | Default: 10 |

**Est. startup:** $50–150/month (AWS RDS or DigitalOcean Managed)

---

### 4.2 Redis

**Used for:** Session management, real-time meeting state, Celery result backend, rate limiting, verification code expiry.

**Referenced in:** `backend/docker-compose.yml`, `backend/src/shared/database/redis.py`

| Key | Description |
|-----|-------------|
| `REDIS_URL` | `redis://[:password]@host:6379/0` |

**Est. startup:** $30–100/month (managed)

---

### 4.3 MongoDB

**Used for:** Unstructured logs, meeting transcripts, raw detection results, flexible incident reports.

**Referenced in:** `backend/docker-compose.yml`, `backend/src/shared/database/mongodb.py`

| Key | Description |
|-----|-------------|
| `MONGODB_URL` | `mongodb://user:pass@host:27017/deepsafe` |

**Est. startup:** $57–200/month (Atlas paid tier)

---

### 4.4 RabbitMQ

**Used for:** Celery message broker for async detection, verification, and workflow tasks.

**Referenced in:** `backend/docker-compose.yml`

| Key | Description |
|-----|-------------|
| `CELERY_BROKER_URL` | `amqp://user:pass@host:5672//` |

**Est. startup:** $40–100/month (CloudAMQP)

---

### 4.5 AWS S3 (via boto3)

**Used for:** Meeting recording storage, forensic evidence archival, ML model artifacts.

**Referenced in:** `backend/pyproject.toml` (`boto3 = "^1.34.0"`)

| Key | Description |
|-----|-------------|
| `AWS_ACCESS_KEY_ID` | IAM access key |
| `AWS_SECRET_ACCESS_KEY` | IAM secret key |
| `AWS_REGION` | e.g., us-east-1 |

**Est. startup:** $50–200/month

---

## 5. Monitoring

### 5.1 Sentry (Error Tracking & APM)

**Used for:** Error tracking, performance monitoring, distributed tracing across API + Celery workers.

**Referenced in:** `backend/.env.example`, `backend/pyproject.toml` (`sentry-sdk`)

| Key | Description |
|-----|-------------|
| `SENTRY_DSN` | Data Source Name for Sentry project |

**Pricing:**
- Free tier: 5K errors/month
- Pro: $29/month
- **Est. startup:** $29/month

**Sign-up:** https://sentry.io/pricing/

---

## 6. Cost Summary

### MVP (Getting Started)

| Service | Monthly Cost |
|---------|-------------|
| Twilio (1K SMS) | $8 |
| SendGrid (free tier) | $0 |
| Firebase (free tier) | $0 |
| Zoom (free tier) | $0 |
| OpenAI GPT-4 | $50 |
| Resemble AI (starter) | $99 |
| Google Speech-to-Text | $25 |
| PostgreSQL (small managed) | $50 |
| Redis (small managed) | $30 |
| MongoDB (free tier) | $0 |
| S3 (minimal) | $10 |
| Sentry (free tier) | $0 |
| **TOTAL** | **~$272/month** |

### Production (Scale-up)

| Service | Monthly Cost |
|---------|-------------|
| Twilio (100K SMS + voice) | $500 |
| SendGrid (professional) | $80 |
| Firebase | $50 |
| Zoom (pro) | $20 |
| OpenAI GPT-4 | $500 |
| Resemble AI (growth) | $499 |
| Sensity (video detection) | $500 |
| Google Speech-to-Text | $200 |
| PostgreSQL (large) | $500 |
| Redis (large) | $200 |
| MongoDB (M10 cluster) | $250 |
| S3 (5TB) | $200 |
| RabbitMQ (managed) | $100 |
| Sentry (pro) | $29 |
| **TOTAL** | **~$3,628/month** |

### Enterprise

| Service | Monthly Cost |
|---------|-------------|
| All services at enterprise tier | $16,000+ |

---

## 7. Environment Variable Quick Reference

```bash
# === Core ===
ENVIRONMENT=production
SECRET_KEY=<secure-random-key>
DEBUG=false

# === Database ===
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/deepsafe
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# === Redis ===
REDIS_URL=redis://:password@host:6379/0

# === MongoDB ===
MONGODB_URL=mongodb://user:pass@host:27017/deepsafe

# === Celery / RabbitMQ ===
CELERY_BROKER_URL=amqp://user:pass@host:5672//
CELERY_RESULT_BACKEND=redis://:password@host:6379/1

# === JWT ===
JWT_SECRET_KEY=<secure-random-key>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# === Zoom ===
ZOOM_CLIENT_ID=<zoom-client-id>
ZOOM_CLIENT_SECRET=<zoom-client-secret>
ZOOM_WEBHOOK_SECRET=<zoom-webhook-secret>
ZOOM_BOT_JID=<zoom-bot-jid>

# === Google ===
GOOGLE_CLIENT_ID=<google-client-id>
GOOGLE_CLIENT_SECRET=<google-client-secret>
GOOGLE_SERVICE_ACCOUNT_JSON=/path/to/service-account.json

# === Twilio ===
TWILIO_ACCOUNT_SID=<twilio-account-sid>
TWILIO_AUTH_TOKEN=<twilio-auth-token>
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_VERIFY_SERVICE_SID=<optional>

# === Firebase ===
FIREBASE_PROJECT_ID=<firebase-project-id>
FIREBASE_CREDENTIALS_JSON=/path/to/firebase-key.json

# === SendGrid ===
SENDGRID_API_KEY=<sendgrid-api-key>
EMAIL_FROM=noreply@deepsafe.ai

# === AI/ML Detection ===
OPENAI_API_KEY=<openai-api-key>
OPENAI_MODEL=gpt-4-turbo-preview
RESEMBLE_API_KEY=<resemble-api-key>
SENSITY_API_KEY=<sensity-api-key>

# === Transcription ===
TRANSCRIPTION_API_KEY=<api-key>
TRANSCRIPTION_PROVIDER=whisper

# === Local Models ===
AUDIO_MODEL_PATH=models/audio_deepfake.onnx
VIDEO_MODEL_PATH=models/video_deepfake.onnx

# === AWS ===
AWS_ACCESS_KEY_ID=<access-key>
AWS_SECRET_ACCESS_KEY=<secret-key>
AWS_REGION=us-east-1

# === Monitoring ===
SENTRY_DSN=<sentry-dsn>
LOG_LEVEL=INFO

# === CORS ===
CORS_ORIGINS=https://app.deepsafe.ai
```

---

## 8. Cost Optimization Tips

1. **Batch processing** for non-real-time analysis (30–50% savings on AI APIs)
2. **Redis caching** for repeated API responses (40% reduction in calls)
3. **Open-source fallbacks** — local Wav2Vec 2.0 + EfficientNet-B4 models as backup for Resemble/Sensity (already in pyproject.toml ML dependencies)
4. **AWS SES** instead of SendGrid — free for first 62K emails/month from EC2
5. **Reserved capacity** — annual contracts for 25–40% discounts on cloud services
