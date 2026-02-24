# DeepSafe Meeting Bot — Product Requirements Document

**Document ID:** DS-PRD-001
**Version:** 1.0
**Status:** Draft
**Last Updated:** 2026-02-23
**Owner:** Product
**Classification:** Internal — Confidential

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Product Vision & Strategy](#3-product-vision--strategy)
4. [Target Users & Personas](#4-target-users--personas)
5. [Product Scope](#5-product-scope)
6. [Functional Requirements](#6-functional-requirements)
7. [Non-Functional Requirements](#7-non-functional-requirements)
8. [User Stories & Acceptance Criteria](#8-user-stories--acceptance-criteria)
9. [Information Architecture](#9-information-architecture)
10. [Platform Support Matrix](#10-platform-support-matrix)
11. [Integration Requirements](#11-integration-requirements)
12. [Data & Privacy Requirements](#12-data--privacy-requirements)
13. [Release Strategy & Milestones](#13-release-strategy--milestones)
14. [Pricing & Packaging](#14-pricing--packaging)
15. [Success Metrics & KPIs](#15-success-metrics--kpis)
16. [Competitive Landscape](#16-competitive-landscape)
17. [Risks & Mitigations](#17-risks--mitigations)
18. [Open Questions & Decisions](#18-open-questions--decisions)
19. [Appendices](#19-appendices)

---

## 1. Executive Summary

### 1.1 One-Liner

DeepSafe is an enterprise social engineering defense platform that joins video conferences as a silent bot, detects deepfake audio/video and social engineering tactics in real time, and triggers out-of-band verification workflows to prevent fraud — before money moves.

### 1.2 Why Now

The threat landscape has shifted dramatically. AI-generated voice clones and deepfake video are now commodity capabilities, and the average Business Email Compromise (BEC) attack costs $130,000 per incident. In 2025 alone, deepfake-enabled video call fraud resulted in over $25 million in losses in a single widely-reported case (Arup/Hong Kong). Existing detection-only tools tell you a deepfake is happening but do nothing to stop the transaction. Organizations need a system that detects, verifies, and enforces — not just alerts.

### 1.3 Core Thesis

> "Even if the deepfake is perfect, the attack still fails at verification."

DeepSafe's layered defense ensures that detection failure at any single point does not result in a successful attack. By combining multi-modal deepfake detection with out-of-band identity verification and automated workflow enforcement, the platform creates a security posture where the attacker must defeat every layer simultaneously — a dramatically harder problem than fooling a single detector.

---

## 2. Problem Statement

### 2.1 The Attack Surface

Modern social engineering attacks against enterprises increasingly exploit video conferencing:

| Attack Vector | How It Works | Impact |
|---|---|---|
| **Voice cloning** | Attacker clones executive voice using 30 seconds of public audio, joins call as "CFO" | Unauthorized wire transfers, confidential disclosures |
| **Deepfake video** | Attacker generates real-time face swap during video call | Impersonation of executives in M&A discussions, earnings pre-announcements |
| **Social engineering** | Attacker uses urgency, authority, and isolation tactics to bypass normal approval processes | Finance teams execute payments without standard verification |
| **Hybrid attacks** | Deepfake + social engineering combined: convincing face/voice + manipulative conversation | Highest success rate, hardest to detect via any single method |

### 2.2 Why Existing Solutions Fail

| Solution Category | Example | Gap |
|---|---|---|
| **Audio-only detection** | Resemble AI Detect | No video analysis, no social engineering detection, no mitigation — just an alert |
| **Video-only detection** | GetReal Security, Sensity | No audio analysis, no conversation context, no workflow enforcement |
| **Identity verification** | Beyond Identity | Post-authentication only; doesn't address real-time impersonation during a call |
| **Email security** | Abnormal Security, Proofpoint | Protects email channel, not video; attackers have shifted to video calls precisely because email is now well-defended |

### 2.3 The Gap

No product on the market today combines:
1. Multi-modal deepfake detection (audio + video)
2. Social engineering pattern recognition (conversation-level analysis)
3. Out-of-band identity verification triggered in real time
4. Automated workflow enforcement that blocks transactions until verification completes

DeepSafe fills this gap.

---

## 3. Product Vision & Strategy

### 3.1 Vision Statement

Become the standard-of-care security layer for every enterprise video conference, making AI-powered impersonation attacks economically unviable for attackers.

### 3.2 Strategic Positioning

**DeepSafe = Detection + Verification + Enforcement**

```
┌────────────────────────────────────────────────────────────────────┐
│                     EXISTING MARKET                                │
│                                                                    │
│   Resemble AI          GetReal/Sensity       Beyond Identity       │
│   ┌──────────┐         ┌──────────┐          ┌──────────┐         │
│   │ Audio    │         │ Video    │          │ Identity │         │
│   │ Detect   │         │ Detect   │          │ Verify   │         │
│   └──────────┘         └──────────┘          └──────────┘         │
│        ↓                    ↓                     ↓                │
│     "Alert"              "Alert"              "Logged in"          │
│                                                                    │
│   ── No mitigation ──  ── No audio ──  ── No real-time ──        │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│                       DEEPSAFE                                     │
│                                                                    │
│   ┌──────────────────────────────────────────────────────────┐    │
│   │  Audio Detect + Video Detect + Social Engineering NLP    │    │
│   └──────────────────────────┬───────────────────────────────┘    │
│                              ↓                                     │
│   ┌──────────────────────────────────────────────────────────┐    │
│   │  Risk Score → Policy Engine → Verification Trigger       │    │
│   └──────────────────────────┬───────────────────────────────┘    │
│                              ↓                                     │
│   ┌──────────────────────────────────────────────────────────┐    │
│   │  SMS + Callback + Push → Transaction Gate → Block/Allow  │    │
│   └──────────────────────────────────────────────────────────┘    │
│                                                                    │
│   ── Detect → Verify → Enforce ──                                 │
└────────────────────────────────────────────────────────────────────┘
```

### 3.3 Design Principles

1. **Silent by default.** The bot must never disrupt a legitimate meeting. False positives erode trust faster than false negatives.
2. **Defense in depth.** No single detection signal should be the sole basis for action. Multiple weak signals compose into strong decisions.
3. **Out-of-band or nothing.** Verification must happen through a channel the attacker does not control. In-band "are you really you?" questions are useless against a skilled impersonator.
4. **Zero-trust participants.** Even authenticated users are continuously verified. An account compromise or SIM swap mid-meeting must be caught.
5. **Enterprise-grade from day one.** RBAC, audit logging, SOC 2 compliance readiness, SSO integration. No "we'll add security later."

---

## 4. Target Users & Personas

### 4.1 Primary Personas

#### P1: Chief Information Security Officer (CISO)

| Attribute | Detail |
|---|---|
| **Goal** | Protect the organization from deepfake-enabled fraud without adding friction to every meeting |
| **Pain** | Current tools only detect; they don't prevent. Board asks "what are we doing about deepfakes?" and there's no good answer |
| **Key needs** | Executive-level dashboard, compliance reports, policy control, incident forensics |
| **Success metric** | Zero successful deepfake-enabled fraud incidents per quarter |

#### P2: Security Operations Analyst (SOC Analyst)

| Attribute | Detail |
|---|---|
| **Goal** | Triage deepfake and social engineering alerts efficiently, investigate incidents, resolve or escalate |
| **Pain** | Alert fatigue from noisy tools; no centralized view of meeting-related threats |
| **Key needs** | Real-time incident feed, meeting transcript with risk annotations, one-click escalation, false-positive marking |
| **Success metric** | Mean time to triage < 5 minutes; false positive rate < 5% |

#### P3: Finance Executive (CFO / VP Finance)

| Attribute | Detail |
|---|---|
| **Goal** | Ensure no fraudulent wire transfers are authorized via deepfake impersonation |
| **Pain** | Received an SMS saying "someone is impersonating you in a meeting" — that's terrifying but also means the system works |
| **Key needs** | Quick verification flow (< 2 min), clear approve/deny, trust that the system won't block legitimate transactions |
| **Success metric** | 100% verification completion rate on high-value transactions |

#### P4: IT Administrator

| Attribute | Detail |
|---|---|
| **Goal** | Deploy, configure, and maintain DeepSafe across the organization |
| **Pain** | Complex integrations, SSO setup, policy configuration |
| **Key needs** | Admin console, SSO integration wizard, policy templates, health monitoring |
| **Success metric** | Deployment to first meeting protection in < 1 business day |

### 4.2 Secondary Personas

- **Meeting Host:** Sees trust badges for participants; receives in-meeting alerts when risk is elevated. Needs clear, non-alarming UX.
- **External Participant:** May be prompted for a liveness check in waiting room. Must not feel surveilled or unwelcome.
- **Compliance Officer:** Needs exportable audit trails, verification logs, and incident reports for SOX, PCI-DSS, and regulatory filings.

---

## 5. Product Scope

### 5.1 In Scope (MVP)

| Capability | Description |
|---|---|
| **Meeting bot** | Automated bot joins Zoom and Google Meet calls, captures audio/video streams silently |
| **Audio deepfake detection** | Real-time voice cloning detection via Resemble AI API + spectral/prosody analysis |
| **Video deepfake detection** | Facial manipulation detection via Sensity/GetReal API + facial landmark analysis |
| **Social engineering detection** | 6-metric conversation risk scoring: scenario matching, keyword analysis, GPT-4 semantic analysis, participant validation, metadata anomalies, behavioral analysis |
| **Risk aggregation** | Composite risk score (0–100%) with configurable thresholds for Low/Medium/High/Critical |
| **SMS verification** | Twilio-powered out-of-band SMS code delivery to registered executives |
| **Voice callback verification** | Twilio IVR-based callback with voice biometric verification |
| **Push notification verification** | Firebase-powered mobile app biometric approval |
| **Security dashboard** | Real-time monitoring of active meetings, incident feed, participant risk profiles, meeting history |
| **Incident management** | Detection → investigation → resolution workflow with evidence preservation |
| **Policy engine** | Configurable rules that map risk conditions to automated actions (alert, verify, block, escalate) |
| **RBAC** | Role-based access control: Admin, Security Analyst, User, Viewer roles with granular permissions |
| **Audit logging** | Complete audit trail of all system actions, user actions, and verification events |
| **WebSocket real-time updates** | Live meeting risk scores and incident updates pushed to dashboard |

### 5.2 In Scope (Post-MVP)

| Capability | Target Phase |
|---|---|
| Microsoft Teams integration | Phase 3 |
| Payment system integration (Stripe, NetSuite, SAP) | Phase 3 |
| Dual-approval workflows | Phase 3 |
| SSO integration (Okta, Azure AD, Google Workspace) | Phase 3 |
| SIEM integration (Splunk, Datadog, Sentinel) | Phase 3 |
| Pre-meeting liveness gating (waiting room challenges) | Phase 4 |
| Custom ML model training (reduce API dependency) | Phase 4 |
| Mobile app (iOS + Android) | Phase 4 |
| Threat intelligence feed sharing | Phase 4 |
| White-label / OEM option | Phase 4 |

### 5.3 Out of Scope

- Email phishing detection (adjacent market, different product)
- Endpoint detection and response (EDR)
- Network security monitoring
- Chat/messaging platform monitoring (Slack, WhatsApp calls)
- Consumer / personal use

---

## 6. Functional Requirements

### 6.1 Meeting Bot Service

#### FR-BOT-001: Bot Lifecycle Management

The system must automatically deploy a bot to join a scheduled or ad-hoc meeting when triggered by calendar sync, manual request, or API call.

| Requirement | Detail |
|---|---|
| **Join latency** | Bot must join within 10 seconds of trigger |
| **Silent presence** | Bot must not produce audio, video, or chat messages unless configured by admin |
| **Platform identity** | Bot appears as "DeepSafe Security" (configurable per company) |
| **Auto-leave** | Bot departs when meeting ends or all monitored participants leave |
| **Reconnection** | Bot must auto-reconnect within 15 seconds on network disruption |
| **Concurrent meetings** | System must support ≥ 100 concurrent meeting bots per tenant |

#### FR-BOT-002: Audio Stream Capture

| Requirement | Detail |
|---|---|
| **Capture method** | Platform-native audio stream API (Zoom SDK raw audio, Google Meet API) |
| **Chunk size** | 3-second audio chunks for analysis pipeline |
| **Per-participant isolation** | Audio must be captured per-participant where platform supports it |
| **Sample rate** | Minimum 16kHz, 16-bit PCM |
| **Buffering** | Ring buffer with 30-second lookback for forensic context |

#### FR-BOT-003: Video Stream Capture

| Requirement | Detail |
|---|---|
| **Capture method** | Platform video stream API or screen capture fallback |
| **Frame rate** | 2 FPS target for analysis (downsampled from source; configurable) |
| **Resolution** | Minimum 480p per participant face region |
| **Per-participant** | Individual face isolation via facial detection |
| **Virtual camera detection** | Detect OBS Virtual Camera, Snap Camera, ManyCam, mmhmm |

#### FR-BOT-004: Metadata Collection

| Requirement | Detail |
|---|---|
| **Participant data** | Name, email, device OS, browser, IP address (where available) |
| **Join/leave events** | Timestamped participant join and leave events |
| **Platform-specific** | Meeting title, scheduled time, organizer, recurring status |
| **Geolocation** | IP-based geolocation for impossible travel detection |

---

### 6.2 Detection Engine

#### FR-DET-001: Audio Deepfake Detection

| Requirement | Detail |
|---|---|
| **Primary detector** | Resemble AI Detect API — returns probability score per audio chunk |
| **Fallback detector** | Local Wav2Vec 2.0 model when API is unavailable or for cost optimization |
| **Spectral analysis** | Frequency-domain anomaly detection for synthetic speech artifacts |
| **Prosody analysis** | Speech rhythm, intonation, and cadence consistency over time |
| **A/V sync** | Lip-sync drift detection with 42ms threshold |
| **Latency** | Per-chunk analysis must complete within 3 seconds |
| **Confidence output** | Score 0.0–1.0 with category label (genuine / likely_synthetic / synthetic) |

#### FR-DET-002: Video Deepfake Detection

| Requirement | Detail |
|---|---|
| **Primary detector** | Sensity/GetReal API — frame-level manipulation detection |
| **Fallback detector** | Local EfficientNet-B4 fine-tuned on FaceForensics++ |
| **Facial landmarks** | 68-point facial landmark geometry analysis for face-swap artifacts |
| **Micro-expressions** | Temporal analysis of facial muscle groups for unnatural transitions |
| **Lighting analysis** | Illumination consistency across face regions vs. background |
| **Virtual camera** | Software detection via device enumeration and metadata |
| **Latency** | Per-frame batch analysis (5 frames) must complete within 3 seconds |
| **Confidence output** | Score 0.0–1.0 with category label |

#### FR-DET-003: Social Engineering Detection (6-Metric Scoring)

**Metric A — Scenario Structure Detection (20% weight)**

| Requirement | Detail |
|---|---|
| **Pattern database** | ≥ 500 known BEC/social engineering scenario templates |
| **Categories** | CEO fraud, vendor impersonation, IT support scam, urgent opportunity, authority override |
| **Match method** | Embedding-based similarity scoring (GPT-4 embeddings) |
| **Trigger** | Score > 7/10 enables enhanced real-time monitoring |

**Metric B — Keyword & Phrase Analysis (20% weight)**

| Requirement | Detail |
|---|---|
| **Keyword categories** | Financial ("wire transfer", "payment", "invoice"), Bypassing ("manual process", "system down"), Secrecy ("don't mention", "keep confidential") |
| **Detection** | Real-time transcript scanning with sliding window |
| **Trigger** | 3+ high-risk keywords within 60-second window = yellow flag |

**Metric C — GPT-4 Semantic Analysis (20% weight)**

| Requirement | Detail |
|---|---|
| **API** | OpenAI GPT-4 Turbo (`gpt-4-turbo-preview`) with structured output schema |
| **Analysis** | Intent classification, manipulation tactic identification, risk assessment |
| **Context window** | Rolling 5-minute transcript window for conversational context |
| **Output** | Structured JSON with risk score, reasoning, tactics_detected, recommended_action |

**Metric D — Participant Validation (15% weight)**

| Requirement | Detail |
|---|---|
| **Email verification** | Domain validation, typosquatting detection (e.g., `companv.com` vs `company.com`) |
| **Role verification** | Cross-reference claimed title against corporate directory (SSO/LDAP) |
| **History** | First-time participant flag, meeting frequency analysis |
| **Trigger** | Domain mismatch + financial keywords = immediate verification |

**Metric E — Metadata Anomaly Detection (10% weight)**

| Requirement | Detail |
|---|---|
| **Timing** | Meeting scheduled outside business hours, unscheduled emergency meeting |
| **Location** | Impossible travel (participant in two locations within impossible timeframe) |
| **Device** | Device change mid-meeting, new device for known user |
| **Trigger** | Multiple metadata flags = escalate to IT security |

**Metric F — Behavioral Analysis (15% weight)**

| Requirement | Detail |
|---|---|
| **Pressure tactics** | Time pressure ("we only have 10 minutes"), deadline pressure ("must be done today") |
| **Isolation tactics** | "Don't CC anyone", "direct message only", "keep this between us" |
| **Authority shortcuts** | "Skip the approval process", "emergency authorization" |
| **Speaker dominance** | One participant dominating conversation with financial requests |
| **Trigger** | 2+ pressure tactics = require dual approval |

#### FR-DET-004: Risk Aggregation

| Requirement | Detail |
|---|---|
| **Composite formula** | `Composite = (Deepfake × 0.40) + (Social_Engineering × 0.40) + (Virtual_Camera × 0.20)`, where `Deepfake = (Audio × 0.50) + (Video × 0.50)` |
| **Risk levels** | Low (0–30%), Medium (31–60%), High (61–85%), Critical (86–100%) |
| **Action thresholds** | Alert at 40%, Verify at 65%, Intervene at 85% |
| **Temporal smoothing** | Exponential moving average to prevent score flickering |
| **Per-participant** | Individual risk scores per participant, not just per meeting |

---

### 6.3 Verification Service

#### FR-VER-001: SMS Verification

| Requirement | Detail |
|---|---|
| **Provider** | Twilio SMS API |
| **Code format** | 6-digit numeric, cryptographically random |
| **Delivery** | Send to executive's registered mobile number from corporate directory |
| **Message template** | "DeepSafe Alert: You're being referenced in a meeting requesting [action] of [amount]. Are you in this meeting? Reply YES to confirm / NO to report fraud. Code: [XXXXXX]" |
| **Expiry** | 10 minutes from send |
| **Rate limit** | Max 5 verification attempts per session, max 10 resends per hour |
| **Fallback** | Escalate to voice callback if no response within 3 minutes |

#### FR-VER-002: Voice Callback Verification

| Requirement | Detail |
|---|---|
| **Provider** | Twilio Voice API |
| **IVR flow** | Automated call → state situation → Press 1 (confirm) / Press 2 (fraud) / Press 3 (speak to security) |
| **Voice biometric** | Verification phrase spoken by executive, compared against enrolled voiceprint |
| **Retry** | Up to 3 call attempts at 2-minute intervals |
| **No-answer action** | Transaction automatically blocked, escalated to manual IT security review |

#### FR-VER-003: Push Notification Verification

| Requirement | Detail |
|---|---|
| **Provider** | Firebase Cloud Messaging |
| **Delivery** | Push notification to DeepSafe mobile app on executive's registered device |
| **Verification method** | Biometric approval (Face ID / Touch ID) in mobile app |
| **Content** | Meeting name, requester, action description, Approve/Deny buttons |
| **Audit** | Biometric proof logged with timestamp |

#### FR-VER-004: Risk-Based Channel Selection

The system must automatically select verification channels based on the transaction value and risk score:

| Transaction Value | Risk Score | Required Verification |
|---|---|---|
| < $5,000 | Any | SMS only |
| $5,000–$25,000 | < 60% | SMS + email |
| $5,000–$25,000 | 61–85% | SMS + push notification |
| $5,000–$25,000 | > 85% | SMS + callback + dual approval |
| $25,000–$100,000 | Any | Callback + push + dual approval |
| > $100,000 | Any | All channels + dual approval + 24-hour hold |

#### FR-VER-005: Verification Session Management

| Requirement | Detail |
|---|---|
| **Session ID** | UUID-based, unique per verification event |
| **State machine** | PENDING → SENT → DELIVERED → VERIFIED / FAILED / EXPIRED |
| **Expiry** | Configurable, default 10 minutes |
| **Hold period** | Configurable 24-hour hold for transactions > $100K |
| **Audit trail** | Every state transition logged with timestamp, channel, and actor |

---

### 6.4 Dashboard & Incident Management

#### FR-DASH-001: Real-Time Security Dashboard

| Requirement | Detail |
|---|---|
| **Active meetings** | Live count of monitored meetings with per-meeting risk level indicator |
| **Metrics cards** | Deepfake detections (24h / 7d / 30d), social engineering alerts by severity, verification completion rate, high-risk meetings in progress |
| **Incident feed** | Chronological list of incidents with severity, type, meeting, participant, status |
| **Risk trend** | Line chart of organizational risk score over time |
| **Refresh** | WebSocket-driven real-time updates, no polling |

#### FR-DASH-002: Meeting Detail View

| Requirement | Detail |
|---|---|
| **Meeting metadata** | Platform, title, start/end time, duration, organizer, participant count |
| **Risk timeline** | Time-series graph of risk score throughout the meeting |
| **Participant list** | Each participant with trust badge, risk score, device info, verification status |
| **Transcript** | Full meeting transcript with risk-flagged segments highlighted |
| **Incidents** | All incidents that occurred during the meeting with evidence links |
| **Recording** | Link to meeting recording with timestamped incident markers |

#### FR-DASH-003: Participant Risk Profile

| Requirement | Detail |
|---|---|
| **Identity** | Name, email, organization, role |
| **History** | Total meetings attended, average risk score, verification history |
| **Trust level** | Computed trust score based on historical behavior |
| **Red flags** | List of historical anomalies: domain mismatches, device changes, failed verifications |
| **Status** | Active / Flagged / Blacklisted |

#### FR-DASH-004: Incident Management

| Requirement | Detail |
|---|---|
| **Incident lifecycle** | Detected → Investigating → Verified / Resolved / False Positive |
| **Evidence package** | Audio/video clips, transcript excerpts, detection scores, metadata |
| **Actions** | Verify (confirm real threat), resolve, escalate to security team, mark false positive, blacklist participant |
| **Assignment** | Assign incident to specific analyst |
| **SLA tracking** | Time from detection to first response, time to resolution |

#### FR-DASH-005: Policy Configuration

| Requirement | Detail |
|---|---|
| **Rule builder** | Visual rule builder for creating policy conditions |
| **Condition types** | Risk score threshold, transaction value, participant attributes, meeting metadata, time-of-day |
| **Action types** | Alert (in-meeting, dashboard, email), Verify (SMS, callback, push), Block (transaction hold), Escalate (security team notification) |
| **Templates** | Pre-built policy templates for common scenarios (wire fraud, executive impersonation, vendor payment) |
| **Testing** | Dry-run mode to evaluate policy against historical meetings before activation |

---

### 6.5 Administration

#### FR-ADM-001: User Management

| Requirement | Detail |
|---|---|
| **Roles** | Admin (full access), Security Analyst (incidents + meetings, no settings), User (standard platform access), Viewer (read-only dashboard) |
| **User CRUD** | Create, update, deactivate users with role assignment |
| **SSO** | SAML 2.0 / OIDC integration with Okta, Azure AD, Google Workspace |
| **MFA** | Enforce MFA for all admin users |

#### FR-ADM-002: Company Configuration

| Requirement | Detail |
|---|---|
| **Bot settings** | Bot display name, auto-join rules, platforms enabled |
| **Detection thresholds** | Configurable risk thresholds per company |
| **Verification settings** | Default channels, timeout values, escalation contacts |
| **Directory sync** | Sync employee directory from SSO provider for participant validation |

#### FR-ADM-003: Audit Log

| Requirement | Detail |
|---|---|
| **Scope** | Every user action, system action, API call, policy change, verification event |
| **Fields** | Timestamp, actor, action, resource type, resource ID, before/after values, IP address |
| **Retention** | Configurable, minimum 1 year for compliance |
| **Export** | CSV, JSON, and SIEM-compatible formats |
| **Immutability** | Audit logs must be append-only, never editable or deletable by any user |

---

## 7. Non-Functional Requirements

### 7.1 Performance

| Metric | Target | Rationale |
|---|---|---|
| **End-to-end detection latency** | < 5 seconds from audio/video capture to risk score update | Must be fast enough to alert before transaction is authorized |
| **Per-chunk audio analysis** | < 3 seconds | 3-second audio chunks must be analyzed before the next chunk arrives |
| **Per-batch video analysis** | < 3 seconds per analysis cycle | Must keep pace with 2 FPS capture rate |
| **SMS delivery** | < 5 seconds from trigger to delivery | Critical for time-sensitive verification |
| **Dashboard load time** | < 2 seconds (initial), < 500ms (subsequent) | SOC analysts need instant access |
| **WebSocket latency** | < 200ms from event to dashboard update | Real-time monitoring must feel real-time |
| **API response time** | p95 < 500ms, p99 < 1000ms | Standard enterprise SaaS API performance |

### 7.2 Scalability

| Metric | Target |
|---|---|
| **Concurrent meeting bots** | 100 per tenant, 10,000 system-wide |
| **Concurrent dashboard users** | 500 per tenant |
| **Meeting events processed** | 1,000,000 events / hour system-wide |
| **Audio chunks processed** | 50,000 / minute system-wide |
| **Horizontal scaling** | Stateless services behind load balancer; scale by adding instances |

### 7.3 Availability

| Metric | Target |
|---|---|
| **Uptime SLA** | 99.9% (8.76 hours downtime / year) |
| **Recovery Time Objective (RTO)** | < 15 minutes |
| **Recovery Point Objective (RPO)** | < 1 minute (no data loss for committed transactions) |
| **Deployment** | Zero-downtime deployments via rolling updates |

### 7.4 Security

| Requirement | Detail |
|---|---|
| **Encryption in transit** | TLS 1.3 for all external communications |
| **Encryption at rest** | AES-256 for all stored data (database, object storage, backups) |
| **Authentication** | JWT with short-lived access tokens (30 min) + refresh tokens (7 days) |
| **Authorization** | RBAC enforced at API layer with per-endpoint permission checks |
| **Secrets management** | AWS Secrets Manager or HashiCorp Vault; no secrets in code or config files |
| **Penetration testing** | Annual third-party pentest required before GA |
| **SOC 2 Type II** | Targeted within 12 months of GA |
| **Data residency** | Configurable per tenant (US, EU, APAC) |

### 7.5 Reliability

| Requirement | Detail |
|---|---|
| **Circuit breakers** | All external API calls (Resemble, Sensity, OpenAI, Twilio) wrapped in circuit breakers with fallback behavior |
| **Retry with backoff** | Transient failures retried with exponential backoff + jitter |
| **Graceful degradation** | If external detection API is down, fall back to local model; if local model fails, flag as "unable to verify" (not "clean") |
| **Dead letter queues** | Failed message processing routed to DLQ for manual review |
| **Idempotency** | All verification triggers and transaction gates are idempotent |

### 7.6 Observability

| Requirement | Detail |
|---|---|
| **Structured logging** | JSON-formatted logs with correlation IDs across services (structlog) |
| **Metrics** | Prometheus-format metrics for all services: request rates, latencies, error rates, queue depths, detection scores |
| **Distributed tracing** | OpenTelemetry traces across the full detection pipeline |
| **Alerting** | PagerDuty / Opsgenie integration for P1/P2 incidents |
| **Dashboards** | Grafana dashboards for operational health, detection pipeline performance, API metrics |

---

## 8. User Stories & Acceptance Criteria

### 8.1 Meeting Bot

**US-BOT-001: Auto-join scheduled meeting**

> As a **security admin**, I want the DeepSafe bot to automatically join all meetings on my organization's calendar, so that every meeting is protected without manual intervention.

*Acceptance Criteria:*
- [ ] Bot joins within 10 seconds of meeting start time
- [ ] Bot appears in participant list as "DeepSafe Security" (or configured name)
- [ ] Bot produces no audio or video output
- [ ] Bot captures audio stream from all participants
- [ ] Bot auto-leaves when meeting ends
- [ ] Failure to join is logged and alerted to admin

**US-BOT-002: Manual meeting protection**

> As a **meeting host**, I want to invite the DeepSafe bot to a specific meeting via link or meeting ID, so that I can protect ad-hoc meetings not on the calendar.

*Acceptance Criteria:*
- [ ] Host can submit meeting link via dashboard or API
- [ ] Bot joins within 10 seconds
- [ ] All standard detection capabilities are active
- [ ] Meeting appears in dashboard immediately

---

### 8.2 Detection

**US-DET-001: Deepfake audio alert**

> As a **SOC analyst**, I want to be alerted in real time when synthetic audio is detected in a meeting, so that I can investigate and take action before harm occurs.

*Acceptance Criteria:*
- [ ] Alert appears on dashboard within 5 seconds of detection
- [ ] Alert includes: meeting ID, participant name, confidence score, audio sample reference
- [ ] Risk badge updates from green to red for the affected participant
- [ ] Incident is automatically created in incident management system
- [ ] Alert is sent via configured notification channels (email, Slack, webhook)

**US-DET-002: Social engineering pattern detection**

> As a **CISO**, I want the system to detect social engineering patterns in meeting conversations — not just deepfakes — so that sophisticated attacks that use real identities but manipulative tactics are also caught.

*Acceptance Criteria:*
- [ ] System detects all 6 metric categories (scenario, keywords, GPT-4, participant, metadata, behavioral)
- [ ] Composite social engineering score is computed and visible on dashboard
- [ ] Specific tactics are identified and labeled (e.g., "pressure tactic detected: deadline urgency")
- [ ] Score updates in real time as conversation progresses
- [ ] Historical social engineering patterns are tracked per participant

---

### 8.3 Verification

**US-VER-001: SMS verification of executive identity**

> As a **finance executive**, I want to receive an SMS on my registered phone when someone impersonating me requests a wire transfer in a meeting, so that I can confirm or deny the request through a channel the attacker doesn't control.

*Acceptance Criteria:*
- [ ] SMS arrives within 5 seconds of trigger
- [ ] Message clearly states the meeting, the requested action, and the amount
- [ ] Reply YES confirms; reply NO triggers fraud alert
- [ ] Verification code is included for in-meeting verbal confirmation
- [ ] No response within 3 minutes escalates to voice callback
- [ ] Complete audit trail of verification attempt is logged

**US-VER-002: Voice callback verification**

> As a **CFO**, I want to receive an automated phone call to verify my identity when a high-value transaction (> $50K) is being discussed in a meeting, so that the most critical transactions have the strongest verification.

*Acceptance Criteria:*
- [ ] Call is placed to registered phone number within 30 seconds of trigger
- [ ] IVR provides clear options: confirm (1), deny/fraud (2), speak to security (3)
- [ ] Voice biometric verification is performed if executive confirms
- [ ] Transaction is blocked if no answer after 3 attempts
- [ ] Recording of verification call is stored for audit

---

### 8.4 Dashboard

**US-DASH-001: Real-time meeting monitoring**

> As a **SOC analyst**, I want to see all active meetings with their current risk levels on a single dashboard, so that I can immediately identify which meetings need attention.

*Acceptance Criteria:*
- [ ] All active monitored meetings are visible
- [ ] Each meeting shows: title, platform, participant count, current risk level (color-coded), time elapsed
- [ ] Risk level updates in real time via WebSocket (no page refresh)
- [ ] Clicking a meeting opens the detail view
- [ ] High/critical risk meetings are visually prominent (sorted to top, distinct styling)

**US-DASH-002: Incident investigation**

> As a **SOC analyst**, I want to view a complete evidence package for any incident, so that I can make an informed triage decision without switching between tools.

*Acceptance Criteria:*
- [ ] Incident detail view shows: type, severity, timestamp, risk score at detection
- [ ] Transcript excerpt with flagged sections highlighted
- [ ] Audio/video clip from the moment of detection
- [ ] Detection engine breakdown (which detectors fired, with what confidence)
- [ ] Participant risk profile linked
- [ ] One-click actions: resolve, escalate, false-positive

---

### 8.5 Policy & Administration

**US-ADM-001: Custom policy creation**

> As a **security admin**, I want to create custom policies that define what actions the system takes at different risk levels, so that I can tailor the response to my organization's risk tolerance and approval processes.

*Acceptance Criteria:*
- [ ] Admin can create a policy with conditions (risk score, transaction value, participant attributes)
- [ ] Admin can assign actions to conditions (alert, verify, block, escalate)
- [ ] Policies can be enabled/disabled without deletion
- [ ] Policies can be tested in dry-run mode against historical data
- [ ] Policy changes are logged in audit trail

---

## 9. Information Architecture

### 9.1 Dashboard Navigation

```
DeepSafe Dashboard
├── Overview (Home)
│   ├── Active Meetings (live count + list)
│   ├── Key Metrics (detections, alerts, verifications)
│   ├── Risk Trend Chart
│   └── Recent Incidents Feed
│
├── Meetings
│   ├── Active Meetings
│   ├── Meeting History (filterable)
│   └── Meeting Detail
│       ├── Risk Timeline
│       ├── Participants
│       ├── Transcript
│       ├── Incidents
│       └── Recording
│
├── Participants
│   ├── All Participants (searchable)
│   ├── Flagged Participants
│   ├── Blacklisted
│   └── Participant Profile
│       ├── Identity & History
│       ├── Risk Profile
│       └── Verification History
│
├── Incidents
│   ├── Active Incidents
│   ├── Resolved
│   ├── False Positives
│   └── Incident Detail
│       ├── Evidence Package
│       ├── Timeline
│       └── Actions
│
├── Policies
│   ├── Active Policies
│   ├── Policy Templates
│   └── Policy Editor
│
├── Settings (Admin only)
│   ├── Company Configuration
│   ├── User Management
│   ├── SSO Configuration
│   ├── Notification Settings
│   ├── Detection Thresholds
│   └── Integration Settings
│
├── Reports
│   ├── Weekly Security Digest
│   ├── Compliance Reports
│   ├── Audit Log
│   └── Export
│
└── Help & Support
```

---

## 10. Platform Support Matrix

| Platform | MVP Support | Bot Method | Audio Capture | Video Capture | In-Meeting Overlay |
|---|---|---|---|---|---|
| **Zoom** | Yes | Zoom Meeting SDK Bot | Native audio stream API | Video stream API | Zoom Apps SDK overlay |
| **Google Meet** | Yes | Puppeteer headless browser bot | Audio capture via browser API | Screen capture / video API | Overlay not natively supported (dashboard only) |
| **Microsoft Teams** | Post-MVP | Microsoft Bot Framework | Teams media API | Teams media API | Teams Messaging Extension |
| **Webex** | Future | TBD | TBD | TBD | TBD |

---

## 11. Integration Requirements

### 11.1 Identity Providers (SSO)

| Provider | Protocol | Purpose |
|---|---|---|
| Okta | SAML 2.0 / OIDC | User authentication + directory sync |
| Azure AD | SAML 2.0 / OIDC | User authentication + directory sync |
| Google Workspace | OIDC | User authentication + directory sync |

### 11.2 Communication Platforms

| Platform | Integration | Purpose |
|---|---|---|
| Slack | Slack App (Bot) | Alert notifications, verification request delivery |
| Microsoft Teams | Teams App | Alert notifications (post-MVP) |
| Email (SendGrid) | API | Verification emails, weekly digests, compliance reports |

### 11.3 Calendar Systems

| System | Integration | Purpose |
|---|---|---|
| Google Calendar | Google Calendar API | Auto-detect meetings for bot deployment |
| Microsoft Outlook | Microsoft Graph API | Auto-detect meetings for bot deployment |

### 11.4 SIEM & Security Tools

| System | Integration | Purpose |
|---|---|---|
| Splunk | HEC (HTTP Event Collector) | Real-time security event export |
| Datadog | API + Agent | Metrics, logs, and traces |
| Microsoft Sentinel | API | Security event correlation |
| Generic webhook | HTTP POST | Custom integrations |

### 11.5 Payment & ERP Systems (Post-MVP)

| System | Integration | Purpose |
|---|---|---|
| Stripe | API | Transaction gating for payment approvals |
| NetSuite | SuiteTalk API | ERP transaction verification |
| SAP | RFC/BAPI | Enterprise payment approval workflows |
| Bill.com | API | AP/AR transaction gating |

---

## 12. Data & Privacy Requirements

### 12.1 Data Classification

| Data Type | Classification | Retention | Encryption |
|---|---|---|---|
| Meeting audio/video streams | Confidential | Processed in-memory only; not stored unless incident detected | TLS in transit |
| Meeting transcripts | Confidential | 90 days default (configurable per tenant) | AES-256 at rest |
| Incident evidence (audio/video clips) | Highly Confidential | 1 year minimum (compliance requirement) | AES-256 at rest |
| Risk scores and detection results | Internal | 1 year | AES-256 at rest |
| Verification logs | Regulatory | 7 years (SOX requirement) | AES-256 at rest |
| Audit logs | Regulatory | 7 years | AES-256 at rest, append-only |
| User PII (name, email, phone) | Personal | Account lifetime + 30 days post-deletion | AES-256 at rest |

### 12.2 Privacy Principles

1. **Minimum necessary processing.** Audio and video streams are analyzed in real time and discarded. Only flagged segments are persisted as evidence.
2. **Participant notice.** All meeting participants must be informed that the meeting is being monitored for security purposes. Bot presence serves as notice.
3. **Data subject rights.** Support GDPR right of access, rectification, and erasure (where not in conflict with regulatory retention requirements).
4. **Cross-border transfer.** Data processing must respect data residency configuration. EU tenant data must be processed in EU region.
5. **Consent management.** Organizations are responsible for obtaining appropriate consent from participants per their jurisdiction. DeepSafe provides configurable disclosure messages.

### 12.3 Compliance Targets

| Standard | Timeline | Key Requirements |
|---|---|---|
| SOC 2 Type I | Within 6 months of GA | Security, availability, confidentiality trust principles |
| SOC 2 Type II | Within 12 months of GA | Sustained compliance over observation period |
| GDPR | At GA | Data processing agreement, privacy impact assessment, data residency |
| HIPAA | Phase 4 | BAA support, PHI handling, audit controls |
| PCI-DSS | Phase 4 | For payment system integration features |

---

## 13. Release Strategy & Milestones

### 13.1 Phase Plan

| Phase | Name | Duration | Key Deliverables |
|---|---|---|---|
| **Phase 1** | Foundation | Months 1–3 | Backend framework, database schema, API service, authentication, RBAC |
| **Phase 2** | Detection Core | Months 3–5 | Audio deepfake detection, video deepfake detection, social engineering engine, risk aggregator |
| **Phase 3** | Verification & Integration | Months 5–7 | SMS verification, voice callback, push notifications, Zoom integration, Google Meet integration |
| **Phase 4** | Stream Processing & Workflow | Months 7–9 | Real-time stream pipeline, policy engine, workflow automation, calendar sync |
| **Phase 5** | Dashboard & Polish | Months 9–11 | Full security dashboard, incident management, reporting, admin console |
| **Phase 6** | Enterprise & GA | Months 11–13 | SSO integration, SIEM integration, SOC 2 audit prep, performance testing, GA launch |

### 13.2 Current Status

| Phase | Status | Notes |
|---|---|---|
| Phase 1 — Foundation | Complete | Backend framework, database schema, API service, auth |
| Phase 2 — API Service | Complete | RESTful API with 166+ tests |
| Phase 3 — Detection Engine | Complete | Audio, video, and social engineering detection |
| Phase 4 — Verification Service | Complete | Multi-channel verification (SMS, voice, push, email) |
| Phase 5 — Platform Integrations | Complete | Zoom + Google Meet bot integrations |
| Phase 6 — Stream Processing Pipeline | In Progress | Audio buffer complete (30 tests), alert generator in progress (28 passing, 10 failing), video queue implemented |
| Phase 7 — Dashboard & Polish | In Progress (parallel) | React dashboard with real-time monitoring, meeting history, participant views |
| Phase 8 — Enterprise & GA | Not Started | SSO, SIEM, SOC 2 audit prep |

### 13.3 MVP Definition

The MVP is the minimum set of capabilities required to onboard the first 5 design-partner customers:

- Zoom meeting bot with auto-join
- Audio deepfake detection (Resemble AI)
- Video deepfake detection (Sensity)
- Social engineering detection (3 of 6 metrics: keywords, GPT-4, participant validation)
- SMS verification
- Security dashboard (active meetings, incidents, participant profiles)
- Admin user management with RBAC
- Audit logging

---

## 14. Pricing & Packaging

### 14.1 Tier Structure

| Tier | Monthly Price | Target | Capabilities |
|---|---|---|---|
| **Starter** | $499/mo | SMB (≤ 100 employees) | Detection only (audio + video), in-meeting alerts, basic dashboard |
| **Professional** | $1,499/mo | Mid-market (≤ 500 employees) | Detection + SMS verification, social engineering analysis, SSO integration, compliance reports |
| **Enterprise** | Custom | Large enterprise (unlimited) | Full verification suite (SMS + callback + push), dual-approval workflows, SIEM integration, dedicated support, custom policies, white-label option |

### 14.2 Add-Ons

| Add-On | Price | Description |
|---|---|---|
| Incident response retainer | $5,000/mo | Priority access to DeepSafe security team for incident investigation |
| Custom scenario training | $10,000 one-time | Industry-specific social engineering scenario library customization |
| API access | $2,000/mo | RESTful API for custom integrations and automation |
| Additional meeting bots | $50/bot/mo | Beyond tier-included concurrent bot limit |

---

## 15. Success Metrics & KPIs

### 15.1 Product KPIs

| KPI | Definition | Target | Measurement |
|---|---|---|---|
| **Attack Prevention Rate** | % of detected high-risk meetings where verification prevented fraud | > 95% | Incident resolution data |
| **Deepfake Detection Accuracy** | True positive rate for deepfake audio/video detection | > 95% | Model evaluation against labeled dataset |
| **False Positive Rate** | % of high-risk flags on legitimate meetings | < 5% | Incidents marked as false positive / total incidents |
| **Verification Completion Time** | Average time from verification trigger to verified/denied | < 2 min (SMS), < 5 min (callback) | Verification session timestamps |
| **End-to-End Detection Latency** | Time from audio/video capture to risk score visible on dashboard | < 5 seconds | Pipeline instrumentation |

### 15.2 Business KPIs

| KPI | Definition | Target (Year 1) |
|---|---|---|
| **Design Partners** | Paying customers in pre-GA phase | 5 |
| **ARR** | Annual Recurring Revenue | $500K |
| **NRR** | Net Revenue Retention | > 120% |
| **Time to Protection** | Time from contract to first meeting protected | < 1 business day |
| **NPS** | Net Promoter Score | > 40 |

### 15.3 Operational KPIs

| KPI | Definition | Target |
|---|---|---|
| **System Uptime** | Availability of detection + verification services | 99.9% |
| **Incident Response Time** | Time from critical alert to security team action | < 10 minutes |
| **User Adoption** | % of organization's meetings protected by DeepSafe | > 80% within 90 days |
| **Verification Compliance** | % of mandatory verifications that are completed | 100% |

---

## 16. Competitive Landscape

### 16.1 Feature Comparison

| Capability | Resemble AI | GetReal Security | Beyond Identity | Pindrop | **DeepSafe** |
|---|:---:|:---:|:---:|:---:|:---:|
| Audio deepfake detection | Yes | Yes | — | Yes | **Yes** |
| Video deepfake detection | — | Yes | — | — | **Yes** |
| Social engineering NLP | — | — | — | — | **Yes** |
| Real-time meeting monitoring | Yes | — | — | — | **Yes** |
| Out-of-band verification | — | — | Yes | — | **Yes** |
| Multi-channel verification | — | — | Partial | — | **Yes** |
| Automated workflow enforcement | — | — | — | — | **Yes** |
| Transaction gating | — | — | — | — | **Yes** |
| Dual-approval workflows | — | — | — | — | **Yes** |
| Enterprise SSO | — | — | Yes | — | **Yes** |
| Compliance reporting | — | — | — | — | **Yes** |

### 16.2 Competitive Moat

1. **Layered defense architecture.** Competitors address one vector. DeepSafe addresses detection + verification + enforcement end-to-end.
2. **Social engineering detection.** Novel 6-metric scoring system with GPT-4 semantic analysis is not available from any competitor.
3. **Out-of-band verification integration.** No competitor triggers out-of-band verification from within a live meeting.
4. **Policy engine.** Configurable, organization-specific response automation — not one-size-fits-all alerting.

---

## 17. Risks & Mitigations

| # | Risk | Severity | Probability | Mitigation |
|---|---|---|---|---|
| R1 | **API vendor lock-in.** Heavy dependence on Resemble AI and Sensity APIs for detection. If pricing changes or service degrades, product is impacted. | High | Medium | Maintain local fallback models (Wav2Vec 2.0, EfficientNet-B4). Abstract detection behind interface layer for easy provider swap. |
| R2 | **False positive fatigue.** If false positive rate exceeds 5%, users will ignore alerts and the product becomes shelfware. | Critical | Medium | Invest heavily in tuning. Implement temporal smoothing, multi-signal correlation, and per-organization threshold calibration. Easy false-positive feedback loop. |
| R3 | **Platform API changes.** Zoom, Google Meet, or Teams may change APIs, restrict bot access, or launch competing features. | High | Medium | Maintain active partnership conversations. Invest in multiple platform support to reduce single-platform dependency. Monitor developer changelog. |
| R4 | **Detection evasion.** Attackers develop techniques to evade detection (e.g., adversarial attacks on deepfake detectors). | High | High | This is why verification layer exists. Detection is one layer; verification is the ultimate backstop. Continuously update detection models. Red-team exercises quarterly. |
| R5 | **Regulatory compliance.** Recording and analyzing meeting content may conflict with privacy regulations in certain jurisdictions. | Medium | Medium | Process audio/video in memory only (don't persist unless incident). Provide configurable data residency. Obtain legal review per target jurisdiction. Participant notice via bot presence. |
| R6 | **Latency budget.** Real-time pipeline must complete within 5 seconds. External API calls (Resemble, OpenAI) may introduce unpredictable latency. | Medium | Medium | Parallel execution of detection tasks. Circuit breakers with fast fallback to local models. Pre-allocated connection pools. |
| R7 | **Adoption friction.** Enterprise buyers may be slow to adopt a meeting security tool due to perceived meeting disruption. | Medium | High | Design for zero meeting disruption. Bot is silent. All alerts go to SOC dashboard, not participants. Emphasize "invisible protection." |

---

## 18. Open Questions & Decisions

| # | Question | Status | Decision | Date |
|---|---|---|---|---|
| OQ-1 | Should the bot produce any in-meeting visual overlay (trust badges visible to participants), or should all feedback be dashboard-only in MVP? | Open | — | — |
| OQ-2 | How do we handle meetings with end-to-end encryption (E2EE) where audio/video streams are not accessible to the bot? | Open | — | — |
| OQ-3 | Should we build a mobile app for verification flows (push notification + biometric), or use SMS/voice-only for MVP? | Decided | SMS + voice for MVP; mobile app in Phase 4 | — |
| OQ-4 | What is the minimum number of social engineering metrics needed for MVP (all 6, or a subset)? | Decided | 3 of 6 for MVP: keywords, GPT-4 semantic, participant validation | — |
| OQ-5 | Do we need to support self-hosted / on-premises deployment for regulated industries (banking, government)? | Open | — | — |
| OQ-6 | How do we price per-meeting-minute vs. per-employee vs. flat tier? | Decided | Per-employee tier pricing (simpler to sell, predictable revenue) | — |
| OQ-7 | Should we pursue Zoom Marketplace listing for distribution, or direct sales only? | Open | — | — |

---

## 19. Appendices

### Appendix A: Glossary

| Term | Definition |
|---|---|
| **BEC** | Business Email Compromise — a type of fraud where an attacker impersonates a trusted person to trick employees into transferring money or sensitive data |
| **Deepfake** | AI-generated synthetic media (audio or video) designed to impersonate a real person |
| **OOB Verification** | Out-of-band verification — identity confirmation through a separate communication channel (e.g., SMS, phone call) that the attacker does not control |
| **Risk Score** | A composite 0–100% score representing the likelihood that a participant or meeting involves a security threat |
| **Trust Badge** | A visual indicator (green/yellow/red/gray) representing a participant's verified identity and risk status |
| **Social Engineering** | Psychological manipulation techniques used to trick people into taking actions or revealing confidential information |
| **IVR** | Interactive Voice Response — automated phone system that interacts with callers through voice and keypad input |
| **Liveness Check** | A challenge-response test to confirm a video call participant is a real, present human (e.g., "touch your nose") |

### Appendix B: User Journey — Deepfake Attack Prevention

```
┌──────────────────────────────────────────────────────────────┐
│  1. Meeting starts on Zoom                                    │
│     DeepSafe bot auto-joins from calendar sync                │
└──────────────────────────┬───────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│  2. Attacker joins as "CFO" using voice clone + face swap     │
│     Bot captures audio/video streams for all participants     │
└──────────────────────────┬───────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│  3. Detection engine flags:                                   │
│     • Audio deepfake: 87% confidence (Resemble AI)            │
│     • Video deepfake: 72% confidence (Sensity)                │
│     • Social engineering: "wire transfer" + urgency keywords  │
│     → Composite risk score: 91% (CRITICAL)                    │
└──────────────────────────┬───────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│  4. Policy engine triggers verification workflow:             │
│     • SMS sent to real CFO's registered phone                 │
│     • Dashboard alert pushed to SOC analyst                   │
│     • Transaction gate activated (any wire transfer blocked)  │
└──────────────────────────┬───────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│  5a. Real CFO replies "NO" to SMS                             │
│      → Fraud confirmed                                        │
│      → Attacker's participant badge turns red                 │
│      → IT security team notified                              │
│      → Incident report auto-generated with evidence           │
│                                                               │
│  5b. No response within 3 minutes                             │
│      → Voice callback initiated to CFO                        │
│      → Transaction remains blocked until verified             │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│  6. Attack prevented. $0 lost. Full forensic trail preserved. │
└──────────────────────────────────────────────────────────────┘
```

### Appendix C: References

- Arup deepfake fraud case ($25M loss, 2024)
- FBI IC3 2024 Internet Crime Report — BEC losses
- Resemble AI Detect API documentation
- Sensity Deepfake Detection API documentation
- NIST SP 800-63B Digital Identity Guidelines
- Zoom Meeting SDK Developer Documentation
- Google Meet REST API Reference

---

*End of Document*
