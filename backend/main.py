import asyncio
import json
import uuid
from typing import Dict, Any, Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from ag_ui.core import (
    StateSnapshotEvent,
    ToolCallStartEvent,
    ToolCallArgsEvent,
    ToolCallEndEvent,
    ToolCallResultEvent,
    CustomEvent
)

app = FastAPI(title="AG-UI & A2UI WebSocket Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

active_connections: Set[WebSocket] = set()

# Catalogo completo A2UI (18 componenti ufficiali)
A2UI_CATALOG_100: Dict[str, Dict[str, Any]] = {
    "Text": {
        "id": "text-01",
        "component": "Text",
        "properties": {
            "text": "Testo descrittivo A2UI trasmesso via WebSocket",
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
            "label": "Campo Input WS",
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

async def send_agui_event(websocket: WebSocket, event_model):
    """Invia un evento AG-UI al client via WebSocket."""
    await websocket.send_text(event_model.model_dump_json())

async def process_component_request(websocket: WebSocket, component_name: str):
    """Genera lo stream di eventi AG-UI/A2UI per la richiesta di un componente."""
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
        await send_agui_event(websocket, ToolCallStartEvent(tool_call_id=tool_call_id, tool_call_name=tool_name))
        await send_agui_event(websocket, ToolCallEndEvent(tool_call_id=tool_call_id))
        await send_agui_event(
            websocket, 
            ToolCallResultEvent(
                message_id=message_id,
                tool_call_id=tool_call_id,
                content=json.dumps(delete_message)
            )
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

    await send_agui_event(websocket, ToolCallStartEvent(tool_call_id=tool_call_id, tool_call_name=tool_name))
    
    chunk_size = 15
    for i in range(0, len(a2ui_str), chunk_size):
        chunk = a2ui_str[i:i + chunk_size]
        await send_agui_event(websocket, ToolCallArgsEvent(tool_call_id=tool_call_id, delta=chunk))
        await asyncio.sleep(0.04)

    await send_agui_event(websocket, ToolCallEndEvent(tool_call_id=tool_call_id))
    await send_agui_event(
        websocket, 
        ToolCallResultEvent(
            message_id=message_id,
            tool_call_id=tool_call_id,
            content=a2ui_str
        )
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.add(websocket)

    try:
        supported_list = list(A2UI_CATALOG_100.keys()) + ["NonSupportedComponent"]
        
        # Invio evento iniziale StateSnapshotEvent (AG-UI)
        initial_snapshot = StateSnapshotEvent(
            snapshot={
                "supportedComponents": supported_list,
                "components": supported_list,
                "selectedComponent": None
            }
        )
        await send_agui_event(websocket, initial_snapshot)

        while True:
            raw_data = await websocket.receive_text()
            try:
                msg = json.loads(raw_data)

                if "component" in msg:
                    asyncio.create_task(process_component_request(websocket, msg["component"]))

                elif "a2uiAction" in msg:
                    ack_event = CustomEvent(
                        name="A2UI_ACTION_PROCESSED",
                        value=msg["a2uiAction"]
                    )
                    await send_agui_event(websocket, ack_event)

            except json.JSONDecodeError:
                print("Messaggio JSON non valido ricevuto via WS")

    except WebSocketDisconnect:
        active_connections.remove(websocket)