# DeepSafe Interactive Demo Application
## Product Requirements Document (PRD)

**Version:** 1.0
**Date:** December 2024
**Author:** DeepSafe Product Team
**Status:** Draft

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Product Overview](#2-product-overview)
3. [User Requirements & Goals](#3-user-requirements--goals)
4. [Demo Scenario](#4-demo-scenario)
5. [Demo Flow & Steps](#5-demo-flow--steps)
6. [UI/UX Design Specifications](#6-uiux-design-specifications)
7. [Technical Specifications](#7-technical-specifications)
8. [Interactive Features](#8-interactive-features)
9. [Component Architecture](#9-component-architecture)
10. [Data Models](#10-data-models)
11. [Branding & Style Guide](#11-branding--style-guide)
12. [Accessibility Requirements](#12-accessibility-requirements)
13. [Deployment Strategy](#13-deployment-strategy)
14. [Success Metrics](#14-success-metrics)
15. [Appendix](#15-appendix)

---

## 1. Executive Summary

### 1.1 Purpose

The DeepSafe Interactive Demo is an immersive, educational web application that showcases DeepSafe's AI-powered meeting protection system in action. Users experience a realistic simulation of a deepfake attack being detected and prevented in real-time, demonstrating the full value proposition of the DeepSafe platform.

### 1.2 Target Audience

| Audience | Goals | Key Interests |
|----------|-------|---------------|
| **Enterprise Security Teams** | Evaluate DeepSafe for deployment | Technical accuracy, detection capabilities |
| **C-Suite Executives** | Understand ROI and risk mitigation | Financial protection, ease of use |
| **Investors & Partners** | Assess technology and market fit | Innovation, scalability, differentiation |
| **Sales & Marketing** | Demonstrate product capabilities | Visual impact, storytelling |

### 1.3 Key Value Propositions Demonstrated

1. **Real-time Deepfake Detection** - AI identifies synthetic video/audio within seconds
2. **Social Engineering Pattern Recognition** - Behavioral analysis catches manipulation tactics
3. **Automated Threat Response** - Immediate intervention without human delay
4. **Forensic Evidence Preservation** - Complete audit trail for investigation
5. **Financial Protection** - Quantified savings from prevented attacks

### 1.4 Success Criteria

- Users complete the demo in under 5 minutes
- 90%+ of users click at least 3 educational hotspots
- Demo effectively communicates all 5 value propositions
- Zero confusion about what DeepSafe does after viewing

---

## 2. Product Overview

### 2.1 What This Demo Is

An **interactive roleplay experience** that simulates joining a Google Meet-style video call where a deepfake attacker attempts to impersonate a CEO to authorize a fraudulent wire transfer. Users watch as DeepSafe detects anomalies, escalates risk scores, triggers verification, and ultimately removes the threat—all in real-time with educational explanations.

### 2.2 What This Demo Is NOT

- Not a functional video conferencing tool
- Not connected to real AI/ML detection systems
- Not a training simulation (educational, not operational)
- Not a game or gamified experience

### 2.3 Core Experience Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DEMO EXPERIENCE                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  [1. INTRO]     [2. JOIN]      [3. CALL]       [4. DETECT]          │
│  Welcome &  →   Meeting    →   Normal      →   First                │
│  Context        Lobby          Conversation    Anomaly              │
│                                                                      │
│  [5. ESCALATE]  [6. VERIFY]   [7. REMOVE]    [8. REPORT]           │
│  Risk Score  →  Identity   →   Threat      →   Incident             │
│  Rising         Challenge      Neutralized     Summary              │
│                                                                      │
│  [9. SUCCESS]                                                        │
│  $250K Protected                                                     │
│  Demo Complete                                                       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. User Requirements & Goals

### 3.1 Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | Demo must mimic Google Meet interface accurately | P0 |
| FR-02 | Step-by-step navigation with forward/back controls | P0 |
| FR-03 | Auto-play mode with configurable timing | P1 |
| FR-04 | Clickable hotspots on all DeepSafe UI elements | P0 |
| FR-05 | Modal popups explaining technical details | P0 |
| FR-06 | Real-time risk score animation | P0 |
| FR-07 | Transcript panel with risk highlighting | P0 |
| FR-08 | Forensic evidence breakdown views | P1 |
| FR-09 | Responsive design (desktop primary, tablet secondary) | P1 |
| FR-10 | Keyboard navigation support | P2 |

### 3.2 Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-01 | Initial load time | < 3 seconds |
| NFR-02 | Step transition smoothness | 60fps animations |
| NFR-03 | Browser support | Chrome, Safari, Firefox, Edge (latest 2 versions) |
| NFR-04 | Mobile support | Responsive but not primary target |
| NFR-05 | Accessibility | WCAG 2.1 AA compliance |

### 3.3 Architecture Decision

**Dual Deployment Strategy:**

1. **Integrated Route** (`/demo`) - Primary deployment within existing deepsafe-app
   - Shares theme, components, and build pipeline
   - Consistent navigation with main application
   - Single codebase maintenance

2. **Standalone Build** - Separate deployable bundle
   - Can be hosted on dedicated demo subdomain (demo.deepsafe.ai)
   - Embeddable in marketing sites
   - Independent versioning for sales demos

---

## 4. Demo Scenario

### 4.1 Scenario Overview

**Title:** "The CEO Wire Transfer Attack"

**Setting:** A Fortune 500 company's finance department

**Attack Type:** Deepfake video + social engineering + BEC (Business Email Compromise)

**Target Amount:** $250,000 emergency wire transfer

**Outcome:** Attack prevented by DeepSafe

### 4.2 Characters

#### Sarah Chen - CFO (Victim Target)
- **Role:** Chief Financial Officer
- **Email:** sarah.chen@company.com
- **Trust Score:** 98 (Verified employee)
- **Status:** Legitimate participant
- **Avatar:** Professional woman, business attire
- **Device:** MacBook Pro, Known device fingerprint

#### "David Mitchell" - Attacker (Impersonating CEO)
- **Claimed Identity:** CEO David Mitchell
- **Actual Identity:** Morgan Reed (Threat actor)
- **Email:** d.mitchell@company.com (spoofed)
- **Trust Score:** Starts 85, drops to 13
- **Status:** Deepfake impersonator
- **Avatar:** AI-generated video of CEO
- **Device:** Windows 11, VPN (NordVPN), OBS Virtual Camera

#### DeepSafe Bot - Protection System
- **Role:** Automated meeting guardian
- **Status:** Always present, always watching
- **Visual:** Teal shield icon in participant list

### 4.3 Attack Script

The attacker uses the following social engineering playbook:

1. **Authority Establishment** - Claims to be CEO, mentions board meeting
2. **Urgency Creation** - "Before markets open", "Time-sensitive acquisition"
3. **Isolation Tactics** - "Keep this confidential", "Don't loop in legal yet"
4. **Process Bypass** - "Skip the usual approval workflow"
5. **Credential/Action Request** - "Authorize the wire transfer now"

### 4.4 Conversation Script

> **Based on:** Real-world cases including the $25M Arup deepfake attack (2024) and Ferrari CEO impersonation attempt.

```
TIME     SPEAKER           DIALOGUE                                         RISK
─────────────────────────────────────────────────────────────────────────────────

── PHASE 1: BUILDING TRUST ──

00:00    [System]          Meeting started. DeepSafe protection active.       0%

00:08    "David Mitchell"  Sarah, thanks for joining. Quick question—          5%
                           how are the Q4 numbers looking?

00:18    Sarah Chen        We're tracking 3% above forecast. Strong            3%
                           APAC performance.

00:28    "David Mitchell"  Perfect. That's actually related to why I           8%
                           called. We have a time-sensitive acquisition
                           opportunity in APAC. The board approved it
                           in an emergency session last night.

── PHASE 2: THE REQUEST ──

00:52    Sarah Chen        I didn't see anything on the board portal.          6%

01:02    "David Mitchell"  It was informal—you know how they are.             18%
                           We'll document it after. Right now, I need
                           you to wire a $250,000 good-faith deposit
                           to secure exclusivity.
                           [⚠️ FLAGGED: Process irregularity]

01:28    Sarah Chen        That should go through standard approval.           8%
                           I can have it done by end of week.

01:38    "David Mitchell"  We don't have until end of week. The seller        45%
                           needs it by 5 PM today or we lose the deal.
                           [⚠️ FLAGGED: Urgency tactic (68%)]

── PHASE 3: PRESSURE ──

01:58    Sarah Chen        A same-day wire for $250K is outside our           12%
                           normal controls. I'd need to loop in legal.

02:12    "David Mitchell"  Remember the Nexus deal we lost? Same thing—       62%
                           we moved too slow. I don't want to make that
                           mistake again. The board feels the same way.
                           [⚠️ FLAGGED: Authority bypass (72%)]

02:35    Sarah Chen        Can I at least verify with someone from            18%
                           the board directly?

02:45    "David Mitchell"  They've authorized me to handle it. Richard        72%
                           specifically said not to bother him with
                           the details. I need you to initiate the wire
                           now—I'll send you the account number.
                           [🔴 FLAGGED: Isolation (71%), Process bypass]

── PHASE 4: ESCALATION ──

03:08    [DeepSafe]        ⚠️ ALERT: Risk Level ELEVATED (72%)                 -
                           Enhanced monitoring active

03:15    "David Mitchell"  Look, if you can't help me, I'll have to go        78%
                           around you. That's not how I wanted to handle
                           this, but the clock is ticking.
                           [🔴 FLAGGED: Implicit threat, Authority bypass]

03:32    Sarah Chen        I'm not trying to obstruct. I just want to         22%
                           make sure we're protected.

03:42    "David Mitchell"  I'll take full responsibility. Keep this           92%
                           between us until the deal closes—I don't
                           want word getting out.
                           [🔴 FLAGGED: Liability transfer (91%),
                            Isolation/secrecy (86%), SE pattern: 94%]

── PHASE 5: DETECTION & REMOVAL ──

03:58    [DeepSafe]        🚨 THREAT CONFIRMED                                  -
                           ├─ Deepfake Confidence: 92%
                           ├─ Voice Cloning: 67%
                           ├─ Social Engineering: 94%
                           └─ Network: VPN + Virtual Camera
                           Verification sent to real David Mitchell...

04:08    [Real CEO]        [SMS Response] "I'm at the airport.                 -
                           I am NOT in any meeting. This is fraud."

04:12    [DeepSafe]        Identity mismatch confirmed.                        -
                           Removing threat actor...

04:15    [System]          'David Mitchell' removed due to security            -
                           concerns.

04:18    [DeepSafe]        ✅ INCIDENT RESOLVED                                 -
                           ├─ Threat Actor: Removed
                           ├─ IT Security: Notified
                           ├─ Forensic Data: Preserved
                           └─ Amount Protected: $250,000
```

### 4.5 Attack Tactics & Detection

| Phase | Tactic | Example | Risk Trigger |
|-------|--------|---------|--------------|
| 1 | **Legitimacy** | Small talk about Q4 numbers | None (normal) |
| 2 | **Authority** | "Board approved it", "They trust me" | 18% |
| 2 | **Urgency** | "By 5 PM today or we lose the deal" | 45% |
| 3 | **Bypass** | "Go around you", "Document it after" | 72% |
| 4 | **Isolation** | "Keep this between us" | 92% |
| 4 | **Liability** | "I'll take full responsibility" | 92% |

---

## 5. Demo Flow & Steps

### Step 1: Welcome & Introduction
**Duration:** 5-10 seconds (skippable)

**Screen Content:**
- DeepSafe logo with gradient animation
- Headline: "Experience DeepSafe in Action"
- Subtext: "Watch how AI protects your meetings from deepfake attacks"
- CTA Button: "Start Demo" (primary teal)

**Hotspots:** None (intro screen)

---

### Step 2: Meeting Lobby
**Duration:** 8-12 seconds

**Screen Content:**
- Google Meet-style lobby interface
- Meeting title: "Urgent: Acquisition Discussion"
- Scheduled by: "David Mitchell (CEO)"
- Your name: "Sarah Chen"
- Camera preview (static image)
- "Join now" button

**DeepSafe Elements:**
- Small badge: "🛡️ DeepSafe Protected Meeting"

**Hotspots:**
1. **DeepSafe Badge** → Modal: "Every meeting with DeepSafe enabled is automatically monitored for deepfakes, voice cloning, and social engineering attempts."

---

### Step 3: Meeting Joined - Normal State
**Duration:** 15-20 seconds

**Screen Content:**
- Full Google Meet interface
- Two participant tiles:
  - "David Mitchell" (CEO) - large tile, speaking indicator
  - "You" (Sarah Chen) - smaller tile
- DeepSafe bot in participant list
- Bottom control bar (mute, video, etc.)
- Transcript panel (collapsible on right)

**DeepSafe Elements:**
- Risk meter in corner: GREEN (12%)
- "All Clear" status indicator
- Participant trust badges

**Conversation:**
- Opening pleasantries (risk: 3-12)

**Hotspots:**
1. **Risk Meter** → Modal: "The risk meter shows real-time threat assessment across audio, video, behavioral, and network signals."
2. **Trust Badge on David** → Modal: "Trust scores are calculated based on device fingerprint, login history, behavioral patterns, and video/audio authenticity."
3. **DeepSafe Bot** → Modal: "The DeepSafe bot joins every protected meeting automatically. It analyzes all participants in real-time without recording or storing video."

---

### Step 4: First Suspicious Message
**Duration:** 12-15 seconds

**Screen Content:**
- Same interface, conversation continues
- First flagged message appears in transcript
- Risk meter begins rising (12% → 45%)

**Conversation:**
- "I need you to authorize a wire transfer of $250,000"

**DeepSafe Elements:**
- Risk meter: YELLOW-ORANGE (45%)
- Transcript highlight: Yellow background on flagged message
- Risk indicator chip: "Credential Request Detected"

**Hotspots:**
1. **Flagged Message** → Modal: Risk Analysis breakdown
   - Credential Request: HIGH
   - Financial Transaction: HIGH
   - Urgency Pattern: MEDIUM
2. **Risk Meter Animation** → Modal: "Risk scores update in real-time as new signals are detected. Multiple risk factors compound the overall score."

---

### Step 5: Risk Escalation
**Duration:** 15-20 seconds

**Screen Content:**
- Video tile of "David Mitchell" shows subtle detection overlay
- Transcript shows severely flagged message
- Risk meter spikes dramatically (45% → 78%)

**Conversation:**
- "The usual process is too slow... I've already cleared this with the board"

**DeepSafe Elements:**
- Risk meter: ORANGE-RED (78%)
- Video tile overlay: Pulsing border with detection indicators
- Alert banner: "⚠️ High Risk Detected - Analyzing..."
- Transcript: Red highlight with multiple risk chips

**Hotspots:**
1. **Video Detection Overlay** → Modal: Video Analysis
   - Deepfake Confidence: 87%
   - Facial Landmark Inconsistencies: 12
   - Micro-expression Anomalies: Detected
   - Frame: [Sample frame with highlighted artifacts]
2. **Risk Indicator Chips** → Modal: Behavioral Analysis
   - Authority Bypass: 89% ("board approved")
   - Urgency Tactics: 76% ("time-sensitive")
   - Process Bypass: 85% ("usual process too slow")
3. **Alert Banner** → Modal: "When risk exceeds 70%, DeepSafe automatically initiates identity verification protocols."

---

### Step 6: Verification Triggered
**Duration:** 10-15 seconds

**Screen Content:**
- Verification modal overlay
- "Verifying participant identity..."
- Progress indicator with verification steps

**DeepSafe Elements:**
- Verification modal showing:
  - Step 1: ✓ Analyzing video authenticity
  - Step 2: ✓ Checking voice fingerprint
  - Step 3: ✓ Cross-referencing device data
  - Step 4: ⏳ Contacting verified identity...
- Risk meter: RED (78%), pulsing

**Hotspots:**
1. **Verification Modal** → Modal: "DeepSafe uses multi-factor verification including out-of-band SMS/email to the real person's verified contact information."
2. **Each Verification Step** → Individual modals explaining:
   - Video Analysis methodology
   - Voice fingerprint matching
   - Device/network verification
   - Identity confirmation process

---

### Step 7: Threat Confirmed & Removal
**Duration:** 12-15 seconds

**Screen Content:**
- Dramatic threat confirmation
- "David Mitchell" tile goes dark/removed
- Success animation

**DeepSafe Elements:**
- Full-screen overlay (brief): "🔴 THREAT CONFIRMED"
- Forensic summary card appears
- Risk meter: RED (87%) → Resolving
- Participant removed notification
- "David Mitchell" tile: Fades out with "Removed" badge

**Conversation:**
- System message: "Participant 'David Mitchell' has been removed due to security concerns."

**Hotspots:**
1. **Forensic Summary Card** → Full Forensic Modal:
   - Video Analysis: 92% deepfake confidence
   - Audio Analysis: 67% voice cloning
   - Network: VPN from Eastern Europe, Virtual Camera
   - Behavioral: 96% match to known BEC patterns
2. **Removal Notification** → Modal: "Threats are automatically removed from meetings. The real participant is notified via verified channels, and all evidence is preserved."

---

### Step 8: Incident Report
**Duration:** 15-20 seconds

**Screen Content:**
- Incident report overlay/panel
- Detailed breakdown of the attack
- Actions taken summary

**DeepSafe Elements:**
- Incident Report Card:
  - Incident ID: INC-2024-1209-001
  - Type: Deepfake Impersonation + Social Engineering
  - Duration: 3 minutes 35 seconds
  - Outcome: PREVENTED
  - Amount Protected: $250,000
- Timeline of events
- Evidence links

**Hotspots:**
1. **Incident Type** → Modal explaining attack classification
2. **Timeline** → Expandable full timeline with all events
3. **Evidence Links** → Modal: "All forensic evidence is preserved for investigation and can be exported for law enforcement if needed."
4. **Amount Protected** → Modal: "DeepSafe calculates protected amounts based on detected financial requests and transaction patterns."

---

### Step 9: Success Summary
**Duration:** Until user exits

**Screen Content:**
- Success celebration screen
- Key metrics displayed prominently
- Call-to-action for next steps

**Content:**
```
🛡️ ATTACK PREVENTED

$250,000 Protected

Detection Time: 1 minute 38 seconds
Threat Type: Deepfake + Social Engineering
Confidence: 92%

What DeepSafe Detected:
✓ AI-generated video (deepfake)
✓ Synthetic voice cloning
✓ Social engineering patterns
✓ Suspicious network origin
✓ Virtual camera software

[Replay Demo]  [Learn More]  [Request Demo]
```

**Hotspots:**
1. **Each Detection Item** → Detailed explanation modal
2. **Metrics** → Comparison to industry averages

---

## 6. UI/UX Design Specifications

### 6.1 Google Meet Interface Recreation

The demo mimics Google Meet's interface while adding DeepSafe overlay elements:

```
┌────────────────────────────────────────────────────────────────────────┐
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                                                                   │  │
│  │                    MAIN VIDEO TILE                               │  │
│  │                   "David Mitchell"                               │  │
│  │                                                                   │  │
│  │   ┌─────────────┐                                                │  │
│  │   │  DeepSafe   │  ← Risk Overlay (appears when risk > 30%)     │  │
│  │   │  Analyzing  │                                                │  │
│  │   └─────────────┘                                                │  │
│  │                                                                   │  │
│  │                                         ┌────────────┐           │  │
│  │                                         │   You      │           │  │
│  │                                         │(Sarah Chen)│           │  │
│  │                                         └────────────┘           │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                        │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │ 🎤 Mute │ 📹 Video │ 👤 People │ 💬 Chat │ ⚙️ More │ 🔴 Leave │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                        │
│  [═══════════════════════════════] RISK: 78% ████████░░ HIGH          │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Transcript Panel (Right Sidebar)

```
┌─────────────────────────────┐
│ 📝 Live Transcript          │
│ ─────────────────────────── │
│                             │
│ David Mitchell  10:00:15    │
│ "Thanks for joining on      │
│ short notice."              │
│ Risk: ████░░░░░░ 8%        │
│                             │
│ ─────────────────────────── │
│                             │
│ David Mitchell  10:01:38    │
│ "I need you to authorize    │
│ a wire transfer of          │
│ $250,000..."                │
│ Risk: █████████░ 91%  ⚠️   │
│ ┌─────────────────────────┐ │
│ │ 🚨 Credential Request   │ │
│ │ 💰 Financial Trans.     │ │
│ │ ⏰ Urgency Pattern      │ │
│ └─────────────────────────┘ │
│                             │
└─────────────────────────────┘
```

### 6.3 Risk Meter Component

The risk meter is the primary visual indicator of threat level:

```
LOW (0-30%)      MEDIUM (31-60%)     HIGH (61-85%)      CRITICAL (86-100%)
┌──────────┐     ┌──────────┐        ┌──────────┐       ┌──────────┐
│ ████░░░░ │     │ █████░░░ │        │ ███████░ │       │ █████████│
│   12%    │     │   45%    │        │   78%    │       │   92%    │
│  ✓ Safe  │     │ ⚠ Alert  │        │ 🔴 High  │       │ 🚨 CRIT  │
└──────────┘     └──────────┘        └──────────┘       └──────────┘
   Green            Amber              Orange/Red          Red/Pulse
```

### 6.4 Hotspot Indicator Design

Clickable elements are indicated by:

```
┌───────────────────────────────────┐
│                                   │
│   Element Text  [?]  ← Hotspot   │
│                  │                │
│                  └── Pulsing dot  │
│                      (teal glow)  │
│                                   │
└───────────────────────────────────┘
```

**Hotspot States:**
- Default: Subtle teal dot with gentle pulse
- Hover: Expanded tooltip preview
- Active: Modal opens with full explanation

### 6.5 Modal Design

Educational modals follow this structure:

```
┌──────────────────────────────────────────────────────────────┐
│  ┌────────────────────────────────────────────────────────┐  │
│  │  🎯 Risk Score Breakdown                           ✕   │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │                                                        │  │
│  │  This participant's risk score is calculated from:     │  │
│  │                                                        │  │
│  │  ┌──────────────────────────────────────────────────┐ │  │
│  │  │  VIDEO ANALYSIS              40% weight          │ │  │
│  │  │  ████████████████████░░░░░   87%                │ │  │
│  │  │  Deepfake confidence: HIGH                       │ │  │
│  │  └──────────────────────────────────────────────────┘ │  │
│  │                                                        │  │
│  │  ┌──────────────────────────────────────────────────┐ │  │
│  │  │  AUDIO ANALYSIS              30% weight          │ │  │
│  │  │  █████████████░░░░░░░░░░░░   67%                │ │  │
│  │  │  Voice cloning detected                          │ │  │
│  │  └──────────────────────────────────────────────────┘ │  │
│  │                                                        │  │
│  │  ┌──────────────────────────────────────────────────┐ │  │
│  │  │  BEHAVIORAL                  20% weight          │ │  │
│  │  │  ███████████████████████░░   89%                │ │  │
│  │  │  Social engineering patterns                     │ │  │
│  │  └──────────────────────────────────────────────────┘ │  │
│  │                                                        │  │
│  │  ┌──────────────────────────────────────────────────┐ │  │
│  │  │  NETWORK                     10% weight          │ │  │
│  │  │  ██████████████████████████  95%                │ │  │
│  │  │  VPN + Virtual camera + Unknown device           │ │  │
│  │  └──────────────────────────────────────────────────┘ │  │
│  │                                                        │  │
│  │  ═══════════════════════════════════════════════════  │  │
│  │  OVERALL RISK SCORE: 87% (CRITICAL)                   │  │
│  │                                                        │  │
│  └────────────────────────────────────────────────────────┘  │
│                                     [Got it]                  │
└──────────────────────────────────────────────────────────────┘
```

---

## 7. Technical Specifications

### 7.1 Risk Score Calculation

DeepSafe calculates risk using weighted analysis across four dimensions:

| Dimension | Weight | Components |
|-----------|--------|------------|
| **Video Analysis** | 40% | Deepfake confidence, facial landmarks, micro-expressions, lighting, edge artifacts, temporal consistency |
| **Audio Analysis** | 30% | Voice cloning confidence, spectral anomalies, prosody, A/V sync, background noise, voice fingerprint |
| **Behavioral Analysis** | 20% | Social engineering score, authority bypass, urgency tactics, isolation tactics, credential requests |
| **Network Analysis** | 10% | VPN detection, device fingerprint, geolocation anomaly, virtual camera detection |

**Formula:**
```
Overall Risk = (Video × 0.40) + (Audio × 0.30) + (Behavioral × 0.20) + (Network × 0.10)
```

**Example Calculation (Demo Scenario):**
```
Video:      92% × 0.40 = 36.8
Audio:      67% × 0.30 = 20.1
Behavioral: 89% × 0.20 = 17.8
Network:    95% × 0.10 =  9.5
─────────────────────────────
Overall Risk Score:     84.2% → Rounded to 84%
```

### 7.2 Risk Thresholds & Actions

| Risk Level | Score Range | Color | Automated Actions |
|------------|-------------|-------|-------------------|
| **Low** | 0-30% | Green (`#2DBE8B`) | Monitoring only |
| **Medium** | 31-60% | Amber (`#F5A623`) | Enhanced monitoring, flag for review |
| **High** | 61-85% | Orange-Red (`#FF6B6B`) | Alert displayed, verification triggered |
| **Critical** | 86-100% | Red (`#D64545`) | Immediate intervention, participant removal |

### 7.3 Forensic Evidence Structure

```typescript
interface ForensicEvidence {
  videoAnalysis: {
    deepfakeConfidence: number;           // 0-100
    facialLandmarkInconsistencies: number; // Count
    microExpressionAnomalies: boolean;
    lightingInconsistencies: number;       // Count
    edgeArtifacts: boolean;
    temporalInconsistencies: boolean;
    evidenceSamples: Array<{
      frameNumber: number;
      description: string;
      thumbnail?: string;                  // Base64 or URL
    }>;
  };

  audioAnalysis: {
    voiceCloningConfidence: number;        // 0-100
    spectralAnomalies: boolean;
    prosodyAnomalies: boolean;
    audioVideoDesync: number;              // Milliseconds
    backgroundNoiseInconsistency: boolean;
    voiceFingerprintMatch: boolean;
    evidenceSamples: Array<{
      timestamp: string;
      description: string;
    }>;
  };

  networkAnalysis: {
    ipAddress: string;                     // Masked for display
    location: string;
    vpnDetected: boolean;
    vpnProvider?: string;
    deviceOS: string;
    browser: string;
    deviceFingerprint: string;
    isKnownDevice: boolean;
    virtualCameraDetected: boolean;
    virtualCameraName?: string;
  };

  behavioralAnalysis: {
    socialEngineeringScore: number;        // 0-100
    authorityBypass: number;               // 0-100
    urgencyTactics: number;                // 0-100
    isolationTactics: number;              // 0-100
    credentialRequestRisk: number;         // 0-100
    conversationPatternMatch: number;      // 0-100
    knownAttackPatternSimilarity: string;  // Description
  };
}
```

### 7.4 Timeline Event Types

```typescript
type TimelineEventType =
  | 'meeting_start'        // Meeting begins, bot joins
  | 'bot_joined'           // DeepSafe protection active
  | 'anomaly_detected'     // First suspicious signal
  | 'risk_escalation'      // Multiple indicators confirm threat
  | 'verification_triggered' // Identity verification initiated
  | 'fraud_confirmed'      // Threat confirmed via verification
  | 'participant_removed'  // Attacker removed from meeting
  | 'incident_resolved'    // Security notified, evidence preserved
  | 'meeting_end';         // Meeting concluded

type EventSeverity = 'info' | 'warning' | 'error' | 'success';
```

### 7.5 Transcript Risk Indicators

```typescript
type RiskIndicator =
  | 'credential_request'      // Asking for passwords, access codes
  | 'financial_transaction'   // Wire transfers, payments
  | 'authority_bypass'        // "CEO approved", "board authorized"
  | 'urgency_tactics'         // "urgent", "immediately", "time-sensitive"
  | 'isolation_tactics'       // "keep this confidential", "don't tell"
  | 'process_bypass'          // "skip the usual workflow"
  | 'personal_liability'      // "I'll take responsibility"
  | 'social_engineering';     // General manipulation pattern match
```

---

## 8. Interactive Features

### 8.1 Step Navigation

**Navigation Bar (Bottom of screen):**

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│   [◀ Back]     Step 5 of 9: Risk Escalation     [▶ Next]           │
│                                                                      │
│   ●───●───●───●───●───○───○───○───○                                 │
│   1   2   3   4   5   6   7   8   9                                 │
│                                                                      │
│   [⏵ Auto-play]  Speed: [Slow ▼]                                    │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

**Controls:**
- **Back/Next Buttons:** Navigate between steps
- **Progress Dots:** Click to jump to any step (visited steps shown as filled)
- **Auto-play Toggle:** Enables automatic progression
- **Speed Control:** Slow (20s), Normal (12s), Fast (6s) per step

**Keyboard Shortcuts:**
- `←` / `→` : Previous / Next step
- `Space` : Play / Pause auto-play
- `1-9` : Jump to specific step
- `Esc` : Close any open modal

### 8.2 Hotspot System

**Types of Hotspots:**

1. **Info Hotspots** (Blue pulsing dot)
   - General educational information
   - Click to open explanation modal

2. **Data Hotspots** (Teal pulsing dot)
   - Technical data with deep-dive capability
   - Click to see detailed breakdowns

3. **Action Hotspots** (Amber pulsing dot)
   - Appear during key moments
   - Highlight what DeepSafe is doing

**Hotspot Behavior:**
- Appear after 2-second delay on each step
- Gentle pulse animation (2s cycle)
- Tooltip preview on hover (300ms delay)
- Full modal on click
- "Don't show hints" option for repeat users

### 8.3 Modal Types

| Modal Type | Trigger | Content |
|------------|---------|---------|
| **Explainer** | Info hotspot click | Educational text with graphics |
| **Data Breakdown** | Risk score click | Detailed metrics with charts |
| **Evidence Viewer** | Forensic hotspot click | Evidence samples with analysis |
| **Timeline Detail** | Event click | Full event context and impact |
| **Glossary** | Term click | Definition and examples |

### 8.4 Progress Persistence

**Local Storage:**
- Current step position
- Viewed hotspots (for "complete demo" tracking)
- Preferred speed setting
- Hints enabled/disabled

---

## 9. Component Architecture

### 9.1 File Structure

```
/src/pages/Demo/
├── DemoPage.tsx                 # Main demo container
├── index.ts                     # Exports
├── hooks/
│   ├── useDemoState.ts          # Demo progression state
│   ├── useDemoData.ts           # Scenario data management
│   └── useAutoPlay.ts           # Auto-play timer logic
├── components/
│   ├── VideoCallInterface/
│   │   ├── VideoCallInterface.tsx
│   │   ├── ParticipantTile.tsx
│   │   ├── ControlBar.tsx
│   │   └── MeetingHeader.tsx
│   ├── DeepSafeOverlay/
│   │   ├── RiskMeter.tsx
│   │   ├── AlertBanner.tsx
│   │   ├── DetectionOverlay.tsx
│   │   └── VerificationModal.tsx
│   ├── TranscriptPanel/
│   │   ├── TranscriptPanel.tsx
│   │   ├── TranscriptEntry.tsx
│   │   └── RiskChips.tsx
│   ├── Navigation/
│   │   ├── StepNavigation.tsx
│   │   ├── ProgressIndicator.tsx
│   │   └── AutoPlayControls.tsx
│   ├── Modals/
│   │   ├── ExplainerModal.tsx
│   │   ├── ForensicModal.tsx
│   │   ├── RiskBreakdownModal.tsx
│   │   └── TimelineModal.tsx
│   ├── Hotspots/
│   │   ├── Hotspot.tsx
│   │   └── HotspotTooltip.tsx
│   └── Screens/
│       ├── WelcomeScreen.tsx
│       ├── LobbyScreen.tsx
│       ├── IncidentReportScreen.tsx
│       └── SuccessScreen.tsx
├── data/
│   ├── demoScenario.ts          # Full scenario configuration
│   ├── transcriptData.ts        # Conversation script
│   ├── forensicData.ts          # Forensic evidence data
│   └── hotspotContent.ts        # Educational content
└── types/
    └── demo.types.ts            # TypeScript interfaces
```

### 9.2 Key Components

#### DemoPage.tsx (Main Container)
```typescript
interface DemoPageProps {
  standalone?: boolean;  // For standalone build
}

// Manages:
// - Current step state
// - Modal visibility
// - Auto-play logic
// - Keyboard navigation
```

#### VideoCallInterface.tsx
```typescript
interface VideoCallInterfaceProps {
  participants: Participant[];
  currentSpeaker: string;
  riskOverlay?: RiskOverlayState;
  onHotspotClick: (hotspotId: string) => void;
}
```

#### RiskMeter.tsx
```typescript
interface RiskMeterProps {
  score: number;          // 0-100
  animated?: boolean;     // Smooth transitions
  showLabel?: boolean;    // "LOW" / "HIGH" etc.
  compact?: boolean;      // For sidebar placement
}
```

#### TranscriptPanel.tsx
```typescript
interface TranscriptPanelProps {
  entries: TranscriptEntry[];
  highlightedEntryId?: string;
  onEntryClick: (entry: TranscriptEntry) => void;
}
```

### 9.3 State Management

```typescript
interface DemoState {
  currentStep: number;           // 1-9
  isPlaying: boolean;            // Auto-play active
  playbackSpeed: 'slow' | 'normal' | 'fast';
  activeModal: ModalType | null;
  visitedHotspots: string[];
  riskScore: number;             // Current animated value
  transcriptEntries: TranscriptEntry[];
  timelineEvents: TimelineEvent[];
}
```

---

## 10. Data Models

### 10.1 Demo Step Configuration

```typescript
interface DemoStep {
  id: number;
  name: string;
  duration: number;              // Seconds (for auto-play)
  component: 'lobby' | 'call' | 'report' | 'success';

  // Video call state
  participants?: Participant[];
  activeSpeaker?: string;

  // DeepSafe state
  riskScore: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  alerts?: Alert[];

  // Transcript state
  transcriptUpTo: number;        // Show entries up to this index
  highlightEntry?: number;       // Entry to highlight

  // Overlays
  showVerification?: boolean;
  showThreatConfirmed?: boolean;
  showRemovalAnimation?: boolean;

  // Hotspots for this step
  hotspots: Hotspot[];
}
```

### 10.2 Participant Model

```typescript
interface DemoParticipant {
  id: string;
  name: string;
  role: string;                  // "CEO", "CFO"
  email: string;
  avatar: string;                // Image URL
  isSpeaking: boolean;
  trustScore: number;
  isAttacker: boolean;

  // Visual states
  showDetectionOverlay?: boolean;
  showRemovalAnimation?: boolean;

  // For attacker
  realIdentity?: {
    name: string;
    location: string;
  };
}
```

### 10.3 Hotspot Model

```typescript
interface Hotspot {
  id: string;
  type: 'info' | 'data' | 'action';
  position: {
    anchor: string;              // CSS selector or element ID
    offsetX: number;
    offsetY: number;
  };
  tooltip: string;               // Short preview text
  modal: {
    title: string;
    content: ReactNode | string;
    size: 'sm' | 'md' | 'lg';
  };
}
```

---

## 11. Branding & Style Guide

### 11.1 Color Palette

**Primary Colors:**
```css
--deepsafe-blue: #1F3C88;        /* Primary brand */
--signal-teal: #1FB6A6;          /* Secondary/accent */
--threat-red: #D64545;           /* Critical alerts */
--alert-amber: #F5A623;          /* Warnings */
```

**Dark Mode Backgrounds:**
```css
--bg-deepest: #05070C;
--bg-primary: #0B1220;
--bg-surface: #121C2E;
--bg-elevated: #1A2740;
```

**Risk Gradients:**
```css
--gradient-low: linear-gradient(135deg, #2DBE8B, #3AD6A3);
--gradient-medium: linear-gradient(135deg, #F5A623, #FFC857);
--gradient-high: linear-gradient(135deg, #FF6B6B, #F5A623);
--gradient-critical: linear-gradient(135deg, #D64545, #FF6B6B);
```

### 11.2 Typography

```css
/* Headlines */
font-family: 'Space Grotesk', sans-serif;
font-weight: 700;

/* Body/UI */
font-family: 'Inter', sans-serif;
font-weight: 400-600;

/* Technical Data */
font-family: 'JetBrains Mono', monospace;
font-weight: 400;
```

### 11.3 Visual Effects

**Glassmorphism:**
```css
background: rgba(18, 28, 46, 0.7);
backdrop-filter: blur(10px);
border: 1px solid rgba(255, 255, 255, 0.08);
```

**Risk Meter Glow:**
```css
/* High risk state */
box-shadow: 0 0 20px rgba(214, 69, 69, 0.5);
```

**Hotspot Pulse:**
```css
@keyframes hotspot-pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.2); opacity: 0.7; }
}
animation: hotspot-pulse 2s ease-in-out infinite;
```

### 11.4 Component Styling

**Cards:**
```css
border-radius: 16px;
padding: 24px;
background: linear-gradient(180deg, #121C2E, #1A2740);
border: 1px solid rgba(255, 255, 255, 0.08);
box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
```

**Buttons:**
```css
/* Primary */
background: linear-gradient(135deg, #1FB6A6, #1F3C88);
border-radius: 8px;
font-weight: 600;
padding: 12px 24px;

/* Hover */
transform: translateY(-2px);
box-shadow: 0 4px 12px rgba(31, 182, 166, 0.3);
```

---

## 12. Accessibility Requirements

### 12.1 WCAG 2.1 AA Compliance

| Requirement | Implementation |
|-------------|----------------|
| **Color Contrast** | Minimum 4.5:1 for body text, 3:1 for large text |
| **Keyboard Navigation** | Full demo navigable via keyboard |
| **Focus Indicators** | Visible focus rings on all interactive elements |
| **Screen Reader** | ARIA labels on all components, live regions for alerts |
| **Motion** | Respect `prefers-reduced-motion` for animations |
| **Text Sizing** | Support browser zoom up to 200% |

### 12.2 Keyboard Shortcuts Reference

| Key | Action |
|-----|--------|
| `Tab` | Move to next interactive element |
| `Shift+Tab` | Move to previous element |
| `Enter/Space` | Activate button/hotspot |
| `Escape` | Close modal, cancel action |
| `←` / `→` | Previous/Next step |
| `1-9` | Jump to step |

### 12.3 Screen Reader Announcements

```typescript
// Announce risk level changes
announceToScreenReader(`Risk level changed to ${riskLevel}. Current score: ${score} percent.`);

// Announce step transitions
announceToScreenReader(`Step ${stepNumber} of 9: ${stepName}`);

// Announce alerts
announceToScreenReader(`Alert: ${alertMessage}`, 'assertive');
```

---

## 13. Deployment Strategy

### 13.1 Integrated Deployment

**Route:** `/demo`

**Build Command:** Standard `npm run build`

**Configuration:**
```typescript
// App.tsx
<Route path="demo" element={<DemoPage />} />
```

### 13.2 Standalone Deployment

**Build Command:** `npm run build:demo`

**Vite Configuration:**
```typescript
// vite.config.demo.ts
export default defineConfig({
  build: {
    outDir: 'dist-demo',
    rollupOptions: {
      input: 'src/demo-entry.tsx',
    },
  },
});
```

**Entry Point:**
```typescript
// src/demo-entry.tsx
import { DemoPage } from './pages/Demo';
import { ThemeProvider } from './context/ThemeContext';

const StandaloneDemo = () => (
  <ThemeProvider>
    <DemoPage standalone />
  </ThemeProvider>
);

ReactDOM.createRoot(document.getElementById('root')!).render(<StandaloneDemo />);
```

### 13.3 Embedding Options

**Iframe Embed:**
```html
<iframe
  src="https://demo.deepsafe.ai"
  width="100%"
  height="800px"
  frameborder="0"
  allow="fullscreen"
></iframe>
```

**URL Parameters:**
- `?autoplay=true` - Start auto-playing immediately
- `?speed=fast` - Set playback speed
- `?step=5` - Start at specific step
- `?dark=true` - Force dark mode

---

## 14. Success Metrics

### 14.1 Engagement Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Completion Rate** | > 80% | Users who reach Step 9 |
| **Avg. Time in Demo** | 4-6 minutes | Time from start to completion |
| **Hotspot Engagement** | > 3 per user | Average hotspots clicked |
| **Replay Rate** | > 15% | Users who restart demo |

### 14.2 Business Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Demo-to-Lead Rate** | > 25% | CTA clicks after completion |
| **Sales Qualification** | > 40% | Leads mentioning demo |
| **Time-to-Value** | < 5 min | Understanding core value prop |

### 14.3 Technical Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Load Time** | < 3s | Time to interactive |
| **Error Rate** | < 0.1% | JavaScript errors |
| **Bounce Rate** | < 20% | Exit before Step 3 |

---

## 15. Appendix

### 15.1 Full Transcript Data

See: [Demo Scenario Section 4.4](#44-full-conversation-script)

### 15.2 Forensic Evidence Data (Demo Scenario)

```typescript
const demoForensicData: ForensicEvidence = {
  videoAnalysis: {
    deepfakeConfidence: 92,
    facialLandmarkInconsistencies: 12,
    microExpressionAnomalies: true,
    lightingInconsistencies: 3,
    edgeArtifacts: true,
    temporalInconsistencies: true,
    evidenceSamples: [
      { frameNumber: 145, description: 'Facial landmark anomaly detected - unnatural eye movement' },
      { frameNumber: 892, description: 'Lighting inconsistency in shadow regions' },
      { frameNumber: 1203, description: 'Digital edge artifacts detected around jawline' },
    ],
  },
  audioAnalysis: {
    voiceCloningConfidence: 67,
    spectralAnomalies: true,
    prosodyAnomalies: true,
    audioVideoDesync: 42,
    backgroundNoiseInconsistency: true,
    voiceFingerprintMatch: false,
    evidenceSamples: [
      { timestamp: '00:01:38', description: 'Synthetic voice markers detected in urgency phrase' },
      { timestamp: '00:02:28', description: 'Prosody pattern inconsistent with baseline' },
    ],
  },
  networkAnalysis: {
    ipAddress: '185.220.XXX.XXX',
    location: 'Bucharest, Romania',
    vpnDetected: true,
    vpnProvider: 'NordVPN',
    deviceOS: 'Windows 11 Pro',
    browser: 'Chrome 120.0.6099.129',
    deviceFingerprint: 'unknown-device-fp-001',
    isKnownDevice: false,
    virtualCameraDetected: true,
    virtualCameraName: 'OBS Virtual Camera',
  },
  behavioralAnalysis: {
    socialEngineeringScore: 89,
    authorityBypass: 89,
    urgencyTactics: 76,
    isolationTactics: 82,
    credentialRequestRisk: 95,
    conversationPatternMatch: 96,
    knownAttackPatternSimilarity: '96% similarity to known BEC/credential theft attacks',
  },
};
```

### 15.3 Risk Indicator Definitions

| Indicator | Description | Risk Weight |
|-----------|-------------|-------------|
| `credential_request` | Direct request for passwords, access codes, or system credentials | HIGH (85-95) |
| `financial_transaction` | Request to transfer money, authorize payments, or share financial info | HIGH (80-95) |
| `authority_bypass` | Claims of executive approval without verification ("CEO approved") | HIGH (75-89) |
| `urgency_tactics` | Time pressure language ("urgent", "immediately", "deadline") | MEDIUM (65-80) |
| `isolation_tactics` | Requests for secrecy ("keep confidential", "don't tell") | MEDIUM (60-82) |
| `process_bypass` | Requests to skip normal approval workflows | MEDIUM (70-85) |
| `personal_liability` | Attacker claims they'll "take responsibility" | MEDIUM (50-70) |

### 15.4 Image Assets Required

| Asset | Description | Dimensions | Format |
|-------|-------------|------------|--------|
| `david-mitchell.jpg` | "CEO" deepfake avatar (AI-generated face) | 400x400 | JPEG |
| `sarah-chen.jpg` | CFO participant avatar | 400x400 | JPEG |
| `deepsafe-bot.svg` | Bot avatar for participant list | 48x48 | SVG |
| `google-meet-bg.jpg` | Meeting background blur | 1920x1080 | JPEG |
| `evidence-frame-*.png` | Forensic evidence frame samples | 640x360 | PNG |
| `logo-deepsafe.svg` | DeepSafe logo for overlays | 200x48 | SVG |

### 15.5 Animation Specifications

| Animation | Duration | Easing | Trigger |
|-----------|----------|--------|---------|
| Risk meter fill | 1.5s | ease-out | Risk score change |
| Alert banner slide | 0.3s | ease-in-out | Alert display |
| Hotspot pulse | 2s | ease-in-out | Continuous (loop) |
| Modal fade-in | 0.2s | ease-out | Modal open |
| Participant removal | 0.8s | ease-in | Threat removal |
| Step transition | 0.4s | ease-in-out | Navigation |
| Risk chip appear | 0.3s | spring(1, 80, 10) | New risk detected |

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 2024 | DeepSafe Product Team | Initial PRD creation |

---

*This PRD is a living document and will be updated as requirements evolve during development.*
