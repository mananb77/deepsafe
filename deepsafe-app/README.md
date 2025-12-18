# DeepSafe Security Dashboard

A modern React/TypeScript security dashboard for monitoring video conference security, detecting deepfakes, and protecting organizations from AI-powered social engineering attacks.

## Overview

DeepSafe provides real-time monitoring and analysis of video conferences across platforms like Zoom, Google Meet, and Microsoft Teams. The dashboard enables security teams to:

- Monitor meetings for deepfake and social engineering threats
- Analyze participant trust scores and verification status
- Review forensic evidence of detected incidents
- Configure alerts and notification preferences
- Track security metrics and risk trends

## Technology Stack

| Category | Technology |
|----------|------------|
| Framework | React 19.2 |
| Language | TypeScript 5.9 |
| UI Library | Material-UI (MUI) 7.3 |
| State Management | Redux Toolkit 2.11 |
| Data Fetching | TanStack React Query 5.90 |
| Routing | React Router 7.10 |
| Charts | Recharts 3.5 |
| Build Tool | Vite 7.2 |
| HTTP Client | Axios 1.13 |

## Prerequisites

- Node.js 18.x or higher
- npm 9.x or higher

## Quick Start

```bash
# Clone the repository
git clone https://github.com/mananb77/deepsafe.git
cd deepsafe/deepsafe-app

# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at `http://localhost:5173`

## Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server with hot reload |
| `npm run build` | Build for production (TypeScript compile + Vite bundle) |
| `npm run preview` | Preview production build locally |
| `npm run lint` | Run ESLint for code quality checks |

## Project Structure

```
deepsafe-app/
├── src/
│   ├── assets/           # Images, icons, static assets
│   ├── components/       # Reusable React components
│   │   ├── common/       # Shared UI components (MetricCard, RiskBadge, etc.)
│   │   ├── features/     # Feature-specific components
│   │   └── layout/       # Layout components (Header, MainLayout)
│   ├── context/          # React Context providers (ThemeContext)
│   ├── data/             # Mock data and data generators
│   ├── hooks/            # Custom React hooks
│   ├── pages/            # Page components
│   │   ├── Dashboard/    # Security overview dashboard
│   │   ├── Meetings/     # Meeting history and details
│   │   ├── Participants/ # Participant monitoring
│   │   ├── Settings/     # Configuration options
│   │   ├── Profile/      # User profile management
│   │   └── Support/      # Help and documentation
│   ├── services/         # API service layer
│   ├── store/            # Redux store configuration
│   ├── theme/            # Theming and styling
│   ├── types/            # TypeScript type definitions
│   ├── App.tsx           # Main app with routing
│   └── main.tsx          # Application entry point
├── public/               # Static public assets
├── docs/                 # Documentation
├── package.json          # Dependencies and scripts
├── tsconfig.json         # TypeScript configuration
├── vite.config.ts        # Vite build configuration
└── eslint.config.js      # ESLint configuration
```

## Pages

| Page | Route | Description |
|------|-------|-------------|
| Dashboard | `/dashboard` | Security metrics, risk trends, recent incidents |
| Meetings | `/meetings` | Meeting history with filtering and search |
| Meeting Details | `/meetings/:id` | Timeline, transcript, forensic analysis |
| Participants | `/participants` | Participant list with trust scores |
| Participant Profile | `/participants/:id` | Individual threat intelligence |
| Settings | `/settings` | Alerts, integrations, security config |
| Profile | `/profile` | User info and connected devices |
| Support | `/support` | FAQ and help resources |

## Features

- **Real-time Dashboard** - Key security metrics with trend analysis
- **Meeting Forensics** - Multi-tab analysis (timeline, transcript, video/audio/network forensics)
- **Risk Scoring** - Four-level system (Low, Medium, High, Critical)
- **Trust Badges** - Verification status and trust score indicators
- **Dark/Light Themes** - Professional dual-theme design system
- **Platform Integrations** - Zoom, Google Meet, Microsoft Teams, Webex
- **Configurable Alerts** - Sensitivity sliders and notification preferences

## Theme System

DeepSafe uses a custom theme with brand colors:

| Color | Hex | Usage |
|-------|-----|-------|
| DeepSafe Blue | `#1F3C88` | Primary brand color |
| Signal Teal | `#1FB6A6` | Secondary/accent |
| Alert Amber | `#F5A623` | Warnings |
| Threat Red | `#D64545` | Critical alerts |

Toggle between dark and light modes using the theme switcher in the header.

## Documentation

- [User Guide](docs/USER_GUIDE.md) - Complete walkthrough of all features
- [Features](docs/FEATURES.md) - Detailed feature descriptions
- [Architecture](docs/ARCHITECTURE.md) - Technical architecture overview

## Development

### Adding New Pages

1. Create page component in `src/pages/YourPage/`
2. Add route in `src/App.tsx`
3. Add navigation link in `src/components/layout/Header.tsx`

### Adding New Components

1. Create component in appropriate `src/components/` subdirectory
2. Export from the directory's `index.ts`
3. Use MUI components and theme tokens for consistency

### API Integration

The `src/services/` directory is prepared for API integration. Currently using mock data from `src/data/` for development.

## License

Proprietary - DeepSafe Inc.
