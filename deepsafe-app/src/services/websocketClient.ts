import { config } from '../config/env';

type MessageHandler = (message: Record<string, unknown>) => void;

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private handlers: Map<string, Set<MessageHandler>> = new Map();
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private url: string;

  constructor(meetingId?: string) {
    const token = localStorage.getItem('access_token') || '';
    const base = meetingId
      ? `${config.wsBaseUrl}/meetings/${meetingId}`
      : config.wsBaseUrl;
    this.url = `${base}?token=${encodeURIComponent(token)}`;
  }

  connect(): void {
    if (config.isMock) return;
    this.ws = new WebSocket(this.url);

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        const type = message.type as string;
        this.handlers.get(type)?.forEach((fn) => fn(message));
        this.handlers.get('*')?.forEach((fn) => fn(message));
      } catch {
        // Ignore malformed messages
      }
    };

    this.ws.onclose = () => {
      this.reconnectTimer = setTimeout(() => this.connect(), 3000);
    };

    this.ws.onerror = () => {
      this.ws?.close();
    };
  }

  on(type: string, handler: MessageHandler): () => void {
    if (!this.handlers.has(type)) {
      this.handlers.set(type, new Set());
    }
    this.handlers.get(type)!.add(handler);
    return () => this.handlers.get(type)?.delete(handler);
  }

  send(message: Record<string, unknown>): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  disconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
    }
    this.ws?.close();
    this.ws = null;
  }
}
