export class ExecutionWebSocket {
  private ws: WebSocket | null = null;
  private runId: string;
  private onMessageCallback: (msg: any) => void;
  private isManuallyClosed = false;

  constructor(runId: string, onMessage: (msg: any) => void) {
    this.runId = runId;
    this.onMessageCallback = onMessage;
    this.connect();
  }

  private connect() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    // If running in vite dev proxying or direct
    const wsUrl = `${protocol}//${host}/ws/execution/${this.runId}`;

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log(`[WS] Connected to execution stream: ${this.runId}`);
      };

      this.ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          this.onMessageCallback(payload);
        } catch (e) {
          console.error('[WS] Failed to parse message', e);
        }
      };

      this.ws.onclose = () => {
        if (!this.isManuallyClosed) {
          console.log('[WS] Connection closed. Attempting reconnect in 2s...');
          setTimeout(() => this.connect(), 2000);
        }
      };

      this.ws.onerror = (err) => {
        console.error('[WS] WebSocket error:', err);
      };
    } catch (e) {
      console.error('[WS] Exception initializing WebSocket', e);
    }
  }

  public sendCommand(action: 'pause' | 'resume' | 'stop') {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ action }));
    }
  }

  public close() {
    this.isManuallyClosed = true;
    if (this.ws) {
      this.ws.close();
    }
  }
}
