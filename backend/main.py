import asyncio
import json
import uuid
from typing import Dict, Any, Set, AsyncGenerator
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from ag_ui.core import (
    StateSnapshotEvent,
    ToolCallStartEvent,
    ToolCallArgsEvent,
    ToolCallEndEvent,
    ToolCallResultEvent,
    CustomEvent
)

app = FastAPI(title="AG-UI & A2UI Dual Protocol Server (WS & SSE)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gestione delle connessioni attive
active_ws_connections: Set[WebSocket] = set()
sse_queues: Dict[str, asyncio.Queue] = {}

# Catalogo completo A2UI (18 componenti ufficiali)
A2UI_CATALOG_100: Dict[str, Dict[str, Any]] = {
    "Text": {
        "id": "text-01",
        "component": "Text",
        "properties": {
            "text": "Testo descrittivo A2UI trasmesso in streaming",
            "variant": "body"
        }
    },
    "Image": {
        "id": "img-01",
        "component": "Image",
        "properties": {
            "url": "https://via.placeholder.com/150",
            "description": "Immagine di esempio A2UI",
            "variant": "mediumFeature"
        }
    },
    "Icon": {
        "id": "icon-01",
        "component": "Icon",
        "properties": {
            "name": "check"
        }
    },
    "Video": {
        "id": "video-01",
        "component": "Video",
        "properties": {
            "url": "https://www.w3schools.com/html/mov_bbb.mp4",
            "posterUrl": "https://via.placeholder.com/320x180"
        }
    },
    "AudioPlayer": {
        "id": "audio-01",
        "component": "AudioPlayer",
        "properties": {
            "url": "https://www.w3schools.com/html/horse.mp3",
            "description": "Riproduttore audio di test"
        }
    },
    "Row": {
        "id": "row-01",
        "component": "Row",
        "properties": {
            "children": [],
            "justify": "start",
            "align": "stretch"
        }
    },
    "Column": {
        "id": "col-01",
        "component": "Column",
        "properties": {
            "children": [],
            "justify": "start",
            "align": "stretch"
        }
    },
    "List": {
        "id": "list-01",
        "component": "List",
        "properties": {
            "children": [],
            "direction": "vertical"
        }
    },
    "Card": {
        "id": "card-01",
        "component": "Card",
        "properties": {
            "child": "text-01"
        }
    },
    "Tabs": {
        "id": "tabs-01",
        "component": "Tabs",
        "properties": {
            "tabs": [
                {"title": "Tab 1", "child": "text-01"}
            ]
        }
    },
    "Modal": {
        "id": "modal-01",
        "component": "Modal",
        "properties": {
            "trigger": "btn-01",
            "content": "text-01"
        }
    },
    "Divider": {
        "id": "divider-01",
        "component": "Divider",
        "properties": {
            "axis": "horizontal"
        }
    },
    "Button": {
        "id": "btn-01",
        "component": "Button",
        "properties": {
            "child": "text-01",
            "variant": "primary",
            "action": {
                "name": "SUBMIT_FORM",
                "parameters": {"formId": "a2ui-form-01"}
            }
        }
    },
    "TextField": {
        "id": "input-01",
        "component": "TextField",
        "properties": {
            "label": "Campo Input Streaming",
            "placeholder": "Digita qualcosa...",
            "value": "",
            "variant": "shortText"
        }
    },
    "CheckBox": {
        "id": "chk-01",
        "component": "CheckBox",
        "properties": {
            "label": "Accetto termini e condizioni",
            "value": False
        }
    },
    "ChoicePicker": {
        "id": "choice-01",
        "component": "ChoicePicker",
        "properties": {
            "label": "Seleziona priorità",
            "options": [
                {"label": "Bassa", "value": "low"},
                {"label": "Media", "value": "medium"},
                {"label": "Alta", "value": "high"}
            ],
            "value": ["medium"],
            "variant": "mutuallyExclusive",
            "displayStyle": "checkbox"
        }
    },
    "Slider": {
        "id": "slider-01",
        "component": "Slider",
        "properties": {
            "label": "Livello di completamento",
            "min": 0,
            "max": 100,
            "value": 60
        }
    },
    "DateTimeInput": {
        "id": "dt-01",
        "component": "DateTimeInput",
        "properties": {
            "label": "Seleziona Data e Ora",
            "value": "2026-10-01T12:00",
            "enableDate": True,
            "enableTime": True
        }
    }
}


# ==========================================
# LOGICA CENTRALIZZATA GENERAZIONE EVENTI AG-UI
# ==========================================

def get_initial_state_snapshot() -> StateSnapshotEvent:
    """Genera lo snapshot iniziale con il catalogo componenti."""
    supported_list = list(A2UI_CATALOG_100.keys()) + ["NonSupportedComponent"]
    return StateSnapshotEvent(
        snapshot={
            "supportedComponents": supported_list,
            "components": supported_list,
            "selectedComponent": None
        }
    )


async def generate_component_events(component_name: str) -> AsyncGenerator[Any, None]:
    """Generatore centralizzato che produce la sequenza di eventi AG-UI per un componente."""
    tool_call_id = f"call_{uuid.uuid4().hex[:8]}"
    message_id = f"msg_{uuid.uuid4().hex[:8]}"
    tool_name = "render_a2ui"

    if component_name not in A2UI_CATALOG_100:
        delete_message = {
            "v": "1.0",
            "deleteSurface": {
                "surfaceId": "functionCall"
            }
        }
        yield ToolCallStartEvent(tool_call_id=tool_call_id, tool_call_name=tool_name)
        yield ToolCallEndEvent(tool_call_id=tool_call_id)
        yield ToolCallResultEvent(
            message_id=message_id,
            tool_call_id=tool_call_id,
            content=json.dumps(delete_message)
        )
        return

    comp_spec = A2UI_CATALOG_100[component_name]

    a2ui_message = {
        "v": "1.0",
        "surfaceUpdate": {
            "surfaceId": "functionCall",
            "components": [comp_spec]
        }
    }
    a2ui_str = json.dumps(a2ui_message)

    yield ToolCallStartEvent(tool_call_id=tool_call_id, tool_call_name=tool_name)
    
    chunk_size = 15
    for i in range(0, len(a2ui_str), chunk_size):
        chunk = a2ui_str[i:i + chunk_size]
        yield ToolCallArgsEvent(tool_call_id=tool_call_id, delta=chunk)
        await asyncio.sleep(0.04)

    yield ToolCallEndEvent(tool_call_id=tool_call_id)
    yield ToolCallResultEvent(
        message_id=message_id,
        tool_call_id=tool_call_id,
        content=a2ui_str
    )


def create_action_ack_event(a2ui_action: dict) -> CustomEvent:
    """Genera evento di conferma elaborazione azione."""
    return CustomEvent(
        name="A2UI_ACTION_PROCESSED",
        value=a2ui_action
    )


# ==========================================
# ENDPOINT WEBSOCKET (/ws)
# ==========================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_ws_connections.add(websocket)

    try:
        # Invio snapshot iniziale
        snapshot = get_initial_state_snapshot()
        await websocket.send_text(snapshot.model_dump_json())

        while True:
            raw_data = await websocket.receive_text()
            try:
                msg = json.loads(raw_data)

                if "component" in msg:
                    async for event in generate_component_events(msg["component"]):
                        await websocket.send_text(event.model_dump_json())

                elif "a2uiAction" in msg:
                    ack_event = create_action_ack_event(msg["a2uiAction"])
                    await websocket.send_text(ack_event.model_dump_json())

            except json.JSONDecodeError:
                print("[WS] JSON non valido ricevuto")

    except WebSocketDisconnect:
        active_ws_connections.remove(websocket)


# ==========================================
# ENDPOINT SSE (/streaming) E HTTP POST (/action)
# ==========================================

@app.get("/streaming")
async def sse_streaming_endpoint(request: Request, session_id: str = "default"):
    """Endpoint SSE che trasmette lo stream continuo di eventi AG-UI al client."""
    
    async def event_publisher():
        queue = asyncio.Queue()
        sse_queues[session_id] = queue

        # Invio snapshot iniziale al momento della connessione
        initial_snapshot = get_initial_state_snapshot()
        yield f"data: {initial_snapshot.model_dump_json()}\n\n"

        try:
            while True:
                # Se la connessione client è interrotta, interrompe il loop
                if await request.is_disconnected():
                    break
                
                # Attesa prossimo evento dalla coda
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=1.0)
                    yield f"data: {event.model_dump_json()}\n\n"
                except asyncio.TimeoutError:
                    # Heartbeat per mantenere la connessione attiva
                    yield ": keepalive\n\n"

        except asyncio.CancelledError:
            pass
        finally:
            sse_queues.pop(session_id, None)

    return StreamingResponse(
        event_publisher(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/action")
async def action_endpoint(request_data: Dict[str, Any]):
    """Endpoint HTTP POST per inviare selezioni o azioni quando si utilizza SSE."""
    session_id = request_data.get("session_id", "default")
    queue = sse_queues.get(session_id)

    if not queue:
        return {"status": "error", "message": f"Sessione SSE '{session_id}' non trovata o disconnessa"}

    # Gestione selezione componente via SSE
    if "component" in request_data:
        async for event in generate_component_events(request_data["component"]):
            await queue.put(event)

    # Gestione azione utente A2UI via SSE
    elif "a2uiAction" in request_data:
        ack_event = create_action_ack_event(request_data["a2uiAction"])
        await queue.put(ack_event)

    return {"status": "ok"}