const dataMode = import.meta.env.VITE_DATA_MODE || 'mock';

export const config = {
  dataMode,
  isLive: dataMode === 'live',
  isMock: dataMode !== 'live',
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  wsBaseUrl: import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000/api/v1/ws',
} as const;
