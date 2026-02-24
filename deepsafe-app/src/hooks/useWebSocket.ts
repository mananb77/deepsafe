import { useEffect, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { config } from '../config/env';

export function useWebSocket() {
  const queryClient = useQueryClient();
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout>>();

  useEffect(() => {
    if (config.isMock) return;

    const connect = () => {
      const token = localStorage.getItem('access_token');
      if (!token) return;

      const url = `${config.wsBaseUrl}?token=${encodeURIComponent(token)}`;
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          switch (message.type) {
            case 'risk_update':
              queryClient.invalidateQueries({ queryKey: ['meetings'] });
              queryClient.invalidateQueries({ queryKey: ['dashboard'] });
              break;
            case 'incident_detected':
              queryClient.invalidateQueries({ queryKey: ['dashboard', 'recentIncidents'] });
              queryClient.invalidateQueries({ queryKey: ['meetings'] });
              break;
            case 'participant_update':
              queryClient.invalidateQueries({ queryKey: ['participants'] });
              break;
          }
        } catch {
          // Ignore malformed messages
        }
      };

      ws.onclose = () => {
        // Reconnect after 3 seconds
        reconnectTimerRef.current = setTimeout(connect, 3000);
      };

      ws.onerror = () => {
        ws.close();
      };
    };

    connect();

    return () => {
      clearTimeout(reconnectTimerRef.current);
      wsRef.current?.close();
    };
  }, [queryClient]);
}
