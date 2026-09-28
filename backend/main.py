import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ag_ui_protocol import (
    StateSnapshotEvent,
    ToolCallStartEvent,
    ToolCallArgsEvent,
    ToolCallEndEvent,
    ToolCallResultEvent,
    ActionEvent
)

app = FastAPI(title="AG-UI & A2UI Full Protocol Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sse_queues: List[asyncio.Queue] = []

# Catalogo A2UI v0.9.1 (basic catalog) con gestione completa delle azioni
A2UI_CATALOG_091: Dict[str, Dict[str, Any]] = {
    "Button": {
        "id": "btn-01",
        "type": "Button",
        "properties": {
            "label": "Esegui Azione A2UI",
            "variant": "primary",
            "action": {
                "name": "SUBMIT_FORM",
                "parameters": {"formId": "a2ui-form-01"}
            }
        }
    },
    "Text": {
        "id": "txt-01",
        "type": "Text",
        "properties": {
            "content": "Testo descrittivo del componente A2UI v0.9.1",
            "variant": "body"
        }
    },
    "TextField": {
        "id": "input-01",
        "type": "TextField",
        "properties": {
            "label": "Campo Input",
            "placeholder": "Digita un testo...",
            "value": "",
            "action": {
                "name": "INPUT_CHANGED"
            }
        }
    },
    "CheckBox": {
        "id": "chk-01",
        "type": "CheckBox",
        "properties": {
            "label": "Conferma iscrizione",
            "checked": False,
            "action": {
                "name": "TOGGLE_CHECKBOX"
            }
        }
    },
    "ChoiceGroup": {
        "id": "choice-01",
        "type": "ChoiceGroup",
        "properties": {
            "label": "Seleziona priorità",
            "options": [
                {"label": "Bassa", "value": "low"},
                {"label": "Media", "value": "medium"},
                {"label": "Alta", "value": "high"}
            ],
            "value": "medium",
            "action": {
                "name": "CHANGE_PRIORITY"
            }
        }
    },
    "Card": {
        "id": "card-01",
        "type": "Card",
        "properties": {
            "title": "Scheda Modulare A2UI",
            "subtitle": "v0.9.1 Standard",
            "content": "Pannello informativo interattivo generato via streaming."
        }
    },
    "Slider": {
        "id": "slider-01",
        "type": "Slider",
        "properties": {
            "label": "Percentuale di completamento",
            "min": 0,
            "max": 100,
            "value": 40,
            "action": {
                "name": "UPDATE_SLIDER"
            }
        }
    },
    "DateTimeInput": {
        "id": "dt-01",
        "type": "DateTimeInput",
        "properties": {
            "label": "Seleziona Data e Ora",
            "value": "2026-10-01T12:00",
            "action": {
                "name": "UPDATE_DATETIME"
            }
        }
    }
}

class ActionRequest(BaseModel):
    component: Optional[str] = None
    a2uiAction: Optional[Dict[str, Any]] = None

async def broadcast_event(event_model):
    event_json = event_model.model_dump_json()
    for q in sse_queues:
        await q.put(event_json)

@app.get("/streaming")
async def stream_events():
    queue: asyncio.Queue = asyncio.Queue()
    sse_queues.append(queue)

    initial_snapshot = StateSnapshotEvent(
        state={
            "supportedComponents": list(A2UI_CATALOG_091.keys()) + ["NonSupportedComponent"],
            "selectedComponent": None
        }
    )
    await queue.put(initial_snapshot.model_dump_json())

    async def event_generator():
        try:
            while True:
                data = await queue.get()
                yield f"data: {data}\n\n"
        except asyncio.CancelledError:
            sse_queues.remove(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")

async def process_component_request(component_name: str):
    call_id = f"call_{uuid.uuid4().hex[:8]}"
    tool_name = "render_a2ui"

    # Se il componente non è supportato, genera il messaggio A2UI `deleteSurface`
    if component_name not in A2UI_CATALOG_091:
        delete_message = {
            "v": "0.9.1",
            "deleteSurface": {
                "surfaceId": "functionCall"
            }
        }
        await broadcast_event(ToolCallStartEvent(call_id=call_id, tool_name=tool_name))
        await broadcast_event(ToolCallEndEvent(call_id=call_id))
        await broadcast_event(ToolCallResultEvent(call_id=call_id, result=delete_message))
        return

    comp_spec = A2UI_CATALOG_091[component_name]

    # Server-to-Client message A2UI v0.9.1 `surfaceUpdate`
    a2ui_message = {
        "v": "0.9.1",
        "surfaceUpdate": {
            "surfaceId": "functionCall",
            "components": [comp_spec]
        }
    }
    a2ui_str = json.dumps(a2ui_message)

    await broadcast_event(ToolCallStartEvent(call_id=call_id, tool_name=tool_name))
    
    # Streaming progressivo del payload A2UI via AG-UI TOOL_CALL_ARGS
    chunk_size = 15
    for i in range(0, len(a2ui_str), chunk_size):
        chunk = a2ui_str[i:i + chunk_size]
        await broadcast_event(ToolCallArgsEvent(call_id=call_id, args_chunk=chunk))
        await asyncio.sleep(0.04)

    await broadcast_event(ToolCallEndEvent(call_id=call_id))
    await broadcast_event(ToolCallResultEvent(call_id=call_id, result=a2ui_message))

@app.post("/action")
async def handle_action(req: ActionRequest, background_tasks: BackgroundTasks):
    """
    Gestisce sia la selezione di un componente sia i messaggi Client-to-Server
    prodotti dalle interazioni utente sui componenti A2UI.
    """
    if req.component:
        background_tasks.add_task(process_component_request, req.component)
        return {"status": "component_requested", "component": req.component}

    if req.a2uiAction:
        # Ricezione e gestione del messaggio di azione A2UI (client_to_server.json)
        print(f"[A2UI Client Action Received]: {json.dumps(req.a2uiAction, indent=2)}")
        
        # Notifica dello stato via AG-UI
        ack_event = ActionEvent(
            action="A2UI_ACTION_PROCESSED",
            payload=req.a2uiAction
        )
        await broadcast_event(ack_event)
        return {"status": "a2ui_action_received", "action": req.a2uiAction}

    return {"status": "invalid_request"}