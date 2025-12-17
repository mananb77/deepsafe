# **DeepSafe Technical Requirements**

## **Table of Contents**

1. [Application Technical Requirements](https://claude.ai/chat/c56f36e3-3a61-45e1-a296-171ce1bcdbd0#application-tech-requirements)  
2. [Dashboard Technical Requirements](https://claude.ai/chat/c56f36e3-3a61-45e1-a296-171ce1bcdbd0#dashboard-tech-requirements)

---

# **Part 1: Application Technical Requirements {\#application-tech-requirements}**

## **1\. System Architecture**

### **1.1 High-Level Architecture**

┌─────────────────────────────────────────────────────────────────┐  
│                        CLIENT LAYER                             │  
├─────────────────────────────────────────────────────────────────┤  
│                                                                 │  
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │  
│  │    Zoom      │  │ Google Meet  │  │ MS Teams     │         │  
│  │     SDK      │  │     SDK      │  │    SDK       │         │  
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │  
│         │                  │                  │                 │  
└─────────┼──────────────────┼──────────────────┼─────────────────┘  
          │                  │                  │  
          └──────────────────┴──────────────────┘  
                             │  
┌─────────────────────────────┼─────────────────────────────────┐  
│                    API GATEWAY LAYER                           │  
├────────────────────────────────────────────────────────────────┤  
│                                                                │  
│  ┌──────────────────────────────────────────────────────────┐ │  
│  │  Kong API Gateway / AWS API Gateway                      │ │  
│  │  • Rate limiting                                         │ │  
│  │  • Authentication (JWT)                                  │ │  
│  │  • Request routing                                       │ │  
│  │  • Load balancing                                        │ │  
│  └──────────────────────────────────────────────────────────┘ │  
│                                                                │  
└─────────────────────────────┬──────────────────────────────────┘  
                              │  
┌─────────────────────────────┼─────────────────────────────────┐  
│                    APPLICATION LAYER                           │  
├────────────────────────────────────────────────────────────────┤  
│                                                                │  
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐  │  
│  │   Real-Time     │  │   Detection     │  │ Verification │  │  
│  │   Processing    │  │    Engine       │  │   Service    │  │  
│  │   Service       │  │                 │  │              │  │  
│  │  (WebSocket)    │  │  • Audio AI     │  │ • SMS (Twilio│  │  
│  │                 │  │  • Video AI     │  │ • Voice Call │  │  
│  │  • Stream mgmt  │  │  • NLP Analysis │  │ • Push Notif │  │  
│  │  • Transcription│  │  • Risk Scoring │  │ • Email      │  │  
│  └─────────────────┘  └─────────────────┘  └──────────────┘  │  
│                                                                │  
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐  │  
│  │   Workflow      │  │   Integration   │  │  Analytics   │  │  
│  │   Engine        │  │    Service      │  │   Service    │  │  
│  │                 │  │                 │  │              │  │  
│  │  • Policy rules │  │  • SSO (Okta)   │  │ • Metrics    │  │  
│  │  • Dual approval│  │  • SIEM export  │  │ • Reporting  │  │  
│  │  • Gating logic │  │  • Slack/Teams  │  │ • Dashboards │  │  
│  └─────────────────┘  └─────────────────┘  └──────────────┘  │  
│                                                                │  
└─────────────────────────────┬──────────────────────────────────┘  
                              │  
┌─────────────────────────────┼─────────────────────────────────┐  
│                        DATA LAYER                              │  
├────────────────────────────────────────────────────────────────┤  
│                                                                │  
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │  
│  │  PostgreSQL  │  │    Redis     │  │  MongoDB     │        │  
│  │              │  │              │  │              │        │  
│  │ • Users      │  │ • Sessions   │  │ • Transcripts│        │  
│  │ • Meetings   │  │ • Real-time  │  │ • Logs       │        │  
│  │ • Incidents  │  │   data       │  │ • Unstructured│       │  
│  │ • Policies   │  │ • Cache      │  │   data       │        │  
│  └──────────────┘  └──────────────┘  └──────────────┘        │  
│                                                                │  
│  ┌──────────────┐  ┌──────────────┐                          │  
│  │     S3       │  │  Elasticsearch│                          │  
│  │              │  │              │                          │  
│  │ • Recordings │  │ • Full-text  │                          │  
│  │ • Forensics  │  │   search     │                          │  
│  │ • Exports    │  │ • Logs       │                          │  
│  └──────────────┘  └──────────────┘                          │  
│                                                                │  
└────────────────────────────────────────────────────────────────┘

### **1.2 Microservices Architecture**

**Core Services:**

1. **Meeting Bot Service**

   * Joins video conferences  
   * Captures audio/video streams  
   * Manages real-time state  
2. **Detection Service**

   * Audio deepfake detection  
   * Video deepfake detection  
   * Behavioral analysis  
3. **Analysis Service**

   * NLP/conversation analysis  
   * Risk scoring engine  
   * Pattern matching  
4. **Verification Service**

   * SMS gateway integration  
   * Voice call automation  
   * Push notification management  
5. **Workflow Service**

   * Policy evaluation  
   * Approval workflows  
   * Transaction gating  
6. **Integration Service**

   * SSO providers  
   * Corporate directories  
   * SIEM systems  
   * Payment platforms  
7. **API Service**

   * REST API endpoints  
   * GraphQL API  
   * WebSocket server

---

## **2\. Technology Stack**

### **2.1 Backend Services**

Core Application:  
  Language: Python 3.11+  
  Framework: FastAPI 0.104+  
  Async Runtime: asyncio, uvicorn  
    
Real-Time Processing:  
  WebSocket Server: Python websockets / Socket.IO  
  Message Queue: Apache Kafka / AWS Kinesis  
  Stream Processing: Apache Flink / AWS Kinesis Analytics  
    
Background Tasks:  
  Task Queue: Celery  
  Message Broker: RabbitMQ / AWS SQS  
  Scheduler: Celery Beat / AWS EventBridge

### **2.2 AI/ML Stack**

Deepfake Detection:  
  Audio:  
    \- Resemble AI API (primary)  
    \- Backup: Custom PyTorch model  
    \- Model: Wav2Vec 2.0 fine-tuned  
    
  Video:  
    \- Sensity API / GetReal API (primary)  
    \- Backup: Custom model (FaceForensics++ trained)  
    \- Framework: PyTorch 2.0+  
    \- Architecture: EfficientNet-B4 \+ Temporal analysis  
    
NLP/Conversation Analysis:  
  \- OpenAI GPT-4 API (primary analysis)  
  \- Backup: Anthropic Claude API  
  \- Local: sentence-transformers for embeddings  
  \- Pattern matching: spaCy 3.5+  
    
ML Infrastructure:  
  \- Training: PyTorch Lightning  
  \- Inference: TorchServe / AWS SageMaker  
  \- Model versioning: MLflow  
  \- Feature store: Feast

### **2.3 Data Storage**

Primary Database:  
  Type: PostgreSQL 15+  
  HA: Primary \+ Read replicas  
  Connection Pool: PgBouncer  
  ORM: SQLAlchemy 2.0+ / Alembic (migrations)  
    
Cache Layer:  
  Type: Redis 7.0+  
  Mode: Cluster mode  
  Use cases:  
    \- Session storage  
    \- Real-time meeting state  
    \- Rate limiting  
    \- Cache for expensive queries  
    
Document Store:  
  Type: MongoDB 6.0+  
  Use cases:  
    \- Meeting transcripts  
    \- Unstructured logs  
    \- Forensic metadata  
    
Search Engine:  
  Type: Elasticsearch 8.0+  
  Use cases:  
    \- Full-text search (transcripts, meetings)  
    \- Log aggregation  
    \- Analytics queries  
    
Object Storage:  
  Type: AWS S3 / MinIO  
  Use cases:  
    \- Video/audio recordings  
    \- Forensic evidence files  
    \- Export files  
    \- Backup archives  
  Lifecycle:  
    \- Hot: 30 days (S3 Standard)  
    \- Warm: 90 days (S3 IA)  
    \- Cold: 365+ days (S3 Glacier)

### **2.4 External APIs & SDKs**

Video Conferencing:  
  Zoom:  
    \- Zoom Apps SDK  
    \- Zoom Webhook API  
    \- Zoom REST API v2  
    
  Google Meet:  
    \- Google Workspace API  
    \- Meet Add-ons SDK  
    
  Microsoft Teams:  
    \- Microsoft Graph API  
    \- Teams Apps SDK  
    \- Bot Framework  
    
Verification Services:  
  Twilio:  
    \- SMS API  
    \- Voice API  
    \- Verify API  
    
  Firebase:  
    \- Cloud Messaging (Push notifications)  
    
Authentication:  
  \- Okta SDK  
  \- Azure AD MSAL  
  \- Google Workspace OAuth 2.0  
    
AI Services:  
  \- OpenAI API (GPT-4)  
  \- Resemble AI API  
  \- Sensity/GetReal API  
  \- AWS Transcribe (backup transcription)

### **2.5 Infrastructure & DevOps**

Container Orchestration:  
  Platform: Kubernetes (AWS EKS / GKE)  
  Version: 1.28+  
    
Containerization:  
  Runtime: Docker 24+  
  Registry: AWS ECR / Google GCR  
    
CI/CD:  
  Pipeline: GitHub Actions / GitLab CI  
  Deployment: ArgoCD / Flux  
  Testing: pytest, jest  
    
Monitoring:  
  Metrics: Prometheus \+ Grafana  
  Logging: ELK Stack (Elasticsearch, Logstash, Kibana)  
  Tracing: Jaeger / AWS X-Ray  
  APM: Datadog / New Relic  
    
Alerting:  
  PagerDuty integration  
  Slack notifications  
  Email alerts  
    
Infrastructure as Code:  
  Terraform 1.5+  
  Helm charts for K8s

---

## **3\. Data Models**

### **3.1 Core Database Schema (PostgreSQL)**

\-- Users table  
CREATE TABLE users (  
    id UUID PRIMARY KEY DEFAULT gen\_random\_uuid(),  
    email VARCHAR(255) UNIQUE NOT NULL,  
    name VARCHAR(255) NOT NULL,  
    phone VARCHAR(20),  
    department VARCHAR(100),  
    role VARCHAR(100),  
    company\_id UUID REFERENCES companies(id),  
    sso\_provider VARCHAR(50),  
    sso\_user\_id VARCHAR(255),  
    is\_active BOOLEAN DEFAULT true,  
    is\_blacklisted BOOLEAN DEFAULT false,  
    blacklist\_reason TEXT,  
    created\_at TIMESTAMP DEFAULT NOW(),  
    updated\_at TIMESTAMP DEFAULT NOW()  
);

CREATE INDEX idx\_users\_email ON users(email);  
CREATE INDEX idx\_users\_company ON users(company\_id);  
CREATE INDEX idx\_users\_blacklisted ON users(is\_blacklisted) WHERE is\_blacklisted \= true;

\-- Companies table  
CREATE TABLE companies (  
    id UUID PRIMARY KEY DEFAULT gen\_random\_uuid(),  
    name VARCHAR(255) NOT NULL,  
    domain VARCHAR(255) NOT NULL,  
    subscription\_tier VARCHAR(50) NOT NULL, \-- starter, professional, enterprise  
    is\_active BOOLEAN DEFAULT true,  
    settings JSONB DEFAULT '{}',  
    created\_at TIMESTAMP DEFAULT NOW(),  
    updated\_at TIMESTAMP DEFAULT NOW()  
);

\-- Meetings table  
CREATE TABLE meetings (  
    id UUID PRIMARY KEY DEFAULT gen\_random\_uuid(),  
    external\_meeting\_id VARCHAR(255) NOT NULL, \-- Zoom/Teams meeting ID  
    platform VARCHAR(50) NOT NULL, \-- zoom, google\_meet, teams  
    meeting\_name VARCHAR(500),  
    host\_user\_id UUID REFERENCES users(id),  
    company\_id UUID REFERENCES companies(id),  
    started\_at TIMESTAMP,  
    ended\_at TIMESTAMP,  
    duration\_minutes INTEGER,  
    risk\_score DECIMAL(5,2), \-- 0.00 to 100.00  
    risk\_category VARCHAR(20), \-- low, medium, high, critical  
    status VARCHAR(50), \-- active, completed, terminated, flagged  
    is\_compromised BOOLEAN DEFAULT false,  
    recording\_url TEXT,  
    transcript\_id UUID, \-- Reference to MongoDB document  
    metadata JSONB DEFAULT '{}',  
    created\_at TIMESTAMP DEFAULT NOW(),  
    updated\_at TIMESTAMP DEFAULT NOW()  
);

CREATE INDEX idx\_meetings\_company ON meetings(company\_id);  
CREATE INDEX idx\_meetings\_host ON meetings(host\_user\_id);  
CREATE INDEX idx\_meetings\_risk ON meetings(risk\_score DESC);  
CREATE INDEX idx\_meetings\_compromised ON meetings(is\_compromised) WHERE is\_compromised \= true;  
CREATE INDEX idx\_meetings\_date ON meetings(started\_at DESC);

\-- Participants table  
CREATE TABLE participants (  
    id UUID PRIMARY KEY DEFAULT gen\_random\_uuid(),  
    meeting\_id UUID REFERENCES meetings(id) ON DELETE CASCADE,  
    user\_id UUID REFERENCES users(id),  
    display\_name VARCHAR(255),  
    email VARCHAR(255),  
    role VARCHAR(50), \-- host, participant, guest  
    joined\_at TIMESTAMP,  
    left\_at TIMESTAMP,  
    duration\_minutes INTEGER,  
    trust\_score DECIMAL(5,2), \-- 0.00 to 100.00  
    audio\_risk\_score DECIMAL(5,2),  
    video\_risk\_score DECIMAL(5,2),  
    credential\_risk\_score DECIMAL(5,2),  
    device\_fingerprint TEXT,  
    ip\_address INET,  
    location\_country VARCHAR(2),  
    location\_city VARCHAR(100),  
    is\_flagged BOOLEAN DEFAULT false,  
    flag\_reason TEXT,  
    verification\_status VARCHAR(50), \-- verified, failed, pending, not\_required  
    metadata JSONB DEFAULT '{}',  
    created\_at TIMESTAMP DEFAULT NOW(),  
    updated\_at TIMESTAMP DEFAULT NOW()  
);

CREATE INDEX idx\_participants\_meeting ON participants(meeting\_id);  
CREATE INDEX idx\_participants\_user ON participants(user\_id);  
CREATE INDEX idx\_participants\_flagged ON participants(is\_flagged) WHERE is\_flagged \= true;

\-- Incidents table  
CREATE TABLE incidents (  
    id UUID PRIMARY KEY DEFAULT gen\_random\_uuid(),  
    incident\_code VARCHAR(50) UNIQUE NOT NULL, \-- INC-20241211-001  
    meeting\_id UUID REFERENCES meetings(id),  
    participant\_id UUID REFERENCES participants(id),  
    company\_id UUID REFERENCES companies(id),  
    incident\_type VARCHAR(100) NOT NULL, \-- deepfake\_audio, deepfake\_video, social\_engineering, bec  
    severity VARCHAR(20) NOT NULL, \-- low, medium, high, critical  
    risk\_score DECIMAL(5,2),  
    status VARCHAR(50) NOT NULL, \-- active, resolved, investigating, false\_positive  
    detected\_at TIMESTAMP NOT NULL,  
    resolved\_at TIMESTAMP,  
    resolution VARCHAR(50), \-- prevented, blocked, escalated, false\_alarm  
    amount\_protected DECIMAL(15,2), \-- Financial amount if applicable  
    detection\_methods JSONB, \-- Array of detection method details  
    actions\_taken JSONB, \-- Array of automated actions  
    assigned\_to UUID REFERENCES users(id), \-- Security analyst  
    forensic\_data\_id UUID, \-- Reference to S3/MongoDB  
    reported\_to\_authorities BOOLEAN DEFAULT false,  
    notes TEXT,  
    created\_at TIMESTAMP DEFAULT NOW(),  
    updated\_at TIMESTAMP DEFAULT NOW()  
);

CREATE INDEX idx\_incidents\_meeting ON incidents(meeting\_id);  
CREATE INDEX idx\_incidents\_company ON incidents(company\_id);  
CREATE INDEX idx\_incidents\_severity ON incidents(severity);  
CREATE INDEX idx\_incidents\_status ON incidents(status);  
CREATE INDEX idx\_incidents\_date ON incidents(detected\_at DESC);

\-- Verifications table  
CREATE TABLE verifications (  
    id UUID PRIMARY KEY DEFAULT gen\_random\_uuid(),  
    incident\_id UUID REFERENCES incidents(id),  
    meeting\_id UUID REFERENCES meetings(id),  
    user\_id UUID REFERENCES users(id), \-- User being verified  
    verification\_type VARCHAR(50) NOT NULL, \-- sms, voice\_call, push, email  
    channel\_data JSONB, \-- Phone number, email, etc.  
    status VARCHAR(50) NOT NULL, \-- sent, pending, verified, denied, timeout, failed  
    sent\_at TIMESTAMP NOT NULL,  
    responded\_at TIMESTAMP,  
    response\_value TEXT, \-- YES, NO, or verification code  
    response\_data JSONB, \-- Additional response metadata  
    timeout\_at TIMESTAMP,  
    attempts INTEGER DEFAULT 1,  
    created\_at TIMESTAMP DEFAULT NOW(),  
    updated\_at TIMESTAMP DEFAULT NOW()  
);

CREATE INDEX idx\_verifications\_incident ON verifications(incident\_id);  
CREATE INDEX idx\_verifications\_user ON verifications(user\_id);  
CREATE INDEX idx\_verifications\_status ON verifications(status);

\-- Risk Indicators table  
CREATE TABLE risk\_indicators (  
    id UUID PRIMARY KEY DEFAULT gen\_random\_uuid(),  
    meeting\_id UUID REFERENCES meetings(id),  
    participant\_id UUID REFERENCES participants(id),  
    indicator\_type VARCHAR(100) NOT NULL, \-- audio\_deepfake, video\_manipulation, social\_engineering, etc.  
    indicator\_category VARCHAR(50), \-- technical, behavioral, metadata  
    confidence\_score DECIMAL(5,2), \-- 0.00 to 100.00  
    detected\_at TIMESTAMP NOT NULL,  
    details JSONB, \-- Specific detection details  
    evidence\_url TEXT, \-- S3 URL for evidence  
    created\_at TIMESTAMP DEFAULT NOW()  
);

CREATE INDEX idx\_risk\_indicators\_meeting ON risk\_indicators(meeting\_id);  
CREATE INDEX idx\_risk\_indicators\_type ON risk\_indicators(indicator\_type);  
CREATE INDEX idx\_risk\_indicators\_confidence ON risk\_indicators(confidence\_score DESC);

\-- Policies table  
CREATE TABLE policies (  
    id UUID PRIMARY KEY DEFAULT gen\_random\_uuid(),  
    company\_id UUID REFERENCES companies(id),  
    name VARCHAR(255) NOT NULL,  
    description TEXT,  
    policy\_type VARCHAR(50), \-- verification, approval, blocking  
    is\_active BOOLEAN DEFAULT true,  
    conditions JSONB NOT NULL, \-- Rule conditions  
    actions JSONB NOT NULL, \-- Actions to take  
    priority INTEGER DEFAULT 0, \-- Higher \= evaluated first  
    created\_by UUID REFERENCES users(id),  
    created\_at TIMESTAMP DEFAULT NOW(),  
    updated\_at TIMESTAMP DEFAULT NOW()  
);

CREATE INDEX idx\_policies\_company ON policies(company\_id);  
CREATE INDEX idx\_policies\_active ON policies(is\_active) WHERE is\_active \= true;  
CREATE INDEX idx\_policies\_priority ON policies(priority DESC);

\-- Audit Log table  
CREATE TABLE audit\_logs (  
    id UUID PRIMARY KEY DEFAULT gen\_random\_uuid(),  
    company\_id UUID REFERENCES companies(id),  
    user\_id UUID REFERENCES users(id),  
    action VARCHAR(100) NOT NULL, \-- login, meeting\_joined, incident\_resolved, etc.  
    resource\_type VARCHAR(50), \-- meeting, incident, user, policy  
    resource\_id UUID,  
    ip\_address INET,  
    user\_agent TEXT,  
    details JSONB,  
    created\_at TIMESTAMP DEFAULT NOW()  
);

CREATE INDEX idx\_audit\_logs\_company ON audit\_logs(company\_id);  
CREATE INDEX idx\_audit\_logs\_user ON audit\_logs(user\_id);  
CREATE INDEX idx\_audit\_logs\_action ON audit\_logs(action);  
CREATE INDEX idx\_audit\_logs\_date ON audit\_logs(created\_at DESC);

### **3.2 MongoDB Documents**

// Transcripts collection  
{  
    \_id: ObjectId("..."),  
    meeting\_id: "uuid-from-postgres",  
    platform: "zoom",  
    created\_at: ISODate("2024-12-11T14:00:00Z"),  
    updated\_at: ISODate("2024-12-11T14:16:00Z"),  
      
    segments: \[  
        {  
            timestamp: ISODate("2024-12-11T14:02:15Z"),  
            speaker: {  
                participant\_id: "uuid",  
                name: "Sarah Chen",  
                role: "host"  
            },  
            text: "Hello, thanks for joining...",  
            confidence: 0.95,  
            language: "en-US",  
            risk\_analysis: {  
                keywords: \["joining", "meeting"\],  
                risk\_score: 5.0,  
                indicators: \[\]  
            }  
        },  
        {  
            timestamp: ISODate("2024-12-11T14:03:45Z"),  
            speaker: {  
                participant\_id: "uuid",  
                name: "Nupur Agarwal",  
                role: "participant"  
            },  
            text: "It's urgent for a project. The CEO authorized it...",  
            confidence: 0.92,  
            language: "en-US",  
            risk\_analysis: {  
                keywords: \["urgent", "CEO", "authorized"\],  
                risk\_score: 78.0,  
                indicators: \[  
                    {  
                        type: "social\_engineering",  
                        category: "authority\_bypass",  
                        confidence: 89.0,  
                        details: "Authority bypass pattern detected"  
                    },  
                    {  
                        type: "social\_engineering",  
                        category: "urgency\_tactic",  
                        confidence: 76.0,  
                        details: "Urgency language detected"  
                    }  
                \]  
            }  
        }  
    \],  
      
    summary: {  
        total\_segments: 45,  
        duration\_seconds: 960,  
        speakers: 2,  
        languages: \["en-US"\],  
        highest\_risk\_score: 78.0,  
        risk\_incidents: 1  
    },  
      
    indexed\_at: ISODate("2024-12-11T14:17:00Z")  
}

// Forensic Evidence collection  
{  
    \_id: ObjectId("..."),  
    incident\_id: "uuid-from-postgres",  
    meeting\_id: "uuid-from-postgres",  
    participant\_id: "uuid-from-postgres",  
    evidence\_type: "deepfake\_detection",  
    created\_at: ISODate("2024-12-11T14:06:00Z"),  
      
    audio\_analysis: {  
        provider: "resemble\_ai",  
        model\_version: "v3.2.1",  
        confidence: 67.0,  
        detection\_methods: \[  
            {  
                method: "spectral\_analysis",  
                result: "synthetic\_markers\_present",  
                confidence: 72.0  
            },  
            {  
                method: "prosody\_analysis",  
                result: "unnatural\_intonation",  
                confidence: 65.0  
            },  
            {  
                method: "audio\_video\_sync",  
                result: "42ms\_desynchronization",  
                confidence: 60.0  
            }  
        \],  
        audio\_clips: \[  
            {  
                timestamp: "00:03:45",  
                s3\_url: "s3://deepsafe-evidence/meetings/abc123/audio\_clip\_1.wav",  
                duration\_ms: 5000,  
                is\_synthetic: true,  
                confidence: 67.0  
            }  
        \],  
        spectrograms: \[  
            {  
                s3\_url: "s3://deepsafe-evidence/meetings/abc123/spectrogram\_1.png",  
                timestamp: "00:03:45"  
            }  
        \]  
    },  
      
    video\_analysis: {  
        provider: "sensity",  
        model\_version: "v2.1.0",  
        confidence: 92.0,  
        detection\_methods: \[  
            {  
                method: "facial\_landmark\_analysis",  
                result: "12\_inconsistencies\_detected",  
                confidence: 89.0  
            },  
            {  
                method: "micro\_expression\_analysis",  
                result: "unnatural\_blinking\_pattern",  
                confidence: 85.0  
            },  
            {  
                method: "lighting\_consistency",  
                result: "shadow\_anomalies",  
                confidence: 95.0,  
                instances: 3  
            }  
        \],  
        flagged\_frames: \[  
            {  
                frame\_number: 145,  
                timestamp: "00:02:25",  
                s3\_url: "s3://deepsafe-evidence/meetings/abc123/frame\_145.jpg",  
                anomaly\_type: "facial\_landmark",  
                confidence: 91.0  
            },  
            {  
                frame\_number: 892,  
                timestamp: "00:05:52",  
                s3\_url: "s3://deepsafe-evidence/meetings/abc123/frame\_892.jpg",  
                anomaly\_type: "lighting\_inconsistency",  
                confidence: 95.0  
            }  
        \]  
    },  
      
    network\_analysis: {  
        ip\_address: "185.220.XXX.XXX",  
        geolocation: {  
            country: "RO",  
            country\_name: "Romania",  
            city: "Bucharest",  
            latitude: 44.4268,  
            longitude: 26.1025  
        },  
        vpn\_detected: true,  
        vpn\_provider: "ProtonVPN",  
        device\_fingerprint: {  
            user\_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",  
            os: "Windows 11 Pro",  
            browser: "Chrome",  
            browser\_version: "120.0.6099.129",  
            screen\_resolution: "1920x1080",  
            timezone: "Europe/Bucharest",  
            plugins: \["OBS Virtual Camera"\],  
            canvas\_fingerprint: "abc123def456..."  
        },  
        email\_analysis: {  
            domain: "company.com",  
            domain\_verified: true,  
            spf\_check: "pass",  
            dkim\_check: "pass",  
            dmarc\_check: "pass",  
            device\_match: false,  
            usual\_devices: \["iPhone 14 Pro", "MacBook Pro"\],  
            current\_device: "Windows 11 Desktop"  
        }  
    },  
      
    behavioral\_analysis: {  
        social\_engineering\_score: 96.0,  
        patterns\_detected: \[  
            {  
                pattern: "authority\_bypass",  
                confidence: 89.0,  
                evidence: "Mentioned CEO authorization"  
            },  
            {  
                pattern: "urgency\_tactic",  
                confidence: 76.0,  
                evidence: "Used words: urgent, now"  
            },  
            {  
                pattern: "isolation",  
                confidence: 82.0,  
                evidence: "Don't loop in others"  
            },  
            {  
                pattern: "credential\_request",  
                confidence: 95.0,  
                evidence: "Direct request for admin credentials"  
            }  
        \],  
        conversation\_similarity: {  
            known\_attack\_type: "BEC\_credential\_theft",  
            similarity\_score: 96.0,  
            matching\_scenarios: \[  
                "CEO\_fraud\_pattern\_12",  
                "credential\_phishing\_pattern\_7"  
            \]  
        }  
    },  
      
    raw\_data\_urls: {  
        full\_video\_recording: "s3://deepsafe-recordings/meetings/abc123/full\_recording.mp4",  
        full\_audio\_recording: "s3://deepsafe-recordings/meetings/abc123/full\_audio.wav",  
        packet\_capture: "s3://deepsafe-forensics/meetings/abc123/network\_capture.pcap"  
    }  
}

### **3.3 Redis Data Structures**

\# Active meeting state  
meeting:active:{meeting\_id}  
{  
    "meeting\_id": "uuid",  
    "platform": "zoom",  
    "external\_id": "123-456-789",  
    "host\_user\_id": "uuid",  
    "started\_at": "2024-12-11T14:00:00Z",  
    "participants": \[  
        {  
            "participant\_id": "uuid",  
            "user\_id": "uuid",  
            "name": "Sarah Chen",  
            "joined\_at": "2024-12-11T14:00:00Z",  
            "trust\_score": 95.0,  
            "is\_flagged": false  
        }  
    \],  
    "current\_risk\_score": 35.0,  
    "risk\_trending": "increasing",  
    "active\_alerts": \[\]  
}  
TTL: 86400 (24 hours)

\# User session  
session:{session\_id}  
{  
    "user\_id": "uuid",  
    "email": "user@company.com",  
    "company\_id": "uuid",  
    "role": "admin",  
    "created\_at": "2024-12-11T10:00:00Z",  
    "last\_activity": "2024-12-11T14:30:00Z",  
    "ip\_address": "192.168.1.100"  
}  
TTL: 3600 (1 hour, sliding)

\# Rate limiting  
ratelimit:api:{user\_id}:{endpoint}  
Count: 45  
TTL: 3600 (1 hour)

\# Real-time risk scores (sorted set)  
risk:meeting:{meeting\_id}:timeline  
Score (timestamp) \-\> Risk score value

\# Cache for expensive queries  
cache:meetings:company:{company\_id}:recent  
TTL: 300 (5 minutes)

\# WebSocket connections  
ws:connections:{meeting\_id}  
Set of connection IDs

\# Verification pending  
verification:pending:{verification\_id}  
{  
    "incident\_id": "uuid",  
    "user\_id": "uuid",  
    "type": "sms",  
    "sent\_at": "2024-12-11T14:05:00Z",  
    "timeout\_at": "2024-12-11T14:10:00Z"  
}  
TTL: 300 (5 minutes)

---

## **4\. API Specifications**

### **4.1 RESTful API Endpoints**

Base URL: https://api.deepsafe.ai/v1

Authentication:   
  \- Bearer JWT token in Authorization header  
  \- API key for service-to-service

Rate Limiting:  
  \- Authenticated: 1000 req/hour per user  
  \- Unauthenticated: 100 req/hour per IP

#### **Meeting Endpoints**

\# Get meetings list  
GET /api/v1/meetings  
Query Parameters:  
  \- company\_id: UUID (required for non-admin)  
  \- start\_date: ISO8601 datetime  
  \- end\_date: ISO8601 datetime  
  \- risk\_category: low|medium|high|critical  
  \- is\_compromised: boolean  
  \- page: integer (default: 1\)  
  \- page\_size: integer (default: 20, max: 100\)  
  \- sort\_by: started\_at|risk\_score|duration (default: started\_at)  
  \- sort\_order: asc|desc (default: desc)

Response 200:  
{  
    "data": \[  
        {  
            "id": "uuid",  
            "external\_meeting\_id": "123-456-789",  
            "platform": "zoom",  
            "meeting\_name": "Q4 Budget Review",  
            "host": {  
                "id": "uuid",  
                "name": "Sarah Chen",  
                "email": "sarah@company.com"  
            },  
            "started\_at": "2024-12-11T14:00:00Z",  
            "ended\_at": "2024-12-11T14:16:00Z",  
            "duration\_minutes": 16,  
            "participant\_count": 2,  
            "risk\_score": 78.0,  
            "risk\_category": "high",  
            "is\_compromised": true,  
            "status": "completed"  
        }  
    \],  
    "pagination": {  
        "page": 1,  
        "page\_size": 20,  
        "total\_items": 126,  
        "total\_pages": 7  
    }  
}

\# Get specific meeting  
GET /api/v1/meetings/{meeting\_id}

Response 200:  
{  
    "id": "uuid",  
    "external\_meeting\_id": "34190412",  
    "platform": "zoom",  
    "meeting\_name": "CSO \<\> Employee",  
    "host": {  
        "id": "uuid",  
        "name": "Chief Security Officer",  
        "email": "cso@company.com",  
        "department": "Security"  
    },  
    "started\_at": "2024-04-09T14:00:00Z",  
    "ended\_at": "2024-04-09T14:16:00Z",  
    "duration\_minutes": 16,  
    "risk\_score": 87.0,  
    "risk\_category": "high",  
    "is\_compromised": true,  
    "status": "completed",  
    "participants": \[  
        {  
            "id": "uuid",  
            "user\_id": "uuid",  
            "name": "CSO",  
            "email": "cso@company.com",  
            "role": "host",  
            "trust\_score": 98.0,  
            "is\_flagged": false,  
            "joined\_at": "2024-04-09T14:00:00Z",  
            "left\_at": "2024-04-09T14:16:00Z",  
            "duration\_minutes": 16  
        },  
        {  
            "id": "uuid",  
            "name": "Nupur Agarwal",  
            "email": "nupur.agarwal@external.com",  
            "role": "participant",  
            "trust\_score": 13.0,  
            "audio\_risk": 67.0,  
            "video\_risk": 92.0,  
            "credential\_risk": 14.0,  
            "is\_flagged": true,  
            "flag\_reason": "Deepfake detected, verification failed",  
            "verification\_status": "failed",  
            "joined\_at": "2024-04-09T14:00:00Z",  
            "left\_at": "2024-04-09T14:08:00Z",  
            "duration\_minutes": 8  
        }  
    \],  
    "incidents": \[  
        {  
            "id": "uuid",  
            "incident\_code": "INC-20240409-001",  
            "type": "deepfake\_impersonation",  
            "severity": "high",  
            "status": "resolved",  
            "detected\_at": "2024-04-09T14:06:00Z",  
            "resolved\_at": "2024-04-09T14:08:00Z"  
        }  
    \],  
    "transcript\_available": true,  
    "recording\_url": "s3://...",  
    "metadata": {  
        "room\_participants\_max": 2,  
        "screen\_share\_used": false  
    }  
}

\# Get meeting transcript  
GET /api/v1/meetings/{meeting\_id}/transcript

Response 200:  
{  
    "meeting\_id": "uuid",  
    "segments": \[  
        {  
            "timestamp": "2024-04-09T14:02:15Z",  
            "speaker": {  
                "name": "CSO",  
                "participant\_id": "uuid"  
            },  
            "text": "Hello, thanks for joining...",  
            "confidence": 0.95,  
            "risk\_score": 5.0,  
            "risk\_indicators": \[\]  
        },  
        {  
            "timestamp": "2024-04-09T14:03:45Z",  
            "speaker": {  
                "name": "Nupur Agarwal",  
                "participant\_id": "uuid"  
            },  
            "text": "It's urgent for a project. The CEO authorized it...",  
            "confidence": 0.92,  
            "risk\_score": 78.0,  
            "risk\_indicators": \[  
                {  
                    "type": "social\_engineering",  
                    "category": "authority\_bypass",  
                    "confidence": 89.0  
                },  
                {  
                    "type": "social\_engineering",  
                    "category": "urgency\_tactic",  
                    "confidence": 76.0  
                }  
            \]  
        }  
    \],  
    "summary": {  
        "total\_segments": 45,  
        "duration\_seconds": 960,  
        "speakers": 2  
    }  
}

\# Get meeting forensics  
GET /api/v1/meetings/{meeting\_id}/forensics

Response 200:  
{  
    "meeting\_id": "uuid",  
    "incident\_id": "uuid",  
    "audio\_analysis": {  
        "confidence": 67.0,  
        "detection\_methods": \[...\],  
        "evidence\_urls": \[...\]  
    },  
    "video\_analysis": {  
        "confidence": 92.0,  
        "detection\_methods": \[...\],  
        "flagged\_frames": \[...\]  
    },  
    "network\_analysis": {...},  
    "behavioral\_analysis": {...}  
}

#### **Incident Endpoints**

\# Get incidents  
GET /api/v1/incidents  
Query Parameters:  
  \- company\_id: UUID  
  \- severity: low|medium|high|critical  
  \- status: active|resolved|investigating|false\_positive  
  \- incident\_type: deepfake\_audio|deepfake\_video|social\_engineering|bec  
  \- start\_date: ISO8601  
  \- end\_date: ISO8601  
  \- page: integer  
  \- page\_size: integer

Response 200:  
{  
    "data": \[  
        {  
            "id": "uuid",  
            "incident\_code": "INC-20241211-002",  
            "meeting\_id": "uuid",  
            "meeting\_name": "M\&A Discussion",  
            "participant": {  
                "id": "uuid",  
                "name": "Nupur Agarwal",  
                "email": "nupur@external.com"  
            },  
            "incident\_type": "deepfake\_impersonation",  
            "severity": "critical",  
            "risk\_score": 94.0,  
            "status": "resolved",  
            "detected\_at": "2024-12-11T14:06:00Z",  
            "resolved\_at": "2024-12-11T14:08:00Z",  
            "resolution": "prevented",  
            "amount\_protected": 250000.00  
        }  
    \],  
    "pagination": {...}  
}

\# Get specific incident  
GET /api/v1/incidents/{incident\_id}

\# Update incident status  
PATCH /api/v1/incidents/{incident\_id}  
Request Body:  
{  
    "status": "resolved",  
    "resolution": "prevented",  
    "notes": "Verification successful, attacker removed"  
}

\# Export incident report  
GET /api/v1/incidents/{incident\_id}/export  
Query Parameters:  
  \- format: pdf|xlsx|json  
  \- include\_forensics: boolean  
  \- include\_recording: boolean

Response 200:  
Binary file download OR  
{  
    "download\_url": "https://s3.../report.pdf",  
    "expires\_at": "2024-12-11T16:00:00Z"  
}

#### **Participant Endpoints**

\# Get participants  
GET /api/v1/participants  
Query Parameters:  
  \- company\_id: UUID  
  \- is\_flagged: boolean  
  \- is\_blacklisted: boolean  
  \- min\_risk\_score: float  
  \- search: string (name or email)  
  \- page: integer  
  \- page\_size: integer

\# Get participant profile  
GET /api/v1/participants/{participant\_id}

Response 200:  
{  
    "id": "uuid",  
    "user\_id": "uuid",  
    "email": "nupur@external.com",  
    "name": "Nupur Agarwal",  
    "is\_blacklisted": true,  
    "blacklist\_reason": "Multiple fraud attempts",  
    "overall\_risk\_score": 87.0,  
    "total\_meetings": 2,  
    "total\_incidents": 2,  
    "first\_seen": "2024-04-08T10:00:00Z",  
    "last\_seen": "2024-04-09T14:08:00Z",  
    "meetings": \[...\],  
    "incidents": \[...\]  
}

\# Update participant (blacklist/whitelist)  
PATCH /api/v1/participants/{participant\_id}  
Request Body:  
{  
    "is\_blacklisted": true,  
    "blacklist\_reason": "Confirmed fraud attempt"  
}

#### **Real-Time WebSocket API**

// WebSocket connection  
ws://api.deepsafe.ai/v1/ws/meetings/{meeting\_id}  
Headers:  
  \- Authorization: Bearer {jwt\_token}

// Client → Server: Subscribe to meeting  
{  
    "action": "subscribe",  
    "meeting\_id": "uuid"  
}

// Server → Client: Meeting state update  
{  
    "event": "meeting\_state\_update",  
    "data": {  
        "meeting\_id": "uuid",  
        "risk\_score": 45.0,  
        "risk\_trending": "increasing",  
        "participants": \[...\]  
    },  
    "timestamp": "2024-12-11T14:05:00Z"  
}

// Server → Client: Risk alert  
{  
    "event": "risk\_alert",  
    "data": {  
        "meeting\_id": "uuid",  
        "participant\_id": "uuid",  
        "risk\_score": 78.0,  
        "risk\_category": "high",  
        "indicators": \[  
            {  
                "type": "social\_engineering",  
                "confidence": 85.0,  
                "details": "Financial transaction mentioned"  
            }  
        \]  
    },  
    "timestamp": "2024-12-11T14:05:30Z"  
}

// Server → Client: Verification triggered  
{  
    "event": "verification\_triggered",  
    "data": {  
        "verification\_id": "uuid",  
        "type": "sms",  
        "user\_id": "uuid",  
        "user\_name": "Mike Williams (CFO)",  
        "status": "pending",  
        "timeout\_at": "2024-12-11T14:10:00Z"  
    },  
    "timestamp": "2024-12-11T14:05:45Z"  
}

// Server → Client: Verification result  
{  
    "event": "verification\_complete",  
    "data": {  
        "verification\_id": "uuid",  
        "status": "denied",  
        "response": "NO",  
        "user\_confirmed\_fraud": true  
    },  
    "timestamp": "2024-12-11T14:06:30Z"  
}

// Server → Client: Incident created  
{  
    "event": "incident\_created",  
    "data": {  
        "incident\_id": "uuid",  
        "incident\_code": "INC-20241211-001",  
        "severity": "critical",  
        "type": "deepfake\_impersonation",  
        "participant\_id": "uuid",  
        "participant\_name": "Nupur Agarwal"  
    },  
    "timestamp": "2024-12-11T14:06:35Z"  
}

---

## **5\. Performance Requirements**

### **5.1 Latency Requirements**

Real-Time Processing:  
  Audio/Video Stream Capture: \< 100ms lag  
  Deepfake Detection: \< 3 seconds from capture  
  Risk Score Calculation: \< 2 seconds  
  Alert Generation: \< 5 seconds total (capture → alert)  
    
API Response Times:  
  GET endpoints: \< 200ms (p95)  
  POST endpoints: \< 500ms (p95)  
  Search queries: \< 1 second (p95)  
  Report generation: \< 10 seconds (p95)  
    
Verification:  
  SMS delivery: \< 10 seconds  
  Voice call initiation: \< 15 seconds  
  Push notification: \< 5 seconds

### **5.2 Throughput Requirements**

Concurrent Meetings:  
  Starter tier: 100 concurrent meetings  
  Professional tier: 1,000 concurrent meetings  
  Enterprise tier: 10,000+ concurrent meetings  
    
API Requests:  
  Total: 10,000 requests/second  
  Per user: 100 requests/minute  
  Per meeting: 50 requests/minute  
    
Data Processing:  
  Audio transcription: 1,000 hours/hour  
  Video analysis: 500 hours/hour  
  NLP analysis: 10,000 segments/second

### **5.3 Availability & Reliability**

Uptime SLA:  
  System availability: 99.9% (8.76 hours downtime/year)  
  Detection service: 99.95%  
  API availability: 99.9%  
    
Disaster Recovery:  
  RPO (Recovery Point Objective): 15 minutes  
  RTO (Recovery Time Objective): 1 hour  
    
Data Durability:  
  Database: 99.999999999% (11 nines) \- AWS RDS  
  Object storage: 99.999999999% \- S3  
    
Backup Strategy:  
  Database: Continuous backup \+ daily snapshots (30 day retention)  
  Files: Versioned storage with 90 day retention  
  Point-in-time recovery: 35 days

---

## **6\. Security Requirements**

### **6.1 Authentication & Authorization**

Authentication:  
  \- JWT tokens (RS256 algorithm)  
  \- Token expiry: 1 hour (access), 7 days (refresh)  
  \- SSO integration: SAML 2.0, OAuth 2.0, OpenID Connect  
  \- MFA required for admin users  
  \- API keys for service-to-service (rotated every 90 days)  
    
Authorization:  
  \- Role-Based Access Control (RBAC)  
  \- Roles: super\_admin, company\_admin, security\_analyst, user  
  \- Resource-level permissions  
  \- Least privilege principle  
    
Password Requirements:  
  \- Minimum 12 characters  
  \- Complexity: uppercase, lowercase, number, symbol  
  \- No password reuse (last 10 passwords)  
  \- Password expiry: 90 days for admins  
  \- Account lockout: 5 failed attempts

### **6.2 Data Security**

Encryption:  
  At Rest:  
    \- Database: AES-256 encryption  
    \- Object storage: AES-256 encryption  
    \- File system: LUKS encryption  
    
  In Transit:  
    \- TLS 1.3 only (minimum 1.2)  
    \- Certificate pinning for mobile apps  
    \- Perfect Forward Secrecy (PFS)  
    
  Application Level:  
    \- PII fields encrypted in database  
    \- Encryption keys in AWS KMS / HashiCorp Vault  
    \- Key rotation: every 90 days  
    
Data Classification:  
  \- Public: Meeting IDs, timestamps  
  \- Internal: Risk scores, analytics  
  \- Confidential: Transcripts, participant info  
  \- Restricted: Forensic evidence, recordings  
    
Data Retention:  
  \- Active meetings: Real-time \+ 90 days  
  \- Resolved incidents: 7 years (compliance)  
  \- Recordings: 90 days (configurable)  
  \- Audit logs: 7 years  
  \- Deleted data: Permanent deletion after 30 days

### **6.3 Compliance**

Regulatory Compliance:  
  \- GDPR (EU General Data Protection Regulation)  
  \- CCPA (California Consumer Privacy Act)  
  \- SOC 2 Type II  
  \- ISO 27001  
  \- HIPAA (for healthcare customers)  
    
Data Privacy:  
  \- Data Processing Agreements (DPA)  
  \- Privacy by design  
  \- Right to deletion  
  \- Data portability  
  \- Consent management  
    
Security Standards:  
  \- OWASP Top 10 mitigation  
  \- CIS Benchmarks  
  \- NIST Cybersecurity Framework  
    
Audit & Logging:  
  \- All access logged  
  \- Immutable audit trail  
  \- Security event monitoring  
  \- Regular security audits  
  \- Penetration testing: Quarterly

---

## **7\. Scalability & Infrastructure**

### **7.1 Auto-Scaling Configuration**

Application Servers:  
  Min instances: 3  
  Max instances: 100  
  Target CPU: 70%  
  Target memory: 80%  
  Scale up: \+2 instances when CPU \> 80% for 2 minutes  
  Scale down: \-1 instance when CPU \< 50% for 5 minutes  
    
Detection Workers:  
  Min instances: 5  
  Max instances: 50  
  Scale based on queue depth  
  Target: \< 100 messages in queue  
    
Database:  
  Read replicas: 3-10 (auto-scale based on load)  
  Connection pool: 20-200 connections per instance  
  Vertical scaling: Automated up to 64 vCPU, 256GB RAM  
    
Cache:  
  Redis cluster: 3-15 nodes  
  Memory per node: 8GB-64GB  
  Eviction policy: LRU (Least Recently Used)

### **7.2 Infrastructure as Code**

\# Example Terraform configuration structure  
modules/  
  ├── networking/  
  │   ├── vpc.tf  
  │   ├── subnets.tf  
  │   └── security\_groups.tf  
  ├── compute/  
  │   ├── eks\_cluster.tf  
  │   ├── node\_groups.tf  
  │   └── autoscaling.tf  
  ├── database/  
  │   ├── rds.tf  
  │   ├── redis.tf  
  │   └── mongodb.tf  
  ├── storage/  
  │   ├── s3\_buckets.tf  
  │   └── lifecycle\_policies.tf  
  └── monitoring/  
      ├── cloudwatch.tf  
      ├── prometheus.tf  
      └── grafana.tf

---

## **8\. Monitoring & Observability**

### **8.1 Metrics**

Application Metrics:  
  \- Request rate (req/s)  
  \- Response time (p50, p95, p99)  
  \- Error rate (%)  
  \- Active meetings count  
  \- Detection accuracy rate  
  \- Verification success rate  
    
Infrastructure Metrics:  
  \- CPU utilization (%)  
  \- Memory utilization (%)  
  \- Network I/O (MB/s)  
  \- Disk I/O (IOPS)  
  \- Queue depth  
    
Business Metrics:  
  \- Meetings monitored per day  
  \- Incidents detected per day  
  \- Money protected (cumulative)  
  \- False positive rate (%)  
  \- Average response time to incidents

### **8.2 Logging**

Log Levels:  
  \- DEBUG: Development only  
  \- INFO: Normal operations  
  \- WARN: Degraded performance  
  \- ERROR: Recoverable errors  
  \- CRITICAL: System failures  
    
Log Format: JSON structured logs  
{  
    "timestamp": "2024-12-11T14:05:30Z",  
    "level": "INFO",  
    "service": "detection-service",  
    "trace\_id": "abc123",  
    "span\_id": "def456",  
    "user\_id": "uuid",  
    "message": "Deepfake detected",  
    "metadata": {  
        "meeting\_id": "uuid",  
        "confidence": 92.0  
    }  
}

Log Aggregation:  
  \- Centralized: Elasticsearch  
  \- Retention: 90 days hot, 365 days cold  
  \- Search: Kibana dashboards

### **8.3 Alerting**

Alert Channels:  
  \- PagerDuty (critical incidents)  
  \- Slack (team notifications)  
  \- Email (reports)  
    
Alert Rules:  
  Critical (Page immediately):  
    \- Service down \> 1 minute  
    \- Error rate \> 5% for 5 minutes  
    \- Database connection failure  
    \- Detection service failure  
    
  High (Page during business hours):  
    \- Response time p95 \> 2 seconds for 10 minutes  
    \- CPU \> 90% for 5 minutes  
    \- Memory \> 95% for 5 minutes  
    \- Queue depth \> 1000 messages  
    
  Medium (Slack notification):  
    \- Error rate \> 1% for 15 minutes  
    \- Response time p95 \> 1 second for 15 minutes  
    \- Disk usage \> 80%  
    
  Low (Email daily digest):  
    \- Response time trending up  
    \- Slow queries detected  
    \- SSL certificate expiring in 30 days

---

This completes Part 1: Application Technical Requirements.

**Continue to Part 2: Dashboard Technical Requirements?**

