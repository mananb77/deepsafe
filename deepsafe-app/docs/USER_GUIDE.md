# DeepSafe User Guide

A complete walkthrough of the DeepSafe Security Dashboard for security analysts and administrators.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Navigation Overview](#navigation-overview)
3. [Dashboard](#dashboard)
4. [Meetings](#meetings)
5. [Meeting Details](#meeting-details)
6. [Participants](#participants)
7. [Participant Profile](#participant-profile)
8. [Settings](#settings)
9. [Profile](#profile)
10. [Support](#support)
11. [Theme Switching](#theme-switching)
12. [Tips & Best Practices](#tips--best-practices)

---

## Getting Started

### First Login

1. Navigate to the DeepSafe dashboard URL provided by your administrator
2. Log in using your organization's SSO credentials
3. Complete multi-factor authentication if required
4. You'll be directed to the main Dashboard

### Understanding the Interface

The DeepSafe interface consists of:
- **Header** - Navigation, search, notifications, and user menu
- **Main Content Area** - Page-specific content
- **Theme Toggle** - Switch between dark and light modes

---

## Navigation Overview

Access all areas of DeepSafe through the header navigation:

| Menu Item | Description |
|-----------|-------------|
| Dashboard | Security overview and metrics |
| Meetings | Meeting history and analysis |
| Participants | User monitoring and profiles |
| Settings | Configuration and preferences |
| Profile | Your account settings |
| Support | Help and documentation |

The notification bell shows unread alerts. Click to view recent security notifications.

---

## Dashboard

**Route:** `/dashboard`

The Dashboard provides a real-time overview of your organization's video conference security.

### Metrics Cards

At the top of the dashboard, you'll find six key metrics:

1. **Total Meetings** - All meetings monitored in the selected period
   - Green arrow = increase from previous period
   - Red arrow = decrease from previous period

2. **Total Participants** - Unique individuals across all meetings

3. **Compromised Meetings** - Meetings with confirmed security incidents

4. **Suspicious Users** - Participants flagged for review

5. **Money Protected** - Estimated value of prevented fraud

6. **Avg Response Time** - Mean incident response duration

### Risk Trend Chart

The line chart shows your organization's risk score over the past 31 days:
- **Y-axis** - Risk score (0-100)
- **X-axis** - Date
- **Spikes** indicate security incidents
- Hover over points for exact values

### Recent Incidents

A scrollable list of the latest security events:
- Click any incident card to view full details
- Color coding indicates severity (green=low, red=critical)
- Shows incident type, time, and current status

### Quick Actions

Buttons for common tasks:
- View all meetings
- Review flagged participants
- Export security report

### Date Range Filter

Use the date picker in the top-right to filter dashboard data by custom date ranges.

---

## Meetings

**Route:** `/meetings`

Browse and search your complete meeting history.

### Filtering Meetings

**Date Range:**
1. Click the date fields
2. Select start and end dates
3. Results update automatically

**Risk Category:**
- Use the dropdown to filter by: All, Low, Medium, High, Critical

**Sort Order:**
- Date (newest/oldest)
- Risk score (highest/lowest)
- Meeting name (A-Z/Z-A)

**Search:**
- Type in the search box to find meetings by name or ID
- Search is case-insensitive
- Results update as you type

### Reading the Meeting List

Each row shows:
| Column | Information |
|--------|-------------|
| Meeting ID | Unique identifier (click to copy) |
| Meeting Name | Title of the meeting |
| Date | When the meeting occurred |
| Risk Score | Numerical risk value (0-100) |
| Risk Category | Low/Medium/High/Critical badge |
| Participants | Number of attendees |
| Actions | View details button |

### Summary Statistics

Above the table, four summary cards show:
- Total meetings matching filters
- Unique participants
- Compromised meetings count
- Suspicious users identified

### Pagination

At the bottom of the table:
- Choose rows per page (5, 10, 20, 50)
- Navigate between pages
- View current position (e.g., "1-10 of 126")

### Viewing Meeting Details

Click any meeting row or the "View" button to open the Meeting Details page.

---

## Meeting Details

**Route:** `/meetings/:meetingId`

Deep analysis of a specific meeting with multiple forensic views.

### Meeting Header

Shows key information:
- Meeting name and ID
- Date, time, and duration
- Platform (Zoom, Meet, Teams)
- Host name
- Overall risk score badge

### Tabs

#### Overview Tab
- Meeting summary
- Participant list with roles
- Key findings highlighted
- Incident summary if applicable

#### Timeline Tab
- Chronological event log
- Each event shows:
  - Timestamp
  - Event type icon
  - Description
  - Related participants

**Event Types:**
- Meeting Start/End
- Bot Joined (DeepSafe monitoring began)
- Anomaly Detected
- Verification Triggered
- Verification Success/Failure
- Fraud Confirmed/Cleared

#### Participants Tab
- All attendees listed
- Trust score for each
- Role (Host, Participant, Guest)
- Verification status badge
- Click to view full profile

#### Transcript Tab
- Full meeting transcript (if available)
- Speaker labels
- Timestamps
- Risk-flagged segments highlighted in yellow/red
- Per-segment risk scores
- Use Ctrl+F to search within transcript

#### Forensics Tab

**Video Analysis:**
- Face manipulation score
- Liveness detection results
- Frame anomaly detection
- Lighting inconsistency checks

**Audio Analysis:**
- Voice pattern match score
- Deepfake probability
- Audio-video sync analysis
- Background noise analysis

**Network Analysis:**
- IP address and geolocation
- VPN/proxy detection
- Connection stability
- Known malicious IP checks

**Behavioral Analysis:**
- Typing pattern analysis
- Mouse movement patterns
- Response timing anomalies
- Engagement metrics

---

## Participants

**Route:** `/participants`

Monitor all participants across your organization's meetings.

### Filtering Participants

**Status Filter:**
Select one or more statuses:
- Verified - Confirmed employees
- Guest - Invited externals
- External - Unknown externals
- Flagged - Under review
- Blacklisted - Blocked users

**Risk Level:**
- All, Low, Medium, High, Critical

**Meeting Count:**
Filter by number of meetings attended

**Search:**
Search by name or email

### Reading the Participant List

| Column | Information |
|--------|-------------|
| Name | Participant's display name |
| Email | Contact email address |
| Status | Verification status badge |
| Trust Score | 0-100 trust rating |
| Meetings | Total meetings attended |
| Last Seen | Most recent activity |
| Risk | Risk level badge |

### Status Badge Colors

| Status | Color | Meaning |
|--------|-------|---------|
| Verified | Green | Confirmed via SSO |
| Guest | Blue | Invited external |
| External | Gray | Unknown external |
| Flagged | Orange | Requires review |
| Blacklisted | Red | Blocked |

### Viewing Participant Profile

Click any row to open the full Participant Profile.

---

## Participant Profile

**Route:** `/participants/:participantId`

Comprehensive view of an individual participant.

### Profile Header
- Full name and avatar
- Email and organization
- Status badge
- Trust score gauge

### Verification Details
- Authentication method (SSO, MFA, etc.)
- Known devices list
- Verified locations
- Biometric status

### Threat Intelligence

**Detection History:**
- Deepfake detection attempts
- Voice cloning flags
- Anomaly incidents

**Device Information:**
- Device fingerprints
- Browser/OS details
- Connection patterns

**Location Data:**
- Expected locations
- Anomalous logins
- VPN usage history

### Meeting History
- Chronological list of all meetings
- Incidents per meeting
- Risk score trends
- Filter by date range

### Actions

**For Flagged Users:**
- Clear flag (with reason)
- Escalate to blacklist
- Request verification

**For Blacklisted Users:**
- View block reason
- Remove from blacklist (admin only)

---

## Settings

**Route:** `/settings`

Configure DeepSafe to match your security requirements.

### Alert Configuration

**Sensitivity Sliders:**
- Deepfake Detection (1-10)
- Social Engineering Detection (1-10)
- Anomaly Threshold (1-10)

Higher values = more alerts, fewer false negatives
Lower values = fewer alerts, fewer false positives

### Notification Preferences

Toggle notifications for:
- Real-time threat alerts
- Daily security summaries
- Weekly trend reports
- Incident resolution updates

**Channels:**
- In-app notifications
- Email alerts
- SMS (critical only)

### Integration Settings

**Connected Platforms:**
- Zoom - Connect/disconnect OAuth
- Google Meet - Extension status
- Microsoft Teams - Bot status
- Webex - API connection

**For Each Platform:**
- Enable/disable monitoring
- Auto-join settings
- Recording preferences

### Security Settings

**API Keys:**
- View active API keys
- Generate new keys
- Revoke existing keys

**Device Management:**
- View authorized devices
- Remove trusted devices
- Enforce device policies

### Theme Customization

- Dark mode (default)
- Light mode
- Auto (match system)

### Two-Factor Authentication

- Enable/disable 2FA
- Configure authenticator app
- Backup codes

---

## Profile

**Route:** `/profile`

Manage your personal account settings.

### Personal Information
- Display name
- Email address
- Phone number
- Profile photo

### Connected Devices
- List of your authorized devices
- Device type and OS
- Last active timestamp
- Remove device option

### Security Status
- 2FA status
- Password last changed
- Active sessions

### Activity Log
- Recent login history
- Settings changes
- API usage

### Quick Stats
- Meetings attended
- Incidents you've reviewed
- Reports generated

---

## Support

**Route:** `/support`

Access help resources and documentation.

### FAQ Section
Expandable accordion with common questions:
- Getting started guides
- Troubleshooting tips
- Feature explanations

Click any question to expand the answer.

### Quick Help Cards
- Documentation links
- Video tutorials
- Contact support
- Release notes

### System Status
Real-time status of DeepSafe services:
- API status
- Detection engine
- Notification service
- Platform integrations

Green = operational
Yellow = degraded
Red = outage

### Contact Support
- Email support form
- Live chat (business hours)
- Emergency hotline (critical incidents)

---

## Theme Switching

DeepSafe supports dark and light themes.

### Toggle Theme
1. Look for the sun/moon icon in the header
2. Click to switch between modes
3. Your preference is saved automatically

### Theme Recommendations
- **Dark Mode** - Recommended for:
  - Extended monitoring sessions
  - Low-light environments
  - Reduced eye strain

- **Light Mode** - Recommended for:
  - Presentations
  - Bright office environments
  - Printing reports

---

## Tips & Best Practices

### Daily Workflow

1. **Start with Dashboard**
   - Review overnight incidents
   - Check risk trend for spikes
   - Note any critical alerts

2. **Review Flagged Participants**
   - Investigate new flags
   - Clear false positives
   - Escalate confirmed threats

3. **Check Recent Meetings**
   - Focus on high-risk meetings
   - Review forensic evidence
   - Document findings

### Investigation Best Practices

1. **Start with Timeline**
   - Understand event sequence
   - Identify trigger points
   - Note verification outcomes

2. **Cross-Reference Participants**
   - Check participant history
   - Look for patterns
   - Review threat intelligence

3. **Document Everything**
   - Add notes to incidents
   - Record investigation steps
   - Export reports for records

### Alert Tuning

1. **Start Conservative**
   - Begin with default sensitivity
   - Monitor false positive rate
   - Adjust incrementally

2. **Platform-Specific Tuning**
   - Different platforms may need different thresholds
   - Consider user populations
   - Account for meeting types

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl + K` | Global search |
| `Ctrl + /` | Toggle theme |
| `Esc` | Close modal/dialog |
| `?` | Show shortcuts help |

---

## Getting Help

If you need assistance:

1. Check the FAQ in Support
2. Search documentation
3. Contact your administrator
4. Reach out to DeepSafe support

For critical security incidents, use the emergency hotline provided by your organization.
