import { LitElement, html, css } from 'lit';
import { customElement, state } from 'lit/decorators.js';

interface AGUIBaseEvent {
  type: string;
  snapshot?: any;
  state?: any;
  tool_call_id?: string;
  delta?: string;
  content?: string;
  [key: string]: any;
}

const LAYOUT_ONLY_COMPONENTS = new Set([
  'Row',
  'Column',
  'List',
  'Tabs',
  'Modal',
  'Divider'
]);

@customElement('app-element')
export class AppElement extends LitElement {
  @state() private supportedComponents: string[] = [];
  @state() private selectedComponent: string = '';
  @state() private isWsConnected = false;
  @state() private reconnectAttempts = 0;

  @state() private streamingToolCallId: string | null = null;
  @state() private streamingArgsAccumulator: string = '';
  @state() private lastAGUIEvent: AGUIBaseEvent | null = null;
  @state() private currentA2UISpec: any = null;
  @state() private surfaceDeletedMessage: string | null = null;

  private socket: WebSocket | null = null;
  private reconnectTimer: number | null = null;
  private isIntentionallyClosed = false;

  private readonly maxReconnectInterval = 30000;
  private readonly baseReconnectInterval = 1000;

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
    .status.reconnecting { background: #fef3c7; color: #92400e; }

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

    .component-preview {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .btn-primary {
      background-color: #2563eb;
      color: white;
      border: none;
      padding: 0.625rem 1.25rem;
      border-radius: 6px;
      cursor: pointer;
      font-weight: 600;
    }

    .input-field {
      padding: 0.5rem;
      border: 1px solid #cbd5e1;
      border-radius: 4px;
      width: 100%;
      box-sizing: border-box;
    }
  `;

  connectedCallback() {
    super.connectedCallback();
    this.isIntentionallyClosed = false;
    this.initWebSocket();
  }

  disconnectedCallback() {
    super.disconnectedCallback();
    this.isIntentionallyClosed = true;
    if (this.reconnectTimer !== null) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.socket?.close();
  }

  private initWebSocket() {
    if (this.socket) {
      this.socket.onopen = null;
      this.socket.onmessage = null;
      this.socket.onclose = null;
      this.socket.onerror = null;
      this.socket.close();
    }

    this.socket = new WebSocket('ws://localhost:8000/ws');

    this.socket.onopen = () => {
      console.log('[WebSocket] Connesso al server');
      this.isWsConnected = true;
      this.reconnectAttempts = 0;
    };

    this.socket.onmessage = (event) => {
      try {
        const aguiEvent: AGUIBaseEvent = JSON.parse(event.data);
        this.lastAGUIEvent = aguiEvent;
        this.processAGUIEvent(aguiEvent);
      } catch (err) {
        console.error('[WebSocket] Errore decodifica messaggio:', err);
      }
    };

    this.socket.onclose = () => {
      this.isWsConnected = false;
      if (!this.isIntentionallyClosed) {
        this.scheduleReconnect();
      }
    };

    this.socket.onerror = (error) => {
      console.error('[WebSocket] Errore di rete:', error);
      this.isWsConnected = false;
    };
  }

  private scheduleReconnect() {
    if (this.reconnectTimer !== null) return;

    this.reconnectAttempts++;
    const expDelay = Math.min(
      this.maxReconnectInterval,
      this.baseReconnectInterval * Math.pow(2, this.reconnectAttempts - 1)
    );
    const jitter = expDelay * 0.2 * (Math.random() - 0.5);
    const delay = Math.max(1000, Math.floor(expDelay + jitter));

    this.reconnectTimer = window.setTimeout(() => {
      this.reconnectTimer = null;
      this.initWebSocket();
    }, delay);
  }

  private processAGUIEvent(event: AGUIBaseEvent) {
    switch (event.type) {
      case 'STATE_SNAPSHOT':
        const componentsList = event.snapshot?.supportedComponents || event.state?.supportedComponents;
        if (componentsList) {
          this.supportedComponents = componentsList;
        }
        break;

      case 'TOOL_CALL_START':
        // Mappatura corretta con tool_call_id
        this.streamingToolCallId = event.tool_call_id || event.call_id;
        this.streamingArgsAccumulator = '';
        this.surfaceDeletedMessage = null;
        break;

      case 'TOOL_CALL_ARGS':
        // Mappatura corretta: estrae event.delta e verifica tool_call_id
        const incomingCallId = event.tool_call_id || event.call_id;
        if (incomingCallId === this.streamingToolCallId && event.delta) {
          this.streamingArgsAccumulator += event.delta;
        }
        break;

      case 'TOOL_CALL_END':
        this.streamingToolCallId = null;
        break;

      case 'TOOL_CALL_RESULT':
        // Mappatura corretta: parsing del payload contenuto in event.content
        let res: any = null;
        try {
          res = typeof event.content === 'string' ? JSON.parse(event.content) : event.result;
        } catch (e) {
          console.error("Errore nel parsing del contenuto di ToolCallResultEvent", e);
        }

        if (res?.deleteSurface) {
          this.currentA2UISpec = null;
          this.surfaceDeletedMessage = `Superficie "${res.deleteSurface.surfaceId}" azzerata (DeleteSurfaceMessage A2UI). Componente non supportato.`;
        } else if (res?.surfaceUpdate) {
          this.surfaceDeletedMessage = null;
          this.currentA2UISpec = res.surfaceUpdate;
        }
        break;
    }
  }

  private onSelectComponent(e: Event) {
    const val = (e.target as HTMLSelectElement).value;
    if (!val || !this.socket || this.socket.readyState !== WebSocket.OPEN) return;

    this.selectedComponent = val;

    if (LAYOUT_ONLY_COMPONENTS.has(val)) {
      this.currentA2UISpec = null;
      this.surfaceDeletedMessage = null;
      this.streamingArgsAccumulator = '';
    } else {
      this.currentA2UISpec = null;
      this.surfaceDeletedMessage = null;
    }

    this.socket.send(JSON.stringify({ component: val }));
  }

  private dispatchA2UIAction(actionName: string, componentId: string, payload: any = {}) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) return;

    const clientActionMessage = {
      v: '1.0',
      action: {
        surfaceId: 'functionCall',
        componentId: componentId,
        actionName: actionName,
        payload: payload,
        timestamp: new Date().toISOString()
      }
    };

    this.socket.send(JSON.stringify({ a2uiAction: clientActionMessage }));
  }

  private renderA2UIComponent(comp: any) {
    if (!comp) return html``;

    const props = comp.properties || {};
    const compType = comp.component || comp.type;

    switch (compType) {
      case 'Button':
        return html`
          <button 
            class="btn-primary"
            @click=${() => this.dispatchA2UIAction(props.action?.name || 'CLICK', comp.id, props.action?.parameters)}>
            ${props.child || 'Pulsante'}
          </button>
        `;

      case 'Text':
        return html`<p style="margin:0;">${props.text || props.content}</p>`;

      case 'Image':
        return html`
          <img 
            src=${props.url || props.src} 
            alt=${props.description || props.alt || ''} 
            style="max-width: 100%; border-radius: 4px;" 
          />
        `;

      case 'Video':
        return html`
          <video controls poster=${props.posterUrl || ''} style="width: 100%; max-width: 400px;">
            <source src=${props.url} type="video/mp4" />
            Il browser non supporta la riproduzione video.
          </video>
        `;

      case 'AudioPlayer':
        return html`
          <div>
            ${props.description ? html`<p style="margin: 0 0 0.5rem 0; font-size: 0.9rem;">${props.description}</p>` : ''}
            <audio controls src=${props.url} style="width: 100%;"></audio>
          </div>
        `;

      case 'Icon':
        return html`
          <span style="font-size: 1.5rem; display: inline-block;">
            📍 [Icona: ${props.name}]
          </span>
        `;

      case 'TextField':
        return html`
          <div>
            <label>${props.label}</label>
            <input 
              type=${props.variant === 'number' ? 'number' : 'text'} 
              class="input-field" 
              placeholder=${props.placeholder || ''} 
              .value=${props.value || ''}
              @change=${(e: Event) => this.dispatchA2UIAction('INPUT_CHANGED', comp.id, { value: (e.target as HTMLInputElement).value })}
            />
          </div>
        `;

      case 'CheckBox':
        return html`
          <label style="display: flex; align-items: center; gap: 0.5rem; font-weight: normal;">
            <input 
              type="checkbox" 
              ?checked=${Boolean(props.value)}
              @change=${(e: Event) => this.dispatchA2UIAction('TOGGLE_CHECKBOX', comp.id, { checked: (e.target as HTMLInputElement).checked })}
            />
            ${props.label}
          </label>
        `;

      case 'ChoicePicker':
        return html`
          <div>
            <label>${props.label}</label>
            ${(props.options || []).map((opt: any) => html`
              <label style="display: block; font-weight: normal; margin-bottom: 0.25rem;">
                <input 
                  type="radio" 
                  name=${comp.id} 
                  value=${opt.value} 
                  ?checked=${Array.isArray(props.value) ? props.value.includes(opt.value) : props.value === opt.value}
                  @change=${() => this.dispatchA2UIAction('CHANGE_SELECTION', comp.id, { selected: opt.value })}
                />
                ${opt.label}
              </label>
            `)}
          </div>
        `;

      case 'Card':
        return html`
          <div style="border: 1px solid #cbd5e1; border-radius: 6px; padding: 1rem; background: #ffffff;">
            <p style="margin:0; font-weight: 600;">[Card Container: ID figlio ${props.child}]</p>
          </div>
        `;

      case 'Slider':
        return html`
          <div>
            <label>${props.label}: ${props.value}</label>
            <input 
              type="range" 
              min=${props.min || 0} 
              max=${props.max || 100} 
              .value=${props.value || 0}
              @change=${(e: Event) => this.dispatchA2UIAction('UPDATE_SLIDER', comp.id, { value: (e.target as HTMLInputElement).value })}
            />
          </div>
        `;

      case 'DateTimeInput':
        return html`
          <div>
            <label>${props.label}</label>
            <input 
              type="datetime-local" 
              class="input-field"
              .value=${props.value || ''}
              @change=${(e: Event) => this.dispatchA2UIAction('UPDATE_DATETIME', comp.id, { value: (e.target as HTMLInputElement).value })}
            />
          </div>
        `;

      default:
        return html`<pre>${JSON.stringify(comp, null, 2)}</pre>`;
    }
  }

  private renderA2UISurface() {
    if (LAYOUT_ONLY_COMPONENTS.has(this.selectedComponent)) {
      return html`<p style="color: #64748b; text-align: center; font-style: italic;">
        Componente di Layout ("${this.selectedComponent}"). Nessun elemento grafico diretto da renderizzare.
      </p>`;
    }

    if (!this.currentA2UISpec || !this.currentA2UISpec.components) {
      return html`<p style="color: #94a3b8; text-align: center;">Nessun componente renderizzato.</p>`;
    }

    return html`
      <div class="component-preview">
        ${this.currentA2UISpec.components.map((c: any) => this.renderA2UIComponent(c))}
      </div>
    `;
  }

  private renderStatusBadge() {
    if (this.isWsConnected) {
      return html`<span class="status online">Connesso</span>`;
    }
    if (this.reconnectAttempts > 0) {
      return html`<span class="status reconnecting">Riconnessione... (#${this.reconnectAttempts})</span>`;
    }
    return html`<span class="status offline">Disconnesso</span>`;
  }

  render() {
    return html`
      <div class="header">
        <h2>Integrazione Full-Stack WebSocket (AG-UI & A2UI)</h2>
      </div>

      <div class="container">
        <!-- Sezione Sinistra: sharedState -->
        <div class="panel">
          <div class="panel-title">
            <span>sharedState</span>
            ${this.renderStatusBadge()}
          </div>

          <label>Seleziona Componente (A2UI Basic Catalog - 18 Componenti):</label>
          <select @change=${this.onSelectComponent} ?disabled=${!this.isWsConnected}>
            <option value="" disabled ?selected=${!this.selectedComponent}>-- Seleziona un componente --</option>
            ${this.supportedComponents.map(
              (c) => html`<option value=${c} ?selected=${this.selectedComponent === c}>${c}</option>`
            )}
          </select>

          <label>Messaggio AG-UI Ricevuto (JSON in Tempo Reale):</label>
          <div class="stream-box">
            ${this.lastAGUIEvent ? JSON.stringify(this.lastAGUIEvent, null, 2) : 'In attesa di eventi via WebSocket...'}
          </div>
        </div>

        <!-- Sezione Destra: functionCall -->
        <div class="panel">
          <div class="panel-title">
            <span>functionCall</span>
          </div>

          ${!LAYOUT_ONLY_COMPONENTS.has(this.selectedComponent) && this.streamingArgsAccumulator
            ? html`
                <label>AG-UI TOOL_CALL_ARGS (Streaming WS Token):</label>
                <div class="stream-box">${this.streamingArgsAccumulator}</div>
              `
            : ''}

          <label style="margin-top: 1rem;">Superficie A2UI:</label>

          ${this.surfaceDeletedMessage
            ? html`<div class="delete-notice">${this.surfaceDeletedMessage}</div>`
            : html`
                <div class="a2ui-surface">
                  ${this.renderA2UISurface()}
                </div>
              `}
        </div>
      </div>
    `;
  }
}