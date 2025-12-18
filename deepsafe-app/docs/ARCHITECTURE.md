# DeepSafe Architecture

Technical architecture documentation for developers working on the DeepSafe Security Dashboard.

---

## Table of Contents

1. [Overview](#overview)
2. [Directory Structure](#directory-structure)
3. [Component Architecture](#component-architecture)
4. [State Management](#state-management)
5. [Data Flow](#data-flow)
6. [Routing](#routing)
7. [Theming System](#theming-system)
8. [Type System](#type-system)
9. [API Integration](#api-integration)
10. [Build & Development](#build--development)

---

## Overview

DeepSafe is a single-page application (SPA) built with modern React patterns:

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser                               │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    React Application                     ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ ││
│  │  │   Router    │  │   Theme     │  │   State Mgmt    │ ││
│  │  │ React Router│  │  MUI Theme  │  │  Redux + Query  │ ││
│  │  └──────┬──────┘  └──────┬──────┘  └────────┬────────┘ ││
│  │         │                │                   │          ││
│  │         ▼                ▼                   ▼          ││
│  │  ┌─────────────────────────────────────────────────────┐││
│  │  │                    Components                        │││
│  │  │  Layout → Pages → Features → Common                  │││
│  │  └─────────────────────────────────────────────────────┘││
│  │                          │                               ││
│  │                          ▼                               ││
│  │  ┌─────────────────────────────────────────────────────┐││
│  │  │                   Data Layer                         │││
│  │  │  Services → Mock Data / API                          │││
│  │  └─────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

**Key Technologies:**
- React 19.2 with functional components and hooks
- TypeScript 5.9 for type safety
- Material-UI 7.3 for UI components
- Redux Toolkit for global state
- React Query for server state
- React Router 7 for routing
- Vite for building

---

## Directory Structure

```
src/
├── assets/                 # Static assets (images, icons)
│
├── components/             # Reusable React components
│   ├── common/             # Shared UI components
│   │   ├── MetricCard.tsx      # Dashboard metric display
│   │   ├── RiskBadge.tsx       # Risk level indicator
│   │   ├── RiskIndicator.tsx   # Detailed risk visualization
│   │   ├── TrustBadge.tsx      # Trust score display
│   │   ├── WarningIcon.tsx     # Alert icon
│   │   └── index.ts            # Barrel export
│   ├── features/           # Feature-specific components
│   │   └── dashboard/
│   │       ├── RecentIncidents.tsx
│   │       ├── RiskTrendChart.tsx
│   │       └── index.ts
│   └── layout/             # Layout components
│       ├── Header.tsx          # App header with navigation
│       ├── MainLayout.tsx      # Page wrapper
│       └── index.ts
│
├── context/                # React Context providers
│   └── ThemeContext.tsx        # Dark/light theme management
│
├── data/                   # Mock data (development)
│   ├── dashboard.ts            # Dashboard metrics & trends
│   ├── meetings.ts             # Meeting records
│   ├── participants.ts         # Participant data
│   ├── user.ts                 # User profile & FAQ
│   └── index.ts                # Barrel export
│
├── hooks/                  # Custom React hooks
│   └── (ready for implementation)
│
├── mocks/                  # MSW mock handlers
│   └── (ready for implementation)
│
├── pages/                  # Page components (routes)
│   ├── Dashboard/
│   │   ├── DashboardPage.tsx
│   │   └── index.ts
│   ├── Meetings/
│   │   ├── MeetingsPage.tsx
│   │   ├── MeetingDetailPage.tsx
│   │   └── index.ts
│   ├── Participants/
│   │   ├── ParticipantsPage.tsx
│   │   ├── ParticipantProfilePage.tsx
│   │   └── index.ts
│   ├── Settings/
│   │   ├── SettingsPage.tsx
│   │   └── index.ts
│   ├── Profile/
│   │   ├── ProfilePage.tsx
│   │   └── index.ts
│   └── Support/
│       ├── SupportPage.tsx
│       ├── ArticlePage.tsx
│       └── index.ts
│
├── services/               # API services
│   └── (ready for backend integration)
│
├── store/                  # Redux store
│   └── slices/             # Redux slices
│       └── (ready for implementation)
│
├── theme/                  # Theming
│   ├── colors.ts               # Color palette definitions
│   ├── gradients.ts            # Gradient definitions
│   └── theme.ts                # MUI theme configuration
│
├── types/                  # TypeScript types
│   ├── api.types.ts            # API response types
│   ├── meeting.types.ts        # Meeting-related types
│   ├── participant.types.ts    # Participant types
│   └── index.ts                # Barrel export
│
├── App.tsx                 # Main app with routing
├── main.tsx                # Application entry point
└── index.css               # Global styles
```

---

## Component Architecture

### Component Hierarchy

```
App
└── ThemeContextProvider
    └── BrowserRouter
        └── MainLayout
            ├── Header
            │   ├── Navigation
            │   ├── SearchBar
            │   ├── NotificationBell
            │   ├── ThemeToggle
            │   └── UserMenu
            └── Page Content
                ├── DashboardPage
                │   ├── MetricCard (x6)
                │   ├── RiskTrendChart
                │   └── RecentIncidents
                ├── MeetingsPage
                │   ├── FilterControls
                │   ├── MeetingTable
                │   └── Pagination
                └── ... (other pages)
```

### Component Patterns

**Page Components** (`src/pages/`)
- One directory per page/feature
- Main component + index.ts for exports
- Handle data fetching and state
- Compose smaller components

```tsx
// Example: DashboardPage.tsx
export const DashboardPage: React.FC = () => {
  const [dateRange, setDateRange] = useState<DateRange>(...);

  return (
    <Box>
      <Typography variant="h4">Dashboard</Typography>
      <Grid container spacing={3}>
        <MetricCard ... />
        <RiskTrendChart ... />
        <RecentIncidents ... />
      </Grid>
    </Box>
  );
};
```

**Common Components** (`src/components/common/`)
- Reusable across multiple pages
- Props-driven, no internal state
- Follow MUI patterns

```tsx
// Example: RiskBadge.tsx
interface RiskBadgeProps {
  level: RiskCategory;
  size?: 'small' | 'medium' | 'large';
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, size = 'medium' }) => {
  const color = getRiskColor(level);
  return <Chip label={level} color={color} size={size} />;
};
```

**Layout Components** (`src/components/layout/`)
- Structural components
- Handle navigation and page structure
- Provide consistent layout

---

## State Management

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      State Management                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │  Redux Toolkit  │  │  React Query    │  │   Context   │ │
│  │                 │  │                 │  │             │ │
│  │  • Auth state   │  │  • API data     │  │  • Theme    │ │
│  │  • UI state     │  │  • Caching      │  │  • Locale   │ │
│  │  • Preferences  │  │  • Pagination   │  │             │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Redux Toolkit (Global State)

Located in `src/store/`:
- Application-wide state
- User authentication
- UI preferences
- Feature flags

```tsx
// Example slice structure (to be implemented)
// src/store/slices/authSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
}

const authSlice = createSlice({
  name: 'auth',
  initialState: { user: null, isAuthenticated: false },
  reducers: {
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
      state.isAuthenticated = true;
    },
    logout: (state) => {
      state.user = null;
      state.isAuthenticated = false;
    },
  },
});
```

### React Query (Server State)

For API data fetching and caching:
- Automatic caching (5-minute stale time)
- Background refetching
- Pagination support
- Optimistic updates

```tsx
// Example query hook (to be implemented)
// src/hooks/useMeetings.ts
export const useMeetings = (filters: MeetingFilters) => {
  return useQuery({
    queryKey: ['meetings', filters],
    queryFn: () => meetingsService.getAll(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};
```

### React Context (UI State)

Theme context in `src/context/ThemeContext.tsx`:
- Dark/light mode toggle
- Persists to localStorage
- Provides theme to MUI

```tsx
interface ThemeContextType {
  mode: 'light' | 'dark';
  toggleTheme: () => void;
}

export const ThemeContext = createContext<ThemeContextType>(...);
```

---

## Data Flow

### Current (Mock Data)

```
Component → imports → data/*.ts → renders
```

Mock data files provide static data for development:
- `dashboard.ts` - Metrics, trends, incidents
- `meetings.ts` - Full meeting records with forensics
- `participants.ts` - User profiles with threat intel
- `user.ts` - Current user, FAQ, system status

### Future (API Integration)

```
Component → useQuery hook → service → API → Backend
                ↓
           React Query Cache
```

Services directory (`src/services/`) will contain:
- `api.ts` - Axios instance with interceptors
- `meetings.service.ts` - Meeting API calls
- `participants.service.ts` - Participant API calls
- `auth.service.ts` - Authentication API calls

---

## Routing

### Route Configuration

Defined in `src/App.tsx`:

```tsx
<Routes>
  <Route path="/" element={<Navigate to="/dashboard" replace />} />
  <Route path="/dashboard" element={<DashboardPage />} />
  <Route path="/meetings" element={<MeetingsPage />} />
  <Route path="/meetings/:meetingId" element={<MeetingDetailPage />} />
  <Route path="/participants" element={<ParticipantsPage />} />
  <Route path="/participants/:participantId" element={<ParticipantProfilePage />} />
  <Route path="/settings" element={<SettingsPage />} />
  <Route path="/profile" element={<ProfilePage />} />
  <Route path="/support" element={<SupportPage />} />
  <Route path="/support/articles/:articleId" element={<ArticlePage />} />
</Routes>
```

### Route Parameters

| Route | Parameters | Usage |
|-------|------------|-------|
| `/meetings/:meetingId` | `meetingId` | View specific meeting |
| `/participants/:participantId` | `participantId` | View participant profile |
| `/support/articles/:articleId` | `articleId` | View help article |

### Navigation

Programmatic navigation using `useNavigate`:

```tsx
const navigate = useNavigate();
navigate('/meetings/12345');
navigate(-1); // Go back
```

---

## Theming System

### Theme Structure

Located in `src/theme/`:

```
theme/
├── colors.ts      # Color palette constants
├── gradients.ts   # Gradient definitions
└── theme.ts       # MUI theme configuration
```

### Color Palette (`colors.ts`)

```typescript
export const colors = {
  brand: {
    deepSafeBlue: '#1F3C88',    // Primary
    signalTeal: '#1FB6A6',       // Secondary
    alertAmber: '#F5A623',       // Warning
    threatRed: '#D64545',        // Error
  },
  dark: {
    background: {
      deepest: '#05070C',
      primary: '#0B1220',
      surface: '#121C2E',
      elevated: '#1A2740',
    },
    // ... text, border colors
  },
  light: {
    background: {
      primary: '#F7F9FC',
      surface: '#FFFFFF',
      // ...
    },
  },
};
```

### Theme Configuration (`theme.ts`)

Creates MUI theme based on mode:

```typescript
export const createAppTheme = (mode: 'light' | 'dark') => createTheme({
  palette: {
    mode,
    primary: { main: colors.brand.deepSafeBlue },
    secondary: { main: colors.brand.signalTeal },
    // ...
  },
  typography: {
    fontFamily: '"Inter", sans-serif',
    h1: { fontFamily: '"Space Grotesk", sans-serif' },
    // ...
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: { borderRadius: 12 },
      },
    },
    // ... component overrides
  },
});
```

### Using Theme

Access theme in components:

```tsx
import { useTheme } from '@mui/material';

const MyComponent = () => {
  const theme = useTheme();
  return (
    <Box sx={{
      color: theme.palette.primary.main,
      bgcolor: theme.palette.background.paper,
    }}>
      ...
    </Box>
  );
};
```

---

## Type System

### Core Types (`src/types/`)

**Meeting Types (`meeting.types.ts`):**
```typescript
export type RiskCategory = 'low' | 'medium' | 'high' | 'critical';

export interface Meeting {
  id: string;
  name: string;
  date: string;
  duration: number;
  platform: 'zoom' | 'meet' | 'teams' | 'webex';
  host: MeetingParticipant;
  participants: MeetingParticipant[];
  riskScore: number;
  riskCategory: RiskCategory;
  riskBreakdown: RiskBreakdown;
  incidents: Incident[];
  timeline: TimelineEvent[];
  transcript: TranscriptEntry[];
  forensicEvidence: ForensicEvidence;
}

export interface ForensicEvidence {
  video: VideoAnalysis;
  audio: AudioAnalysis;
  network: NetworkAnalysis;
  behavioral: BehavioralAnalysis;
}
```

**Participant Types (`participant.types.ts`):**
```typescript
export type ParticipantStatus =
  | 'verified'
  | 'guest'
  | 'external'
  | 'flagged'
  | 'blacklisted';

export interface Participant {
  id: string;
  name: string;
  email: string;
  status: ParticipantStatus;
  trustScore: number;
  riskLevel: RiskCategory;
  threatIntelligence: ThreatIntelligence;
  verificationDetails: VerificationDetails;
  meetingHistory: ParticipantMeetingHistory[];
}
```

**API Types (`api.types.ts`):**
```typescript
export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}
```

---

## API Integration

### Prepared Structure

```
src/services/
├── api.ts              # Axios instance
├── meetings.service.ts  # Meeting endpoints
├── participants.service.ts
├── auth.service.ts
└── index.ts
```

### Axios Configuration (to implement)

```typescript
// src/services/api.ts
import axios from 'axios';

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
    }
    return Promise.reject(error);
  }
);
```

### Service Example (to implement)

```typescript
// src/services/meetings.service.ts
import { api } from './api';
import { Meeting, MeetingFilters, PaginatedResponse } from '../types';

export const meetingsService = {
  getAll: async (filters: MeetingFilters): Promise<PaginatedResponse<Meeting>> => {
    const { data } = await api.get('/meetings', { params: filters });
    return data;
  },

  getById: async (id: string): Promise<Meeting> => {
    const { data } = await api.get(`/meetings/${id}`);
    return data;
  },
};
```

---

## Build & Development

### Development Server

```bash
npm run dev
```

- Runs Vite dev server on `http://localhost:5173`
- Hot Module Replacement (HMR) enabled
- Fast refresh for React components

### Production Build

```bash
npm run build
```

1. TypeScript compilation (`tsc -b`)
2. Vite production bundle
3. Output to `dist/` directory

### Preview Production

```bash
npm run preview
```

Serves the `dist/` folder locally for testing.

### Linting

```bash
npm run lint
```

Runs ESLint with TypeScript rules.

### Environment Variables

Create `.env` file:

```env
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws
```

Access in code:
```typescript
const apiUrl = import.meta.env.VITE_API_URL;
```

---

## Adding New Features

### Adding a New Page

1. Create directory in `src/pages/NewPage/`
2. Create `NewPage.tsx` component
3. Create `index.ts` barrel export
4. Add route in `src/App.tsx`
5. Add navigation in `src/components/layout/Header.tsx`

### Adding a New Component

1. Determine location (common, features, layout)
2. Create component file
3. Add to directory's `index.ts`
4. Use MUI components and theme tokens

### Adding a New Type

1. Add to appropriate file in `src/types/`
2. Export from `src/types/index.ts`
3. Import where needed

### Adding a New API Service

1. Create service file in `src/services/`
2. Define methods using `api` instance
3. Create corresponding React Query hook
4. Use in components

---

## Best Practices

### Component Guidelines

- Use functional components with hooks
- Prefer composition over inheritance
- Keep components focused (single responsibility)
- Extract reusable logic into custom hooks
- Use TypeScript strictly (no `any`)

### Styling Guidelines

- Use MUI `sx` prop for one-off styles
- Use theme tokens for colors/spacing
- Create reusable styled components for complex patterns
- Follow responsive design patterns

### Performance Guidelines

- Memoize expensive computations with `useMemo`
- Memoize callbacks with `useCallback`
- Use React Query for data fetching
- Implement pagination for large lists
- Lazy load routes/components where appropriate
