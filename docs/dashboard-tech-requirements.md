# **Part 2: Dashboard Technical Requirements {\#dashboard-tech-requirements}**

## **1\. Dashboard Architecture**

### **1.1 Frontend Architecture Overview**

┌─────────────────────────────────────────────────────────────────┐  
│                        CLIENT BROWSER                           │  
├─────────────────────────────────────────────────────────────────┤  
│                                                                 │  
│  ┌───────────────────────────────────────────────────────────┐ │  
│  │              React Application Layer                      │ │  
│  │                                                           │ │  
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │ │  
│  │  │   Pages     │  │ Components  │  │   Hooks     │      │ │  
│  │  │             │  │             │  │             │      │ │  
│  │  │ • Summary   │  │ • DataGrid  │  │ • useAuth   │      │ │  
│  │  │ • Meetings  │  │ • Charts    │  │ • useAPI    │      │ │  
│  │  │ • Incidents │  │ • Modals    │  │ • useWebSocket     │ │  
│  │  │ • Settings  │  │ • Forms     │  │             │      │ │  
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │ │  
│  │                                                           │ │  
│  └───────────────────────────────────────────────────────────┘ │  
│                             │                                   │  
│  ┌───────────────────────────────────────────────────────────┐ │  
│  │              State Management Layer                       │ │  
│  │                                                           │ │  
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │ │  
│  │  │   Redux     │  │   React     │  │   React     │      │ │  
│  │  │   Toolkit   │  │   Query     │  │   Context   │      │ │  
│  │  │             │  │             │  │             │      │ │  
│  │  │ • Global    │  │ • Server    │  │ • Theme     │      │ │  
│  │  │   state     │  │   state     │  │ • User prefs│      │ │  
│  │  │ • Auth      │  │ • Cache     │  │ • Locale    │      │ │  
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │ │  
│  │                                                           │ │  
│  └───────────────────────────────────────────────────────────┘ │  
│                             │                                   │  
│  ┌───────────────────────────────────────────────────────────┐ │  
│  │              Data/API Layer                               │ │  
│  │                                                           │ │  
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │ │  
│  │  │   Axios     │  │  WebSocket  │  │   GraphQL   │      │ │  
│  │  │   Client    │  │   Client    │  │   Client    │      │ │  
│  │  │             │  │             │  │             │      │ │  
│  │  │ • REST API  │  │ • Real-time │  │ • Optional  │      │ │  
│  │  │ • Interceptors  │   updates   │  │   queries   │      │ │  
│  │  │ • Retry logic│  │ • Auto-    │  │             │      │ │  
│  │  │             │  │   reconnect │  │             │      │ │  
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │ │  
│  │                                                           │ │  
│  └───────────────────────────────────────────────────────────┘ │  
│                                                                 │  
└─────────────────────────────┬───────────────────────────────────┘  
                              │  
                              │ HTTPS / WSS  
                              │  
┌─────────────────────────────┼───────────────────────────────────┐  
│                       CDN LAYER                                 │  
│                    (CloudFlare)                                 │  
│                                                                 │  
│  • Static asset caching                                        │  
│  • DDoS protection                                             │  
│  • SSL/TLS termination                                         │  
│  • Geographic distribution                                     │  
│                                                                 │  
└─────────────────────────────┬───────────────────────────────────┘  
                              │  
┌─────────────────────────────┼───────────────────────────────────┐  
│                    BACKEND API                                  │  
│                 (From Part 1\)                                   │  
└─────────────────────────────────────────────────────────────────┘

---

## **2\. Technology Stack**

### **2.1 Core Technologies**

Framework & Build:  
  Framework: React 18.2+  
  Language: TypeScript 5.0+  
  Build Tool: Vite 5.0+ (or Next.js 14+ for SSR)  
  Package Manager: pnpm 8.0+  
    
Routing:  
  Library: React Router v6  
  Features:  
    \- Code splitting per route  
    \- Protected routes  
    \- Nested routing  
    \- Query parameter management  
    
UI Component Library:  
  Base: Material-UI (MUI) v5  
  Alternatives: Ant Design, Chakra UI  
  Custom components: Built on top of base library  
    
Styling:  
  Primary: Emotion (CSS-in-JS) \- comes with MUI  
  Alternative: Tailwind CSS 3.0+  
  Theme: Custom theme system with dark/light modes

### **2.2 State Management**

Global State:  
  Library: Redux Toolkit 2.0+  
  Middleware: redux-thunk (included)  
  DevTools: Redux DevTools Extension  
    
Server State:  
  Library: TanStack Query (React Query) v5  
  Features:  
    \- Automatic caching  
    \- Background refetching  
    \- Optimistic updates  
    \- Infinite scrolling  
    \- Pagination  
  Cache time: 5 minutes  
  Stale time: 1 minute  
    
Form State:  
  Library: React Hook Form v7  
  Validation: Zod schema validation  
    
Real-time State:  
  WebSocket: Socket.IO client v4  
  Fallback: Long polling  
  Auto-reconnect: Exponential backoff

### **2.3 Data Visualization**

Charts & Graphs:  
  Library: Recharts 2.5+ or Apache ECharts  
  Chart Types:  
    \- Line charts (risk trends)  
    \- Bar charts (incident types)  
    \- Pie charts (risk distribution)  
    \- Area charts (cumulative metrics)  
    \- Heatmaps (activity patterns)  
    
Real-time Updates:  
  \- Live data streaming to charts  
  \- Smooth animations  
  \- Auto-scaling axes  
    
Tables:  
  Library: TanStack Table (React Table) v8  
  Features:  
    \- Virtual scrolling (handle 10k+ rows)  
    \- Sorting (client & server side)  
    \- Filtering (multi-column)  
    \- Column resizing  
    \- Column hiding  
    \- Export to CSV/Excel

### **2.4 Utilities & Helpers**

Date/Time:  
  Library: date-fns 2.30+ or dayjs  
  Timezone: date-fns-tz  
  Formatting: Locale-aware  
    
HTTP Client:  
  Library: axios 1.6+  
  Features:  
    \- Interceptors (auth token injection)  
    \- Request cancellation  
    \- Retry logic (exponential backoff)  
    \- Response caching  
    
Notifications:  
  Library: react-hot-toast or notistack  
  Types: success, error, warning, info  
  Position: Top-right (configurable)  
  Duration: 5 seconds (auto-dismiss)  
    
File Handling:  
  Upload: react-dropzone  
  Download: file-saver  
  Preview: react-pdf-viewer  
    
Internationalization:  
  Library: react-i18next  
  Languages: English (default), Spanish, French, German, Japanese  
  Fallback: English

---

## **3\. Component Architecture**

### **3.1 Component Hierarchy**

src/  
├── components/  
│   ├── common/                    \# Reusable components  
│   │   ├── Button/  
│   │   │   ├── Button.tsx  
│   │   │   ├── Button.test.tsx  
│   │   │   ├── Button.stories.tsx  
│   │   │   └── index.ts  
│   │   ├── Input/  
│   │   ├── Modal/  
│   │   ├── Card/  
│   │   ├── Badge/  
│   │   ├── Alert/  
│   │   ├── Tooltip/  
│   │   └── Loader/  
│   │  
│   ├── layout/                    \# Layout components  
│   │   ├── Header/  
│   │   │   ├── Header.tsx  
│   │   │   ├── NotificationBell.tsx  
│   │   │   └── UserMenu.tsx  
│   │   ├── Sidebar/  
│   │   │   ├── Sidebar.tsx  
│   │   │   └── NavigationMenu.tsx  
│   │   ├── Footer/  
│   │   └── MainLayout/  
│   │  
│   ├── features/                  \# Feature-specific components  
│   │   ├── meetings/  
│   │   │   ├── MeetingList/  
│   │   │   ├── MeetingDetail/  
│   │   │   ├── MeetingCard/  
│   │   │   ├── RiskIndicator/  
│   │   │   ├── TrustBadge/  
│   │   │   └── TranscriptViewer/  
│   │   │  
│   │   ├── incidents/  
│   │   │   ├── IncidentList/  
│   │   │   ├── IncidentDetail/  
│   │   │   ├── IncidentTimeline/  
│   │   │   ├── ForensicViewer/  
│   │   │   └── VerificationStatus/  
│   │   │  
│   │   ├── participants/  
│   │   │   ├── ParticipantList/  
│   │   │   ├── ParticipantProfile/  
│   │   │   ├── ParticipantCard/  
│   │   │   └── BlacklistManager/  
│   │   │  
│   │   ├── dashboard/  
│   │   │   ├── MetricCard/  
│   │   │   ├── RiskTrendChart/  
│   │   │   ├── RecentIncidents/  
│   │   │   └── QuickActions/  
│   │   │  
│   │   └── alerts/  
│   │       ├── AlertBanner/  
│   │       ├── RealTimeAlert/  
│   │       └── NotificationCenter/  
│   │  
│   └── charts/                    \# Chart components  
│       ├── LineChart/  
│       ├── BarChart/  
│       ├── PieChart/  
│       ├── AreaChart/  
│       └── HeatMap/  
│  
├── pages/                         \# Page components  
│   ├── Dashboard/  
│   │   └── DashboardPage.tsx  
│   ├── Meetings/  
│   │   ├── MeetingsPage.tsx  
│   │   └── MeetingDetailPage.tsx  
│   ├── Incidents/  
│   │   ├── IncidentsPage.tsx  
│   │   └── IncidentDetailPage.tsx  
│   ├── Participants/  
│   │   ├── ParticipantsPage.tsx  
│   │   └── ParticipantProfilePage.tsx  
│   ├── Settings/  
│   │   └── SettingsPage.tsx  
│   └── Auth/  
│       ├── LoginPage.tsx  
│       └── SSOCallbackPage.tsx  
│  
├── hooks/                         \# Custom React hooks  
│   ├── useAuth.ts  
│   ├── useAPI.ts  
│   ├── useWebSocket.ts  
│   ├── usePagination.ts  
│   ├── useFilters.ts  
│   ├── useExport.ts  
│   └── useRealTimeAlerts.ts  
│  
├── store/                         \# Redux store  
│   ├── index.ts  
│   ├── slices/  
│   │   ├── authSlice.ts  
│   │   ├── uiSlice.ts  
│   │   ├── filtersSlice.ts  
│   │   └── alertsSlice.ts  
│   └── middleware/  
│       └── apiMiddleware.ts  
│  
├── services/                      \# API services  
│   ├── api.ts                     \# Axios instance  
│   ├── meetingsAPI.ts  
│   ├── incidentsAPI.ts  
│   ├── participantsAPI.ts  
│   ├── authAPI.ts  
│   └── websocket.ts  
│  
├── utils/                         \# Utility functions  
│   ├── formatters.ts  
│   ├── validators.ts  
│   ├── constants.ts  
│   └── helpers.ts  
│  
├── types/                         \# TypeScript types  
│   ├── meeting.types.ts  
│   ├── incident.types.ts  
│   ├── participant.types.ts  
│   ├── api.types.ts  
│   └── common.types.ts  
│  
├── assets/                        \# Static assets  
│   ├── images/  
│   ├── icons/  
│   └── fonts/  
│  
└── styles/                        \# Global styles  
    ├── theme.ts  
    ├── globals.css  
    └── variables.css

### **3.2 Key Component Specifications**

#### **TrustBadge Component**

// components/features/meetings/TrustBadge/TrustBadge.tsx

import React from 'react';  
import { Tooltip, Badge, Box } from '@mui/material';  
import {   
  CheckCircle,   
  Warning,   
  Error,   
  Help   
} from '@mui/icons-material';

export type TrustLevel \= 'verified' | 'partial' | 'high-risk' | 'external';

interface TrustBadgeProps {  
  level: TrustLevel;  
  score?: number; // 0-100  
  tooltip?: string;  
  size?: 'small' | 'medium' | 'large';  
  showScore?: boolean;  
}

const TrustBadge: React.FC\<TrustBadgeProps\> \= ({  
  level,  
  score,  
  tooltip,  
  size \= 'medium',  
  showScore \= false  
}) \=\> {  
  const config \= {  
    verified: {  
      color: 'success',  
      icon: \<CheckCircle /\>,  
      label: 'Verified & Trusted',  
      bgColor: '\#4caf50'  
    },  
    partial: {  
      color: 'warning',  
      icon: \<Warning /\>,  
      label: 'Partially Verified',  
      bgColor: '\#ff9800'  
    },  
    'high-risk': {  
      color: 'error',  
      icon: \<Error /\>,  
      label: 'High Risk / Unverified',  
      bgColor: '\#f44336'  
    },  
    external: {  
      color: 'default',  
      icon: \<Help /\>,  
      label: 'External / Guest',  
      bgColor: '\#9e9e9e'  
    }  
  }\[level\];

  const sizeConfig \= {  
    small: 20,  
    medium: 28,  
    large: 36  
  }\[size\];

  return (  
    \<Tooltip title={tooltip || config.label} arrow\>  
      \<Box  
        sx={{  
          display: 'inline-flex',  
          alignItems: 'center',  
          gap: 0.5  
        }}  
      \>  
        \<Badge  
          sx={{  
            '& .MuiBadge-badge': {  
              backgroundColor: config.bgColor,  
              width: sizeConfig,  
              height: sizeConfig,  
              borderRadius: '50%',  
              display: 'flex',  
              alignItems: 'center',  
              justifyContent: 'center'  
            }  
          }}  
        \>  
          {React.cloneElement(config.icon, {  
            sx: { fontSize: sizeConfig \* 0.7, color: 'white' }  
          })}  
        \</Badge\>  
        {showScore && score \!== undefined && (  
          \<Box  
            component="span"  
            sx={{  
              fontSize: size \=== 'small' ? '0.75rem' : '0.875rem',  
              fontWeight: 500,  
              color: 'text.secondary'  
            }}  
          \>  
            {score}%  
          \</Box\>  
        )}  
      \</Box\>  
    \</Tooltip\>  
  );  
};

export default TrustBadge;

#### **RiskIndicator Component**

// components/features/meetings/RiskIndicator/RiskIndicator.tsx

import React from 'react';  
import { Box, LinearProgress, Typography } from '@mui/material';

interface RiskIndicatorProps {  
  score: number; // 0-100  
  category: 'low' | 'medium' | 'high' | 'critical';  
  showLabel?: boolean;  
  showPercentage?: boolean;  
  size?: 'small' | 'medium' | 'large';  
}

const RiskIndicator: React.FC\<RiskIndicatorProps\> \= ({  
  score,  
  category,  
  showLabel \= true,  
  showPercentage \= true,  
  size \= 'medium'  
}) \=\> {  
  const getColor \= (score: number): string \=\> {  
    if (score \>= 86\) return '\#f44336'; // Critical \- Red  
    if (score \>= 61\) return '\#ff9800'; // High \- Orange  
    if (score \>= 31\) return '\#ffc107'; // Medium \- Yellow  
    return '\#4caf50'; // Low \- Green  
  };

  const getCategoryLabel \= (category: string): string \=\> {  
    return {  
      low: 'Low Risk',  
      medium: 'Medium Risk',  
      high: 'High Risk',  
      critical: 'Critical Risk'  
    }\[category\] || 'Unknown';  
  };

  const heightMap \= {  
    small: 6,  
    medium: 8,  
    large: 10  
  };

  return (  
    \<Box sx={{ width: '100%', minWidth: 150 }}\>  
      \<Box  
        sx={{  
          display: 'flex',  
          justifyContent: 'space-between',  
          alignItems: 'center',  
          mb: 0.5  
        }}  
      \>  
        {showLabel && (  
          \<Typography  
            variant={size \=== 'small' ? 'caption' : 'body2'}  
            sx={{ fontWeight: 500, color: 'text.secondary' }}  
          \>  
            Risk Level: {getCategoryLabel(category)}  
          \</Typography\>  
        )}  
        {showPercentage && (  
          \<Typography  
            variant={size \=== 'small' ? 'caption' : 'body2'}  
            sx={{ fontWeight: 600, color: getColor(score) }}  
          \>  
            {score}%  
          \</Typography\>  
        )}  
      \</Box\>  
      \<LinearProgress  
        variant="determinate"  
        value={score}  
        sx={{  
          height: heightMap\[size\],  
          borderRadius: 1,  
          backgroundColor: 'rgba(0, 0, 0, 0.1)',  
          '& .MuiLinearProgress-bar': {  
            backgroundColor: getColor(score),  
            borderRadius: 1  
          }  
        }}  
      /\>  
      {size \!== 'small' && (  
        \<Box  
          sx={{  
            display: 'flex',  
            justifyContent: 'space-between',  
            mt: 0.5  
          }}  
        \>  
          \<Typography variant="caption" color="text.secondary"\>  
            0%  
          \</Typography\>  
          \<Typography variant="caption" color="text.secondary"\>  
            Safe  
          \</Typography\>  
          \<Typography variant="caption" color="text.secondary"\>  
            Critical  
          \</Typography\>  
          \<Typography variant="caption" color="text.secondary"\>  
            100%  
          \</Typography\>  
        \</Box\>  
      )}  
    \</Box\>  
  );  
};

export default RiskIndicator;

#### **MetricCard Component**

// components/features/dashboard/MetricCard/MetricCard.tsx

import React from 'react';  
import { Card, CardContent, Typography, Box, Skeleton } from '@mui/material';  
import { TrendingUp, TrendingDown, TrendingFlat } from '@mui/icons-material';

interface MetricCardProps {  
  title: string;  
  value: number | string;  
  subtitle?: string;  
  trend?: {  
    value: number;  
    direction: 'up' | 'down' | 'flat';  
    label?: string;  
  };  
  icon?: React.ReactNode;  
  isLoading?: boolean;  
  onClick?: () \=\> void;  
  alert?: boolean;  
}

const MetricCard: React.FC\<MetricCardProps\> \= ({  
  title,  
  value,  
  subtitle,  
  trend,  
  icon,  
  isLoading \= false,  
  onClick,  
  alert \= false  
}) \=\> {  
  const getTrendIcon \= (direction: string) \=\> {  
    const iconProps \= {   
      fontSize: 'small' as const,  
      sx: {   
        color: direction \=== 'up' ? 'success.main' :   
               direction \=== 'down' ? 'error.main' :   
               'text.secondary'   
      }  
    };  
      
    switch (direction) {  
      case 'up': return \<TrendingUp {...iconProps} /\>;  
      case 'down': return \<TrendingDown {...iconProps} /\>;  
      default: return \<TrendingFlat {...iconProps} /\>;  
    }  
  };

  return (  
    \<Card  
      sx={{  
        height: '100%',  
        cursor: onClick ? 'pointer' : 'default',  
        transition: 'all 0.3s ease',  
        border: alert ? '2px solid' : '1px solid',  
        borderColor: alert ? 'error.main' : 'divider',  
        '&:hover': onClick ? {  
          boxShadow: 4,  
          transform: 'translateY(-2px)'  
        } : {}  
      }}  
      onClick={onClick}  
    \>  
      \<CardContent\>  
        \<Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}\>  
          \<Typography  
            variant="subtitle2"  
            color="text.secondary"  
            sx={{ fontWeight: 500 }}  
          \>  
            {title}  
          \</Typography\>  
          {icon && (  
            \<Box sx={{ color: 'primary.main' }}\>  
              {icon}  
            \</Box\>  
          )}  
        \</Box\>

        {isLoading ? (  
          \<\>  
            \<Skeleton variant="text" width="60%" height={40} /\>  
            \<Skeleton variant="text" width="40%" /\>  
          \</\>  
        ) : (  
          \<\>  
            \<Typography  
              variant="h3"  
              sx={{  
                fontWeight: 700,  
                mb: 1,  
                color: alert ? 'error.main' : 'text.primary'  
              }}  
            \>  
              {value}  
            \</Typography\>

            {subtitle && (  
              \<Typography variant="body2" color="text.secondary"\>  
                {subtitle}  
              \</Typography\>  
            )}

            {trend && (  
              \<Box  
                sx={{  
                  display: 'flex',  
                  alignItems: 'center',  
                  gap: 0.5,  
                  mt: 1  
                }}  
              \>  
                {getTrendIcon(trend.direction)}  
                \<Typography  
                  variant="caption"  
                  sx={{  
                    color: trend.direction \=== 'up' ? 'success.main' :   
                           trend.direction \=== 'down' ? 'error.main' :   
                           'text.secondary',  
                    fontWeight: 500  
                  }}  
                \>  
                  {trend.value \> 0 ? '+' : ''}{trend.value}  
                  {trend.label && \` ${trend.label}\`}  
                \</Typography\>  
              \</Box\>  
            )}  
          \</\>  
        )}  
      \</CardContent\>  
    \</Card\>  
  );  
};

export default MetricCard;

---

## **4\. State Management Architecture**

### **4.1 Redux Store Structure**

// store/index.ts

import { configureStore } from '@reduxjs/toolkit';  
import { setupListeners } from '@reduxjs/toolkit/query';  
import authReducer from './slices/authSlice';  
import uiReducer from './slices/uiSlice';  
import filtersReducer from './slices/filtersSlice';  
import alertsReducer from './slices/alertsSlice';  
import { apiSlice } from './api/apiSlice';

export const store \= configureStore({  
  reducer: {  
    auth: authReducer,  
    ui: uiReducer,  
    filters: filtersReducer,  
    alerts: alertsReducer,  
    \[apiSlice.reducerPath\]: apiSlice.reducer,  
  },  
  middleware: (getDefaultMiddleware) \=\>  
    getDefaultMiddleware().concat(apiSlice.middleware),  
  devTools: process.env.NODE\_ENV \!== 'production',  
});

setupListeners(store.dispatch);

export type RootState \= ReturnType\<typeof store.getState\>;  
export type AppDispatch \= typeof store.dispatch;

### **4.2 Auth Slice**

// store/slices/authSlice.ts

import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface User {  
  id: string;  
  email: string;  
  name: string;  
  role: string;  
  company\_id: string;  
  company\_name: string;  
}

interface AuthState {  
  user: User | null;  
  token: string | null;  
  isAuthenticated: boolean;  
  isLoading: boolean;  
  error: string | null;  
}

const initialState: AuthState \= {  
  user: null,  
  token: localStorage.getItem('deepsafe\_token'),  
  isAuthenticated: false,  
  isLoading: true,  
  error: null,  
};

const authSlice \= createSlice({  
  name: 'auth',  
  initialState,  
  reducers: {  
    setCredentials: (  
      state,  
      action: PayloadAction\<{ user: User; token: string }\>  
    ) \=\> {  
      state.user \= action.payload.user;  
      state.token \= action.payload.token;  
      state.isAuthenticated \= true;  
      state.isLoading \= false;  
      localStorage.setItem('deepsafe\_token', action.payload.token);  
    },  
    logout: (state) \=\> {  
      state.user \= null;  
      state.token \= null;  
      state.isAuthenticated \= false;  
      localStorage.removeItem('deepsafe\_token');  
    },  
    setAuthLoading: (state, action: PayloadAction\<boolean\>) \=\> {  
      state.isLoading \= action.payload;  
    },  
    setAuthError: (state, action: PayloadAction\<string\>) \=\> {  
      state.error \= action.payload;  
      state.isLoading \= false;  
    },  
  },  
});

export const { setCredentials, logout, setAuthLoading, setAuthError } \=   
  authSlice.actions;

export default authSlice.reducer;

### **4.3 UI Slice**

// store/slices/uiSlice.ts

import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface UIState {  
  theme: 'light' | 'dark';  
  sidebarOpen: boolean;  
  notificationsPanelOpen: boolean;  
  activeFilters: Record\<string, any\>;  
  dateRange: {  
    start: string | null;  
    end: string | null;  
  };  
}

const initialState: UIState \= {  
  theme: (localStorage.getItem('theme') as 'light' | 'dark') || 'light',  
  sidebarOpen: true,  
  notificationsPanelOpen: false,  
  activeFilters: {},  
  dateRange: {  
    start: null,  
    end: null,  
  },  
};

const uiSlice \= createSlice({  
  name: 'ui',  
  initialState,  
  reducers: {  
    toggleTheme: (state) \=\> {  
      state.theme \= state.theme \=== 'light' ? 'dark' : 'light';  
      localStorage.setItem('theme', state.theme);  
    },  
    toggleSidebar: (state) \=\> {  
      state.sidebarOpen \= \!state.sidebarOpen;  
    },  
    toggleNotificationsPanel: (state) \=\> {  
      state.notificationsPanelOpen \= \!state.notificationsPanelOpen;  
    },  
    setDateRange: (  
      state,  
      action: PayloadAction\<{ start: string | null; end: string | null }\>  
    ) \=\> {  
      state.dateRange \= action.payload;  
    },  
    setFilter: (  
      state,  
      action: PayloadAction\<{ key: string; value: any }\>  
    ) \=\> {  
      state.activeFilters\[action.payload.key\] \= action.payload.value;  
    },  
    clearFilters: (state) \=\> {  
      state.activeFilters \= {};  
    },  
  },  
});

export const {  
  toggleTheme,  
  toggleSidebar,  
  toggleNotificationsPanel,  
  setDateRange,  
  setFilter,  
  clearFilters,  
} \= uiSlice.actions;

export default uiSlice.reducer;

### **4.4 React Query Configuration**

// services/queryClient.ts

import { QueryClient } from '@tanstack/react-query';

export const queryClient \= new QueryClient({  
  defaultOptions: {  
    queries: {  
      staleTime: 1000 \* 60 \* 1, // 1 minute  
      cacheTime: 1000 \* 60 \* 5, // 5 minutes  
      retry: 3,  
      retryDelay: (attemptIndex) \=\> Math.min(1000 \* 2 \*\* attemptIndex, 30000),  
      refetchOnWindowFocus: false,  
      refetchOnReconnect: true,  
      refetchOnMount: true,  
    },  
    mutations: {  
      retry: 1,  
    },  
  },  
});

// Query keys factory  
export const queryKeys \= {  
  meetings: {  
    all: \['meetings'\] as const,  
    lists: () \=\> \[...queryKeys.meetings.all, 'list'\] as const,  
    list: (filters: any) \=\>   
      \[...queryKeys.meetings.lists(), filters\] as const,  
    details: () \=\> \[...queryKeys.meetings.all, 'detail'\] as const,  
    detail: (id: string) \=\>   
      \[...queryKeys.meetings.details(), id\] as const,  
    transcript: (id: string) \=\>   
      \[...queryKeys.meetings.detail(id), 'transcript'\] as const,  
    forensics: (id: string) \=\>   
      \[...queryKeys.meetings.detail(id), 'forensics'\] as const,  
  },  
  incidents: {  
    all: \['incidents'\] as const,  
    lists: () \=\> \[...queryKeys.incidents.all, 'list'\] as const,  
    list: (filters: any) \=\>   
      \[...queryKeys.incidents.lists(), filters\] as const,  
    detail: (id: string) \=\>   
      \[...queryKeys.incidents.all, 'detail', id\] as const,  
  },  
  participants: {  
    all: \['participants'\] as const,  
    lists: () \=\> \[...queryKeys.participants.all, 'list'\] as const,  
    list: (filters: any) \=\>   
      \[...queryKeys.participants.lists(), filters\] as const,  
    detail: (id: string) \=\>   
      \[...queryKeys.participants.all, 'detail', id\] as const,  
  },  
  dashboard: {  
    summary: \['dashboard', 'summary'\] as const,  
    metrics: (dateRange: any) \=\>   
      \['dashboard', 'metrics', dateRange\] as const,  
  },  
};

### **4.5 Custom Hooks**

// hooks/useMeetings.ts

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';  
import { queryKeys } from '@/services/queryClient';  
import \* as meetingsAPI from '@/services/meetingsAPI';

export function useMeetings(filters: any) {  
  return useQuery({  
    queryKey: queryKeys.meetings.list(filters),  
    queryFn: () \=\> meetingsAPI.getMeetings(filters),  
    keepPreviousData: true,  
  });  
}

export function useMeeting(id: string) {  
  return useQuery({  
    queryKey: queryKeys.meetings.detail(id),  
    queryFn: () \=\> meetingsAPI.getMeeting(id),  
    enabled: \!\!id,  
  });  
}

export function useMeetingTranscript(id: string) {  
  return useQuery({  
    queryKey: queryKeys.meetings.transcript(id),  
    queryFn: () \=\> meetingsAPI.getMeetingTranscript(id),  
    enabled: \!\!id,  
  });  
}

export function useExportMeeting() {  
  const queryClient \= useQueryClient();  
    
  return useMutation({  
    mutationFn: ({   
      meetingId,   
      format   
    }: {   
      meetingId: string;   
      format: 'pdf' | 'xlsx' | 'json'   
    }) \=\> meetingsAPI.exportMeeting(meetingId, format),  
    onSuccess: () \=\> {  
      // Could trigger a notification  
      console.log('Export successful');  
    },  
  });  
}

// hooks/useRealTimeAlerts.ts

import { useEffect, useState } from 'react';  
import { useDispatch } from 'react-redux';  
import { io, Socket } from 'socket.io-client';  
import { addAlert } from '@/store/slices/alertsSlice';

interface Alert {  
  id: string;  
  type: 'info' | 'warning' | 'error' | 'critical';  
  message: string;  
  meetingId?: string;  
  incidentId?: string;  
  timestamp: string;  
}

export function useRealTimeAlerts() {  
  const dispatch \= useDispatch();  
  const \[socket, setSocket\] \= useState\<Socket | null\>(null);  
  const \[isConnected, setIsConnected\] \= useState(false);

  useEffect(() \=\> {  
    const token \= localStorage.getItem('deepsafe\_token');  
    if (\!token) return;

    const newSocket \= io(process.env.REACT\_APP\_WS\_URL\!, {  
      auth: { token },  
      transports: \['websocket', 'polling'\],  
    });

    newSocket.on('connect', () \=\> {  
      console.log('WebSocket connected');  
      setIsConnected(true);  
    });

    newSocket.on('disconnect', () \=\> {  
      console.log('WebSocket disconnected');  
      setIsConnected(false);  
    });

    newSocket.on('alert', (alert: Alert) \=\> {  
      dispatch(addAlert(alert));  
        
      // Show browser notification if permitted  
      if ('Notification' in window && Notification.permission \=== 'granted') {  
        new Notification('DeepSafe Alert', {  
          body: alert.message,  
          icon: '/logo192.png',  
          badge: '/logo192.png',  
        });  
      }  
    });

    newSocket.on('meeting\_state\_update', (data: any) \=\> {  
      // Handle real-time meeting updates  
      console.log('Meeting update:', data);  
    });

    setSocket(newSocket);

    return () \=\> {  
      newSocket.close();  
    };  
  }, \[dispatch\]);

  return { socket, isConnected };  
}

---

## **5\. API Integration**

### **5.1 Axios Configuration**

// services/api.ts

import axios, {   
  AxiosInstance,   
  AxiosError,   
  InternalAxiosRequestConfig   
} from 'axios';  
import { store } from '@/store';  
import { logout } from '@/store/slices/authSlice';

const api: AxiosInstance \= axios.create({  
  baseURL: process.env.REACT\_APP\_API\_URL || 'https://api.deepsafe.ai/v1',  
  timeout: 30000,  
  headers: {  
    'Content-Type': 'application/json',  
  },  
});

// Request interceptor \- Add auth token  
api.interceptors.request.use(  
  (config: InternalAxiosRequestConfig) \=\> {  
    const token \= store.getState().auth.token;  
    if (token && config.headers) {  
      config.headers.Authorization \= \`Bearer ${token}\`;  
    }  
    return config;  
  },  
  (error: AxiosError) \=\> {  
    return Promise.reject(error);  
  }  
);

// Response interceptor \- Handle errors  
api.interceptors.response.use(  
  (response) \=\> response,  
  async (error: AxiosError) \=\> {  
    const originalRequest \= error.config as InternalAxiosRequestConfig & {  
      \_retry?: boolean;  
    };

    // Handle 401 Unauthorized  
    if (error.response?.status \=== 401 && \!originalRequest.\_retry) {  
      originalRequest.\_retry \= true;  
        
      // Try to refresh token  
      try {  
        const refreshToken \= localStorage.getItem('deepsafe\_refresh\_token');  
        if (refreshToken) {  
          const response \= await axios.post(  
            \`${process.env.REACT\_APP\_API\_URL}/auth/refresh\`,  
            { refresh\_token: refreshToken }  
          );  
            
          const { token } \= response.data;  
          localStorage.setItem('deepsafe\_token', token);  
            
          // Retry original request with new token  
          originalRequest.headers\!.Authorization \= \`Bearer ${token}\`;  
          return api(originalRequest);  
        }  
      } catch (refreshError) {  
        // Refresh failed, logout user  
        store.dispatch(logout());  
        window.location.href \= '/login';  
        return Promise.reject(refreshError);  
      }  
    }

    // Handle 429 Too Many Requests \- Rate limiting  
    if (error.response?.status \=== 429\) {  
      const retryAfter \= error.response.headers\['retry-after'\];  
      const delay \= retryAfter ? parseInt(retryAfter) \* 1000 : 5000;  
        
      await new Promise(resolve \=\> setTimeout(resolve, delay));  
      return api(originalRequest);  
    }

    // Handle network errors with retry  
    if (\!error.response && \!originalRequest.\_retry) {  
      originalRequest.\_retry \= true;  
      await new Promise(resolve \=\> setTimeout(resolve, 2000));  
      return api(originalRequest);  
    }

    return Promise.reject(error);  
  }  
);

export default api;

### **5.2 API Service Layer**

// services/meetingsAPI.ts

import api from './api';  
import { Meeting, MeetingFilters, Transcript } from '@/types/meeting.types';

export async function getMeetings(filters: MeetingFilters) {  
  const params \= new URLSearchParams();  
    
  if (filters.start\_date) params.append('start\_date', filters.start\_date);  
  if (filters.end\_date) params.append('end\_date', filters.end\_date);  
  if (filters.risk\_category) params.append('risk\_category', filters.risk\_category);  
  if (filters.is\_compromised \!== undefined) {  
    params.append('is\_compromised', String(filters.is\_compromised));  
  }  
  params.append('page', String(filters.page || 1));  
  params.append('page\_size', String(filters.page\_size || 20));  
    
  const response \= await api.get(\`/meetings?${params.toString()}\`);  
  return response.data;  
}

export async function getMeeting(id: string): Promise\<Meeting\> {  
  const response \= await api.get(\`/meetings/${id}\`);  
  return response.data;  
}

export async function getMeetingTranscript(id: string): Promise\<Transcript\> {  
  const response \= await api.get(\`/meetings/${id}/transcript\`);  
  return response.data;  
}

export async function getMeetingForensics(id: string) {  
  const response \= await api.get(\`/meetings/${id}/forensics\`);  
  return response.data;  
}

export async function exportMeeting(  
  id: string,   
  format: 'pdf' | 'xlsx' | 'json'  
) {  
  const response \= await api.get(\`/meetings/${id}/export\`, {  
    params: { format },  
    responseType: format \=== 'json' ? 'json' : 'blob',  
  });  
    
  if (format \!== 'json') {  
    // Trigger download  
    const url \= window.URL.createObjectURL(new Blob(\[response.data\]));  
    const link \= document.createElement('a');  
    link.href \= url;  
    link.setAttribute('download', \`meeting-${id}.${format}\`);  
    document.body.appendChild(link);  
    link.click();  
    link.remove();  
  }  
    
  return response.data;  
}

---

## **6\. Performance Requirements**

### **6.1 Loading Performance**

Initial Load:  
  First Contentful Paint (FCP): \< 1.5 seconds  
  Largest Contentful Paint (LCP): \< 2.5 seconds  
  Time to Interactive (TTI): \< 3.5 seconds  
  Total Bundle Size: \< 500 KB (gzipped)  
    
Route Transitions:  
  Navigation: \< 200ms  
  Data fetching: \< 500ms  
  Page render: \< 300ms  
    
Code Splitting:  
  Initial bundle: \< 200 KB  
  Route chunks: \< 100 KB each  
  Vendor chunks: \< 200 KB  
  Dynamic imports for heavy components  
    
Asset Optimization:  
  Images: WebP format, lazy loading  
  Fonts: WOFF2, preloaded critical fonts  
  Icons: SVG sprites or icon fonts  
  CSS: Critical CSS inlined

### **6.2 Runtime Performance**

Rendering:  
  Frame rate: 60 FPS (16.67ms/frame)  
  Scroll performance: Butter smooth  
  Animation: Hardware accelerated  
  Re-renders: Minimized with React.memo, useMemo, useCallback  
    
Data Tables:  
  Rows displayed: Up to 10,000 with virtual scrolling  
  Sort/filter: \< 100ms  
  Column resize: Real-time, no lag  
  Export: Background processing for large datasets  
    
Charts:  
  Data points: Up to 10,000  
  Real-time updates: 1 second interval  
  Smooth animations: 60 FPS  
  Interactive tooltips: \< 16ms response  
    
Memory:  
  Heap size: \< 100 MB for typical usage  
  Memory leaks: Zero tolerance  
  Cleanup: Proper useEffect cleanup  
  Large lists: Virtual scrolling (react-window)

### **6.3 Optimization Techniques**

// Example: Virtualized table with react-window

import React from 'react';  
import { FixedSizeList } from 'react-window';  
import AutoSizer from 'react-virtualized-auto-sizer';

interface MeetingRow {  
  id: string;  
  name: string;  
  risk\_score: number;  
  date: string;  
}

interface VirtualizedMeetingListProps {  
  meetings: MeetingRow\[\];  
  onRowClick: (meeting: MeetingRow) \=\> void;  
}

const VirtualizedMeetingList: React.FC\<VirtualizedMeetingListProps\> \= ({  
  meetings,  
  onRowClick  
}) \=\> {  
  const Row \= React.memo(({ index, style }: any) \=\> {  
    const meeting \= meetings\[index\];  
      
    return (  
      \<div  
        style={style}  
        onClick={() \=\> onRowClick(meeting)}  
        className="meeting-row"  
      \>  
        \<span\>{meeting.name}\</span\>  
        \<span\>{meeting.risk\_score}%\</span\>  
        \<span\>{meeting.date}\</span\>  
      \</div\>  
    );  
  });

  return (  
    \<AutoSizer\>  
      {({ height, width }) \=\> (  
        \<FixedSizeList  
          height={height}  
          width={width}  
          itemCount={meetings.length}  
          itemSize={60}  
          overscanCount={5}  
        \>  
          {Row}  
        \</FixedSizeList\>  
      )}  
    \</AutoSizer\>  
  );  
};

export default VirtualizedMeetingList;

// Example: Debounced search

import { useState, useCallback } from 'react';  
import debounce from 'lodash/debounce';

export function useDebounce\<T extends (...args: any\[\]) \=\> any\>(  
  callback: T,  
  delay: number  
) {  
  const debouncedFn \= useCallback(  
    debounce((...args: Parameters\<T\>) \=\> callback(...args), delay),  
    \[callback, delay\]  
  );

  return debouncedFn;  
}

// Usage in component  
function SearchInput() {  
  const \[searchTerm, setSearchTerm\] \= useState('');  
    
  const performSearch \= async (term: string) \=\> {  
    if (term.length \< 3\) return;  
    // API call to search  
    const results \= await api.search(term);  
    // Update results  
  };  
    
  const debouncedSearch \= useDebounce(performSearch, 500);  
    
  const handleChange \= (e: React.ChangeEvent\<HTMLInputElement\>) \=\> {  
    const value \= e.target.value;  
    setSearchTerm(value);  
    debouncedSearch(value);  
  };  
    
  return \<input value={searchTem} onChange={handleChange} /\>;  
}

---

## **7\. Responsive Design Requirements**

### **7.1 Breakpoints**

// styles/theme.ts

export const breakpoints \= {  
  xs: 0,      // Mobile portrait  
  sm: 600,    // Mobile landscape  
  md: 960,    // Tablet  
  lg: 1280,   // Desktop  
  xl: 1920,   // Large desktop  
};

// Media query helpers  
export const media \= {  
  xs: \`@media (min-width: ${breakpoints.xs}px)\`,  
  sm: \`@media (min-width: ${breakpoints.sm}px)\`,  
  md: \`@media (min-width: ${breakpoints.md}px)\`,  
  lg: \`@media (min-width: ${breakpoints.lg}px)\`,  
  xl: \`@media (min-width: ${breakpoints.xl}px)\`,  
};

### **7.2 Responsive Layout Rules**

Mobile (\< 600px):  
  \- Single column layout  
  \- Collapsible sidebar (hamburger menu)  
  \- Stacked metric cards  
  \- Simplified tables (show key columns only)  
  \- Bottom navigation for quick actions  
  \- Touch-friendly targets (min 44x44px)  
    
Tablet (600px \- 960px):  
  \- Two column layout where applicable  
  \- Sidebar toggleable  
  \- Metric cards in 2-column grid  
  \- Tables with horizontal scroll  
  \- Expanded touch targets  
    
Desktop (960px+):  
  \- Multi-column layouts  
  \- Persistent sidebar  
  \- Metric cards in 3-4 column grid  
  \- Full tables with all columns  
  \- Hover states and tooltips  
    
Large Desktop (1920px+):  
  \- Max width container (1600px)  
  \- Wider spacing  
  \- Larger fonts  
  \- More data density

---

## **8\. Accessibility Requirements**

### **8.1 WCAG 2.1 Level AA Compliance**

Keyboard Navigation:  
  \- All interactive elements keyboard accessible  
  \- Logical tab order  
  \- Visible focus indicators  
  \- Skip to main content link  
  \- Escape key to close modals/menus  
    
Screen Readers:  
  \- Semantic HTML  
  \- ARIA labels where needed  
  \- ARIA live regions for dynamic content  
  \- Alt text for all images  
  \- Form labels properly associated  
    
Color & Contrast:  
  \- Text: Minimum 4.5:1 contrast ratio  
  \- Large text: Minimum 3:1 contrast ratio  
  \- Interactive elements: Clear visual states  
  \- No color-only information  
    
Responsive Text:  
  \- Font sizes: 16px minimum  
  \- Line height: 1.5 minimum  
  \- Text can be resized 200% without breaking  
  \- No horizontal scrolling at 320px width

### **8.2 Accessibility Implementation**

// Example: Accessible Modal

import React, { useEffect, useRef } from 'react';  
import { Dialog, DialogTitle, DialogContent } from '@mui/material';  
import { Close } from '@mui/icons-material';

interface AccessibleModalProps {  
  open: boolean;  
  onClose: () \=\> void;  
  title: string;  
  children: React.ReactNode;  
}

const AccessibleModal: React.FC\<AccessibleModalProps\> \= ({  
  open,  
  onClose,  
  title,  
  children  
}) \=\> {  
  const closeButtonRef \= useRef\<HTMLButtonElement\>(null);

  useEffect(() \=\> {  
    if (open && closeButtonRef.current) {  
      closeButtonRef.current.focus();  
    }  
  }, \[open\]);

  const handleKeyDown \= (e: React.KeyboardEvent) \=\> {  
    if (e.key \=== 'Escape') {  
      onClose();  
    }  
  };

  return (  
    \<Dialog  
      open={open}  
      onClose={onClose}  
      onKeyDown={handleKeyDown}  
      aria-labelledby="modal-title"  
      aria-describedby="modal-description"  
    \>  
      \<DialogTitle id="modal-title"\>  
        {title}  
        \<button  
          ref={closeButtonRef}  
          onClick={onClose}  
          aria-label="Close modal"  
          style={{  
            position: 'absolute',  
            right: 8,  
            top: 8,  
          }}  
        \>  
          \<Close /\>  
        \</button\>  
      \</DialogTitle\>  
      \<DialogContent id="modal-description"\>  
        {children}  
      \</DialogContent\>  
    \</Dialog\>  
  );  
};

---

## **9\. Testing Requirements**

### **9.1 Testing Stack**

Unit Testing:  
  Framework: Jest 29+  
  React Testing: React Testing Library  
  Coverage target: 80%  
    
Integration Testing:  
  Tool: React Testing Library  
  API Mocking: MSW (Mock Service Worker)  
  Coverage target: 70%  
    
E2E Testing:  
  Framework: Playwright or Cypress  
  Critical paths:  
    \- User login flow  
    \- Meeting list and detail view  
    \- Incident investigation flow  
    \- Export functionality  
  Coverage: All critical user journeys  
    
Visual Regression:  
  Tool: Percy or Chromatic  
  Coverage: All major components and pages  
    
Performance Testing:  
  Tool: Lighthouse CI  
  Thresholds:  
    \- Performance: \> 90  
    \- Accessibility: \> 95  
    \- Best Practices: \> 90  
    \- SEO: \> 90

### **9.2 Test Examples**

// Example unit test

import { render, screen, fireEvent } from '@testing-library/react';  
import TrustBadge from '@/components/features/meetings/TrustBadge';

describe('TrustBadge', () \=\> {  
  it('renders verified badge correctly', () \=\> {  
    render(\<TrustBadge level="verified" score={95} /\>);  
      
    const badge \= screen.getByRole('img', { hidden: true });  
    expect(badge).toBeInTheDocument();  
      
    // Check tooltip  
    const tooltip \= screen.getByText('Verified & Trusted');  
    expect(tooltip).toBeInTheDocument();  
  });

  it('shows score when showScore is true', () \=\> {  
    render(\<TrustBadge level="verified" score={95} showScore /\>);  
      
    expect(screen.getByText('95%')).toBeInTheDocument();  
  });

  it('renders high-risk badge with correct color', () \=\> {  
    const { container } \= render(  
      \<TrustBadge level="high-risk" score={15} /\>  
    );  
      
    const badgeElement \= container.querySelector('.MuiBadge-badge');  
    expect(badgeElement).toHaveStyle({ backgroundColor: '\#f44336' });  
  });  
});

// Example integration test

import { render, screen, waitFor } from '@testing-library/react';  
import { QueryClientProvider } from '@tanstack/react-query';  
import { queryClient } from '@/services/queryClient';  
import MeetingsPage from '@/pages/Meetings/MeetingsPage';  
import { setupServer } from 'msw/node';  
import { rest } from 'msw';

const server \= setupServer(  
  rest.get('/api/v1/meetings', (req, res, ctx) \=\> {  
    return res(  
      ctx.json({  
        data: \[  
          {  
            id: '1',  
            meeting\_name: 'Test Meeting',  
            risk\_score: 45,  
            risk\_category: 'medium',  
          },  
        \],  
        pagination: {  
          page: 1,  
          page\_size: 20,  
          total\_items: 1,  
        },  
      })  
    );  
  })  
);

beforeAll(() \=\> server.listen());  
afterEach(() \=\> server.resetHandlers());  
afterAll(() \=\> server.close());

describe('MeetingsPage', () \=\> {  
  it('loads and displays meetings', async () \=\> {  
    render(  
      \<QueryClientProvider client={queryClient}\>  
        \<MeetingsPage /\>  
      \</QueryClientProvider\>  
    );

    // Check loading state  
    expect(screen.getByText('Loading...')).toBeInTheDocument();

    // Wait for data to load  
    await waitFor(() \=\> {  
      expect(screen.getByText('Test Meeting')).toBeInTheDocument();  
    });

    // Check risk score is displayed  
    expect(screen.getByText('45%')).toBeInTheDocument();  
  });  
});

---

## **10\. Build & Deployment**

### **10.1 Build Configuration**

// vite.config.ts

import { defineConfig } from 'vite';  
import react from '@vitejs/plugin-react';  
import path from 'path';  
import { visualizer } from 'rollup-plugin-visualizer';  
import compression from 'vite-plugin-compression';

export default defineConfig({  
  plugins: \[  
    react(),  
    compression({  
      algorithm: 'gzip',  
      ext: '.gz',  
    }),  
    compression({  
      algorithm: 'brotliCompress',  
      ext: '.br',  
    }),  
    visualizer({  
      filename: './dist/stats.html',  
      open: false,  
      gzipSize: true,  
      brotliSize: true,  
    }),  
  \],  
  resolve: {  
    alias: {  
      '@': path.resolve(\_\_dirname, './src'),  
    },  
  },  
  build: {  
    target: 'es2015',  
    outDir: 'dist',  
    sourcemap: process.env.NODE\_ENV \!== 'production',  
    minify: 'terser',  
    terserOptions: {  
      compress: {  
        drop\_console: process.env.NODE\_ENV \=== 'production',  
        drop\_debugger: true,  
      },  
    },  
    rollupOptions: {  
      output: {  
        manualChunks: {  
          vendor: \['react', 'react-dom', 'react-router-dom'\],  
          mui: \['@mui/material', '@mui/icons-material'\],  
          charts: \['recharts'\],  
          utils: \['axios', 'date-fns', 'lodash'\],  
        },  
      },  
    },  
    chunkSizeWarningLimit: 1000,  
  },  
  server: {  
    port: 3000,  
    proxy: {  
      '/api': {  
        target: 'http://localhost:8000',  
        changeOrigin: true,  
      },  
      '/ws': {  
        target: 'ws://localhost:8000',  
        ws: true,  
      },  
    },  
  },  
});

### **10.2 Environment Variables**

\# .env.production

VITE\_APP\_NAME=DeepSafe  
VITE\_API\_URL=https://api.deepsafe.ai/v1  
VITE\_WS\_URL=wss://api.deepsafe.ai/v1/ws  
VITE\_SENTRY\_DSN=https://xxx@sentry.io/xxx  
VITE\_GOOGLE\_ANALYTICS\_ID=G-XXXXXXXXXX  
VITE\_ENVIRONMENT=production

### **10.3 CI/CD Pipeline**

\# .github/workflows/deploy.yml

name: Build and Deploy

on:  
  push:  
    branches: \[main, staging\]  
  pull\_request:  
    branches: \[main\]

jobs:  
  test:  
    runs-on: ubuntu-latest  
    steps:  
      \- uses: actions/checkout@v3  
        
      \- name: Setup Node.js  
        uses: actions/setup-node@v3  
        with:  
          node-version: '18'  
          cache: 'pnpm'  
        
      \- name: Install dependencies  
        run: pnpm install \--frozen-lockfile  
        
      \- name: Run linter  
        run: pnpm lint  
        
      \- name: Run type check  
        run: pnpm tsc \--noEmit  
        
      \- name: Run tests  
        run: pnpm test \--coverage  
        
      \- name: Upload coverage  
        uses: codecov/codecov-action@v3

  build:  
    needs: test  
    runs-on: ubuntu-latest  
    if: github.event\_name \== 'push'  
      
    steps:  
      \- uses: actions/checkout@v3  
        
      \- name: Setup Node.js  
        uses: actions/setup-node@v3  
        with:  
          node-version: '18'  
          cache: 'pnpm'  
        
      \- name: Install dependencies  
        run: pnpm install \--frozen-lockfile  
        
      \- name: Build  
        run: pnpm build  
        env:  
          VITE\_API\_URL: ${{ secrets.API\_URL }}  
          VITE\_WS\_URL: ${{ secrets.WS\_URL }}  
        
      \- name: Upload build artifacts  
        uses: actions/upload-artifact@v3  
        with:  
          name: dist  
          path: dist/

  deploy:  
    needs: build  
    runs-on: ubuntu-latest  
    if: github.ref \== 'refs/heads/main'  
      
    steps:  
      \- name: Download build artifacts  
        uses: actions/download-artifact@v3  
        with:  
          name: dist  
          path: dist/  
        
      \- name: Deploy to S3  
        uses: jakejarvis/s3-sync-action@master  
        with:  
          args: \--delete \--cache-control max-age=31536000  
        env:  
          AWS\_S3\_BUCKET: ${{ secrets.AWS\_S3\_BUCKET }}  
          AWS\_ACCESS\_KEY\_ID: ${{ secrets.AWS\_ACCESS\_KEY\_ID }}  
          AWS\_SECRET\_ACCESS\_KEY: ${{ secrets.AWS\_SECRET\_ACCESS\_KEY }}  
          SOURCE\_DIR: 'dist'  
        
      \- name: Invalidate CloudFront  
        uses: chetan/invalidate-cloudfront-action@v2  
        env:  
          DISTRIBUTION: ${{ secrets.CLOUDFRONT\_DISTRIBUTION\_ID }}  
          PATHS: '/\*'  
          AWS\_REGION: 'us-east-1'  
          AWS\_ACCESS\_KEY\_ID: ${{ secrets.AWS\_ACCESS\_KEY\_ID }}  
          AWS\_SECRET\_ACCESS\_KEY: ${{ secrets.AWS\_SECRET\_ACCESS\_KEY }}

---

## **11\. Browser Support**

Supported Browsers:  
  Chrome/Edge: Last 2 versions  
  Firefox: Last 2 versions  
  Safari: Last 2 versions  
  iOS Safari: iOS 13+  
  Chrome Android: Last 2 versions

Not Supported:  
  Internet Explorer: Any version  
  Legacy Edge: Pre-Chromium versions

Polyfills Required:  
  \- Core-js for ES6+ features  
  \- Intersection Observer  
  \- ResizeObserver  
  \- AbortController

Feature Detection:  
  \- Check for WebSocket support  
  \- Check for local storage  
  \- Check for IndexedDB  
  \- Fallback messages for unsupported browsers

---

## **12\. Security Requirements (Frontend)**

Content Security Policy:  
  default-src: 'self'  
  script-src: 'self' 'unsafe-inline' https://apis.google.com  
  style-src: 'self' 'unsafe-inline'  
  img-src: 'self' data: https:  
  connect-src: 'self' wss://api.deepsafe.ai https://api.deepsafe.ai  
  font-src: 'self' data:  
  frame-ancestors: 'none'

XSS Prevention:  
  \- Sanitize all user inputs  
  \- Use React's built-in XSS protection  
  \- Avoid dangerouslySetInnerHTML  
  \- Use DOMPurify for HTML sanitization when needed

CSRF Protection:  
  \- CSRF tokens in state-changing requests  
  \- SameSite cookies  
  \- Double-submit cookie pattern

Sensitive Data:  
  \- Never log sensitive data to console in production  
  \- Clear sensitive data from state on logout  
  \- No sensitive data in localStorage (use httpOnly cookies)  
  \- Mask PII in UI where appropriate

Dependencies:  
  \- Regular security audits (npm audit)  
  \- Automated dependency updates (Dependabot)  
  \- Lock file committed to repo  
  \- No dependencies with known vulnerabilities

---

This completes the comprehensive technical requirements for both the application and dashboard. Would you like me to add anything else, such as:

1. Database migration strategy?  
2. Disaster recovery procedures?  
3. API rate limiting implementation?  
4. Mobile app technical requirements?

