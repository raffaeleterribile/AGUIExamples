import asyncio
import json
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # oppure specifica: ["http://localhost:7860", "http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

event_queue = asyncio.Queue()

# ============================================================
# COMPONENTI AG-UI
# ============================================================

def text_example():
    return {"type": "text", "text": "Questo è un componente TEXT."}

def buttons_example():
    return {
        "type": "component",
        "component": "buttons",
        "props": {
            "title": "Scegli un componente AG-UI",
            "buttons": [
                {"label": "Text", "value": "text"},
                {"label": "Buttons", "value": "buttons"},
                {"label": "Actions", "value": "actions"},
                {"label": "Card", "value": "card"},
                {"label": "List", "value": "list"},
                {"label": "Select", "value": "select"},
                {"label": "Form", "value": "form"},
                {"label": "Checkbox", "value": "checkbox"},
                {"label": "Grid", "value": "grid"},
                {"label": "Table", "value": "table"},
                {"label": "Image", "value": "image"},
                {"label": "Modal", "value": "modal"},
                {"label": "Progress", "value": "progress"},
                {"label": "Input", "value": "input"},
                {"label": "File", "value": "file"},
                {"label": "Wizard", "value": "wizard"}
            ]
        }
    }

def actions_example():
    return {
        "type": "actions",
        "actions": [
            {"id": "search", "label": "Cerca"},
            {"id": "save", "label": "Salva"},
            {"id": "cancel", "label": "Annulla"}
        ]
    }

def card_example():
    return {
        "type": "component",
        "component": "card",
        "props": {
            "title": "Titolo card",
            "subtitle": "Sottotitolo",
            "content": "Contenuto della card.",
            "actions": [
                {"label": "OK", "value": "ok"},
                {"label": "Annulla", "value": "cancel"}
            ]
        }
    }

def list_example():
    return {
        "type": "component",
        "component": "list",
        "props": {
            "title": "Lista di elementi",
            "items": ["Uno", "Due", "Tre", "Quattro"]
        }
    }

def select_example():
    return {
        "type": "component",
        "component": "select",
        "props": {
            "label": "Seleziona un'opzione",
            "options": [
                {"label": "A", "value": "A"},
                {"label": "B", "value": "B"},
                {"label": "C", "value": "C"}
            ]
        }
    }

def form_example():
    return {
        "type": "component",
        "component": "form",
        "props": {
            "title": "Inserisci i dati",
            "fields": [
                {"id": "nome", "label": "Nome", "type": "text"},
                {"id": "eta", "label": "Età", "type": "number"}
            ],
            "submit": {"label": "Invia", "value": "submit_form"}
        }
    }

def checkbox_example():
    return {
        "type": "component",
        "component": "form",
        "props": {
            "title": "Seleziona più opzioni",
            "fields": [
                {
                    "id": "scelte",
                    "label": "Opzioni",
                    "type": "checkbox",
                    "options": [
                        {"label": "Uno", "value": "uno"},
                        {"label": "Due", "value": "due"},
                        {"label": "Tre", "value": "tre"}
                    ]
                }
            ],
            "submit": {"label": "Conferma", "value": "submit_checkbox"}
        }
    }

def grid_example():
    return {
        "type": "component",
        "component": "grid",
        "props": {
            "columns": 3,
            "items": [
                {"title": "Elemento 1", "content": "Contenuto 1"},
                {"title": "Elemento 2", "content": "Contenuto 2"},
                {"title": "Elemento 3", "content": "Contenuto 3"},
                {"title": "Elemento 4", "content": "Contenuto 4"}
            ]
        }
    }

def table_example():
    return {
        "type": "component",
        "component": "table",
        "props": {
            "columns": [
                {"label": "Nome", "id": "nome"},
                {"label": "Età", "id": "eta"},
                {"label": "Città", "id": "citta"}
            ],
            "rows": [
                {"nome": "Mario", "eta": 30, "citta": "Roma"},
                {"nome": "Luca", "eta": 25, "citta": "Milano"},
                {"nome": "Giulia", "eta": 28, "citta": "Torino"}
            ]
        }
    }

def image_example():
    return {
        "type": "component",
        "component": "image",
        "props": {
            "url": "https://placekitten.com/300/200",
            "caption": "Immagine di esempio"
        }
    }

def modal_example():
    return {
        "type": "component",
        "component": "modal",
        "props": {
            "title": "Attenzione",
            "content": "Questo è un messaggio importante.",
            "actions": [
                {"label": "OK", "value": "ok"},
                {"label": "Chiudi", "value": "close"}
            ]
        }
    }

def progress_example():
    return {
        "type": "component",
        "component": "progress",
        "props": {
            "value": 70,
            "label": "Caricamento..."
        }
    }

def input_example():
    return {
        "type": "component",
        "component": "input",
        "props": {
            "label": "Scrivi qualcosa",
            "placeholder": "Testo...",
            "submit": {"label": "Invia", "value": "submit_input"}
        }
    }

def file_example():
    return {
        "type": "component",
        "component": "file",
        "props": {
            "label": "Carica un file",
            "accept": ["pdf", "txt"]
        }
    }

def wizard_example():
    return {
        "type": "component",
        "component": "wizard",
        "props": {
            "steps": [
                {"title": "Step 1", "content": "Contenuto step 1"},
                {"title": "Step 2", "content": "Contenuto step 2"},
                {"title": "Step 3", "content": "Contenuto step 3"}
            ]
        }
    }

# ============================================================
# ENDPOINTS
# ============================================================

@app.post("/agent/run")
async def agent_run(request: Request):
    await event_queue.put(text_example())
    await event_queue.put(buttons_example())
    return {"status": "ok"}

@app.get("/agent/events")
async def agent_events():
    async def event_stream():
        while True:
            event = await event_queue.get()
            yield f"data: {json.dumps(event)}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")
# METODO ALTERNATIVO PER INVIARE EVENTI AL CLIENT (SSE)
# from ag_ui.core import TextMessageContentEvent, EventType
# from ag_ui.encoder import EventEncoder

# # Create an event
# event = TextMessageContentEvent(
#     type=EventType.TEXT_MESSAGE_CONTENT,
#     message_id="msg_123",
#     delta="Hello, world!"
# )

# # Initialize the encoder
# encoder = EventEncoder()

# # Encode the event
# encoded_event = encoder.encode(event)
# print(encoded_event)
# # Output: data: {"type":"TEXT_MESSAGE_CONTENT","messageId":"msg_123","delta":"Hello, world!"}\n\n

@app.post("/agent/event")
async def agent_event(request: Request):
    data = await request.json()
    value = data.get("value")

    mapping = {
        "text": text_example,
        "buttons": buttons_example,
        "actions": actions_example,
        "card": card_example,
        "list": list_example,
        "select": select_example,
        "form": form_example,
        "checkbox": checkbox_example,
        "grid": grid_example,
        "table": table_example,
        "image": image_example,
        "modal": modal_example,
        "progress": progress_example,
        "input": input_example,
        "file": file_example,
        "wizard": wizard_example
    }

    component = mapping.get(value, buttons_example)
    await event_queue.put(component())
    return {"status": "ok"}
