import gradio as gr
import requests
import sseclient
import threading
import time
import json

EVENTS_URL = "http://localhost:8000/agent/events"
RUN_URL = "http://localhost:8000/agent/run"
EVENT_URL = "http://localhost:8000/agent/event"

COMPONENTS = [
    "text", "buttons", "actions", "card", "list", "select",
    "form", "checkbox", "grid", "table", "image", "modal",
    "progress", "input", "file", "wizard"
]

event_log = []
last_event = None


def listen_events():
    """Thread che ascolta gli eventi SSE e aggiorna event_log + last_event."""
    global last_event
    messages = sseclient.SSEClient(EVENTS_URL)
    for msg in messages:
        if msg.data:
            event_log.append(msg.data)
            last_event = msg.data


def start_sse_listener():
    thread = threading.Thread(target=listen_events, daemon=True)
    thread.start()


def send_run_message():
    requests.post(RUN_URL, json={"message": "Ciao agente!"})


def send_event(value):
    requests.post(EVENT_URL, json={"event": "action", "value": value})


def handle_event(event_json):
    """Restituisce gli update per tutti i componenti, mostrando solo quello giusto."""
    # default: tutti nascosti
    updates = {
        "text": gr.update(visible=False),
        "buttons": gr.update(visible=False, choices=[]),
        "actions": gr.update(visible=False, choices=[]),
        "card": gr.update(visible=False, value=""),
        "list": gr.update(visible=False, value=""),
        "select": gr.update(visible=False, choices=[]),
        "form": gr.update(visible=False, value=""),
        "checkbox": gr.update(visible=False, choices=[]),
        "grid": gr.update(visible=False, value=""),
        "table": gr.update(visible=False, value=""),
        "image": gr.update(visible=False, value=None),
        "modal": gr.update(visible=False, value=""),
        "progress": gr.update(visible=False, value=0),
        "input": gr.update(visible=False, value=""),
        "file": gr.update(visible=False),
        "wizard": gr.update(visible=False, value=""),
    }

    if not event_json:
        return updates

    try:
        data = json.loads(event_json)
    except Exception:
        updates["text"] = gr.update(visible=True, value=f"Evento non valido:\n{event_json}")
        return updates

    t = data.get("type")

    if t == "text":
        updates["text"] = gr.update(visible=True, value=data.get("text", ""))
        return updates

    if t == "actions":
        labels = [a.get("label", "") for a in data.get("actions", [])]
        updates["actions"] = gr.update(visible=True, choices=labels)
        return updates

    if t == "component":
        comp = data.get("component")
        props = data.get("props", {})

        if comp == "buttons":
            labels = [b.get("label", "") for b in props.get("buttons", [])]
            updates["buttons"] = gr.update(visible=True, choices=labels)

        elif comp == "list":
            updates["list"] = gr.update(
                visible=True,
                value="\n".join(props.get("items", []))
            )

        elif comp == "card":
            md = (
                f"### {props.get('title','')}\n"
                f"**{props.get('subtitle','')}**\n\n"
                f"{props.get('content','')}"
            )
            updates["card"] = gr.update(visible=True, value=md)

        elif comp == "select":
            labels = [o.get("label", "") for o in props.get("options", [])]
            updates["select"] = gr.update(visible=True, choices=labels)

        elif comp == "form":
            updates["form"] = gr.update(
                visible=True,
                value=json.dumps(props, indent=2)
            )

        elif comp == "checkbox":
            # assumiamo un singolo campo checkbox
            fields = props.get("fields", [])
            if fields:
                opts = [o.get("label", "") for o in fields[0].get("options", [])]
                updates["checkbox"] = gr.update(visible=True, choices=opts)

        elif comp == "grid":
            updates["grid"] = gr.update(
                visible=True,
                value=json.dumps(props, indent=2)
            )

        elif comp == "table":
            updates["table"] = gr.update(
                visible=True,
                value=json.dumps(props, indent=2)
            )

        elif comp == "image":
            updates["image"] = gr.update(
                visible=True,
                value=props.get("url", None)
            )

        elif comp == "modal":
            md = f"### {props.get('title','')}\n{props.get('content','')}"
            updates["modal"] = gr.update(visible=True, value=md)

        elif comp == "progress":
            updates["progress"] = gr.update(
                visible=True,
                value=props.get("value", 0)
            )

        elif comp == "input":
            updates["input"] = gr.update(
                visible=True,
                value=""
            )

        elif comp == "file":
            updates["file"] = gr.update(visible=True)

        elif comp == "wizard":
            updates["wizard"] = gr.update(
                visible=True,
                value=json.dumps(props, indent=2)
            )

    return updates


def test_all_components():
    """Test automatico: invia tutti i componenti e mostra l'ultimo ricevuto."""
    global event_log, last_event
    event_log = []
    last_event = None

    send_run_message()
    time.sleep(1)

    for c in COMPONENTS:
        send_event(c)
        time.sleep(1.2)

    # aspetta un attimo che arrivino gli eventi
    time.sleep(1)

    log_text = "\n".join(event_log)
    updates = handle_event(last_event)

    return (
        log_text,
        updates["text"],
        updates["buttons"],
        updates["actions"],
        updates["card"],
        updates["list"],
        updates["select"],
        updates["form"],
        updates["checkbox"],
        updates["grid"],
        updates["table"],
        updates["image"],
        updates["modal"],
        updates["progress"],
        updates["input"],
        updates["file"],
        updates["wizard"],
    )


def test_single_component(component):
    """Test di un singolo componente."""
    global event_log, last_event
    event_log = []
    last_event = None

    send_run_message()
    time.sleep(1)

    send_event(component)
    time.sleep(1.2)

    time.sleep(1)

    log_text = "\n".join(event_log)
    updates = handle_event(last_event)

    return (
        log_text,
        updates["text"],
        updates["buttons"],
        updates["actions"],
        updates["card"],
        updates["list"],
        updates["select"],
        updates["form"],
        updates["checkbox"],
        updates["grid"],
        updates["table"],
        updates["image"],
        updates["modal"],
        updates["progress"],
        updates["input"],
        updates["file"],
        updates["wizard"],
    )


with gr.Blocks(title="AG-UI Client") as demo:
    gr.Markdown("# 🧪 Client AG‑UI (Gradio)")
    gr.Markdown("Mostra l'elenco degli eventi AG‑UI e il componente corrispondente all'ultimo evento.")

    event_log_box = gr.Textbox(label="Eventi ricevuti (JSON)", lines=20)

    text_output = gr.Textbox(label="Text", visible=False)
    buttons_output = gr.Radio([], label="Buttons", visible=False)
    actions_output = gr.Radio([], label="Actions", visible=False)
    card_output = gr.Markdown(visible=False)
    list_output = gr.Textbox(label="List", visible=False)
    select_output = gr.Dropdown([], label="Select", visible=False)
    form_output = gr.Textbox(label="Form (JSON props)", visible=False)
    checkbox_output = gr.CheckboxGroup([], label="Checkbox", visible=False)
    grid_output = gr.Textbox(label="Grid (JSON props)", visible=False)
    table_output = gr.Textbox(label="Table (JSON props)", visible=False)
    image_output = gr.Image(label="Image", visible=False)
    modal_output = gr.Markdown(label="Modal", visible=False)
    progress_output = gr.Slider(0, 100, label="Progress", visible=False)
    input_output = gr.Textbox(label="Input", visible=False)
    file_output = gr.File(label="File Upload", visible=False)
    wizard_output = gr.Textbox(label="Wizard (JSON props)", visible=False)

    with gr.Row():
        auto_btn = gr.Button("Test automatico di tutti i componenti")
        dropdown = gr.Dropdown(COMPONENTS, label="Test singolo componente")
        manual_btn = gr.Button("Esegui test componente selezionato")

    start_sse_listener()

    auto_btn.click(
        fn=test_all_components,
        outputs=[
            event_log_box,
            text_output,
            buttons_output,
            actions_output,
            card_output,
            list_output,
            select_output,
            form_output,
            checkbox_output,
            grid_output,
            table_output,
            image_output,
            modal_output,
            progress_output,
            input_output,
            file_output,
            wizard_output,
        ],
    )

    manual_btn.click(
        fn=test_single_component,
        inputs=dropdown,
        outputs=[
            event_log_box,
            text_output,
            buttons_output,
            actions_output,
            card_output,
            list_output,
            select_output,
            form_output,
            checkbox_output,
            grid_output,
            table_output,
            image_output,
            modal_output,
            progress_output,
            input_output,
            file_output,
            wizard_output,
        ],
    )

demo.launch()
