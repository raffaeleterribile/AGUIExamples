import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';
import { renderA2UI } from '@a2ui/lit';

interface AGUIBaseEvent {
  type: string;
  [key: string]: any;
}

@customElement('app-element')
export class AppElement extends LitElement {
  @state() private supportedComponents: string[] = [];
  @state() private selectedComponent: string = '';
  @state() private isConnected = false;

  @state() private streamingToolCallId: string | null = null;
  @state() private streamingArgsAccumulator: string = '';
  @state() private lastAGUIEvent: AGUIBaseEvent | null = null;
  @state() private currentA2UISpec: any = null;
  @state() private surfaceDeletedMessage: string | null = null;

  private eventSource: EventSource | null = null;

  static styles = css`
    :host {
      display: block;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      padding: 2rem;
      background: #f8fafc;
      min-height: 100vh;
      box-sizing: border-box;
    }

    .header {
      text-align: center;
      margin-bottom: 2rem;
    }

    .container {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 2rem;
      max-width: 1200px;
      margin: 0 auto;
    }

    .panel {
      background: #ffffff;
      border-radius: 8px;
      padding: 1.5rem;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
      border: 1px solid #e2e8f0;
    }

    .panel-title {
      font-size: 1.25rem;
      font-weight: 700;
      margin-top: 0;
      margin-bottom: 1rem;
      padding-bottom: 0.5rem;
      border-bottom: 2px solid #e2e8f0;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .status {
      font-size: 0.75rem;
      padding: 0.25rem 0.5rem;
      border-radius: 9999px;
      font-weight: 600;
    }
    .status.online { background: #dcfce7; color: #166534; }
    .status.offline { background: #fee2e2; color: #991b1b; }

    select {
      width: 100%;
      padding: 0.625rem;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
      font-size: 0.95rem;
      margin-bottom: 1.25rem;
    }

    .stream-box {
      background: #0f172a;
      color: #38bdf8;
      padding: 1rem;
      border-radius: 6px;
      font-family: monospace;
      font-size: 0.825rem;
      max-height: 220px;
      overflow-y: auto;
      white-space: pre-wrap;
    }

    .a2ui-surface {
      background: #fafafa;
      border: 2px dashed #3b82f6;
      border-radius: 8px;
      padding: 1.5rem;
      margin-top: 1rem;
      min-height: 120px;
    }

    .delete-notice {
      background-color: #fef2f2;
      border: 1px solid #fca5a5;
      color: #991b1b;
      padding: 1rem;
      border-radius: 6px;
      margin-top: 1rem;
      font-weight: 500;
      text-align: center;
    }

    label {
      font-weight: 600;
      display: block;
      margin-bottom: 0.5rem;
      color: #334155;
    }
  `;

  connectedCallback() {
    super.connectedCallback();
    this.initSSE();
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this.eventSource?.close();
  }

  private initSSE() {
    this.eventSource = new EventSource('http://localhost:8000/streaming');

    this.eventSource.onopen = () => {
      this.isConnected = true;
    };

    this.eventSource.onmessage = (e) => {
      try {
        const event: AGUIBaseEvent = JSON.parse(e.data);
        this.lastAGUIEvent = event;
        this.processAGUIEvent(event);
      } catch (err) {
        console.error('Errore durante la decodifica dell'evento SSE:', err);
      }
    };

    this.eventSource.onerror = () => {
      this.isConnected = false;
    };
  }

  private processAGUIEvent(event: AGUIBaseEvent) {
    switch (event.type) {
      case 'STATE_SNAPSHOT':
        if (event.state?.supportedComponents) {
          this.supportedComponents = event.state.supportedComponents;
        }
        break;

      case 'TOOL_CALL_START':
        this.streamingToolCallId = event.call_id;
        this.streamingArgsAccumulator = '';
        this.surfaceDeletedMessage = null;
        break;

      case 'TOOL_CALL_ARGS':
        if (event.call_id === this.streamingToolCallId) {
          this.streamingArgsAccumulator += event.args_chunk;
        }
        break;

      case 'TOOL_CALL_END':
        this.streamingToolCallId = null;
        break;

      case 'TOOL_CALL_RESULT':
        const res = event.result;
        
        // Gestione DeleteSurfaceMessage (schema A2UI v0.9.1 server_to_client)
        if (res?.deleteSurface) {
          this.currentA2UISpec = null;
          this.surfaceDeletedMessage = `Superficie "${res.deleteSurface.surfaceId}" azzerata (DeleteSurfaceMessage A2UI v0.9.1). Componente non supportato.`;
        } 
        // Gestione SurfaceUpdateMessage (schema A2UI v0.9.1 server_to_client)
        else if (res?.surfaceUpdate) {
          this.surfaceDeletedMessage = null;
          this.currentA2UISpec = res;
        }
        break;
    }
  }

  private async onSelectComponent(e: Event) {
    const val = (e.target as HTMLSelectElement).value;
    if (!val) return;

    this.selectedComponent = val;
    this.currentA2UISpec = null;
    this.surfaceDeletedMessage = null;

    await fetch('http://localhost:8000/action', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ component: val })
    });
  }

  /**
   * Handler di dispatch per i messaggi Client-to-Server A2UI (client_to_server.json)
   * Genera un messaggio di tipo 'action' e lo trasmette al backend.
   */
  private async dispatchA2UIAction(actionName: string, componentId: string, payload: any = {}) {
    const clientActionMessage = {
      v: "0.9.1",
      action: {
        surfaceId: "functionCall",
        componentId: componentId,
        actionName: actionName,
        payload: payload,
        timestamp: new Date().toISOString()
      }
    };

    await fetch('http://localhost:8000/action', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ a2uiAction: clientActionMessage })
    });
  }

  private handleA2UINativeInteraction(e: CustomEvent) {
    // Intercetta eventi generati dal renderer A2UI
    const detail = e.detail || {};
    this.dispatchA2UIAction(detail.actionName || 'USER_INTERACTION', detail.componentId || 'a2ui-comp', detail);
  }

  render() {
    return html`
      <div class="header">
        <h2>Integrazione Protocolli AG-UI & A2UI v0.9.1</h2>
      </div>

      <div class="container">
        <!-- Sezione Sinistra: sharedState -->
        <div class="panel">
          <div class="panel-title">
            <span>sharedState</span>
            <span class="status ${this.isConnected ? 'online' : 'offline'}">
              ${this.isConnected ? 'SSE Connesso' : 'Disconnesso'}
            </span>
          </div>

          <label>Seleziona Componente (A2UI Basic Catalog):</label>
          <select @change=${this.onSelectComponent}>
            <option value="" disabled ?selected=${!this.selectedComponent}>-- Seleziona un componente --</option>
            ${this.supportedComponents.map(
              (c) => html`<option value=${c} ?selected=${this.selectedComponent === c}>${c}</option>`
            )}
          </select>

          <label>Evento AG-UI (Messaggio JSON in tempo reale):</label>
          <div class="stream-box">
            ${this.lastAGUIEvent ? JSON.stringify(this.lastAGUIEvent, null, 2) : 'In attesa di eventi dal server...'}
          </div>
        </div>

        <!-- Sezione Destra: functionCall -->
        <div class="panel">
          <div class="panel-title">
            <span>functionCall</span>
          </div>

          ${this.streamingArgsAccumulator
            ? html`
                <label>AG-UI TOOL_CALL_ARGS (Streaming A2UI Payload):</label>
                <div class="stream-box">${this.streamingArgsAccumulator}</div>
              `
            : ''}

          <label style="margin-top: 1rem;">Superficie A2UI (A2UI Renderer / DeleteSurface):</label>

          ${this.surfaceDeletedMessage
            ? html`<div class="delete-notice">${this.surfaceDeletedMessage}</div>`
            : html`
                <div class="a2ui-surface" @a2ui-action=${this.handleA2UINativeInteraction}>${this.currentA2UISpec
                    ? renderA2UI(this.currentA2UISpec)
                    : html`<p style="color: #94a3b8; text-align: center;">Nessun componente renderizzato.</p>`}
                </div>
              `}
        </div>
      </div>
    `;
  }
}