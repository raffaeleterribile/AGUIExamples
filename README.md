Comandi per ricreare l'ambiente.

```
pip install agent-framework-ag-ui --pre
pip install agent-framework-devui --pre
```

interfaccia di sviluppo devUI

```
# Launch web UI + API server
devui ./agents --port 8080
# Web UI: http://localhost:8080
# API: http://localhost:8080/v1/*
```

```
uvicorn server:app --reload
```

Sì Raffaele — ti preparo **il catalogo completo dei componenti AG‑UI**, tutti in un’unica risposta, tutti con:

- descrizione chiara  
- JSON minimo funzionante  
- quando usarli  
- cosa inviano come eventi  

E ogni voce è cliccabile per approfondire grazie ai Guided Links.

---

## 📘 **Catalogo completo dei componenti AG‑UI**

### 🟦 1. **Text**  
Il componente più semplice: mostra testo puro.

```json
{
  "type": "text",
  "text": "Questo è un messaggio di testo."
}
```

---

### 🟩 2. **Buttons**  
Serie di bottoni cliccabili.

```json
{
  "type": "component",
  "component": "buttons",
  "props": {
    "buttons": [
      {"label": "Uno", "value": "uno"},
      {"label": "Due", "value": "due"}
    ]
  }
}
```

---

### 🟧 3. **Actions**  
Toolbar di azioni (simile ai bottoni, ma semantica diversa).

```json
{
  "type": "actions",
  "actions": [
    {"id": "search", "label": "Cerca"},
    {"id": "save", "label": "Salva"}
  ]
}
```

---

### 🟥 4. **Card**  
Card informativa con titolo, contenuto e azioni.

```json
{
  "type": "component",
  "component": "card",
  "props": {
    "title": "Titolo",
    "subtitle": "Sottotitolo",
    "content": "Contenuto della card.",
    "actions": [
      {"label": "Apri", "value": "open"}
    ]
  }
}
```

---

### 🟦 5. **List**  
Lista di elementi testuali.

```json
{
  "type": "component",
  "component": "list",
  "props": {
    "title": "Lista",
    "items": ["Uno", "Due", "Tre"]
  }
}
```

---

### 🟩 6. **Select**  
Menu a tendina.

```json
{
  "type": "component",
  "component": "select",
  "props": {
    "label": "Scegli",
    "options": [
      {"label": "A", "value": "a"},
      {"label": "B", "value": "b"}
    ]
  }
}
```

---

### 🟧 7. **Form**  
Form con campi input, checkbox, numerici, ecc.

```json
{
  "type": "component",
  "component": "form",
  "props": {
    "title": "Inserisci dati",
    "fields": [
      {"id": "nome", "label": "Nome", "type": "text"},
      {"id": "eta", "label": "Età", "type": "number"}
    ],
    "submit": {"label": "Invia", "value": "submit_form"}
  }
}
```

---

### 🟥 8. **Checkbox list**  
Multi‑selezione tramite form.

```json
{
  "type": "component",
  "component": "form",
  "props": {
    "title": "Seleziona",
    "fields": [
      {
        "id": "scelte",
        "label": "Opzioni",
        "type": "checkbox",
        "options": [
          {"label": "Uno", "value": "uno"},
          {"label": "Due", "value": "due"}
        ]
      }
    ],
    "submit": {"label": "Conferma", "value": "submit_checkbox"}
  }
}
```

---

### 🟦 9. **Grid**  
Layout a colonne.

```json
{
  "type": "component",
  "component": "grid",
  "props": {
    "columns": 3,
    "items": [
      {"title": "Item 1", "content": "Contenuto 1"},
      {"title": "Item 2", "content": "Contenuto 2"}
    ]
  }
}
```

---

### 🟩 10. **Table**  
Tabella con righe e colonne.

```json
{
  "type": "component",
  "component": "table",
  "props": {
    "columns": [
      {"label": "Nome", "id": "nome"},
      {"label": "Età", "id": "eta"}
    ],
    "rows": [
      {"nome": "Mario", "eta": 30},
      {"nome": "Luca", "eta": 25}
    ]
  }
}
```

---

### 🟧 11. **Image**  
Mostra un’immagine.

```json
{
  "type": "component",
  "component": "image",
  "props": {
    "url": "https://example.com/img.png",
    "caption": "Immagine di esempio"
  }
}
```

---

### 🟥 12. **Modal**  
Finestra modale.

```json
{
  "type": "component",
  "component": "modal",
  "props": {
    "title": "Attenzione",
    "content": "Messaggio importante",
    "actions": [
      {"label": "OK", "value": "ok"}
    ]
  }
}
```

---

### 🟦 13. **Progress**  
Barra di progresso.

```json
{
  "type": "component",
  "component": "progress",
  "props": {
    "value": 70,
    "label": "Caricamento..."
  }
}
```

---

### 🟩 14. **Input**  
Campo input singolo (alternativa al form).

```json
{
  "type": "component",
  "component": "input",
  "props": {
    "label": "Scrivi qualcosa",
    "placeholder": "Testo...",
    "submit": {"label": "Invia", "value": "submit_input"}
  }
}
```

---

### 🟧 15. **File upload**  
Caricamento file.

```json
{
  "type": "component",
  "component": "file",
  "props": {
    "label": "Carica un file",
    "accept": ["pdf", "txt"]
  }
}
```

---

### 🟥 16. **Wizard / Stepper**  
UI multi‑step.

```json
{
  "type": "component",
  "component": "wizard",
  "props": {
    "steps": [
      {"title": "Step 1", "content": "Contenuto 1"},
      {"title": "Step 2", "content": "Contenuto 2"}
    ]
  }
}
```

---

## 🎉 Vuoi il **catalogo completo con esempi server + client React**?

Posso generare:

- un progetto FastAPI con endpoint `/run`, `/events`, `/event`  
- un client React che renderizza **tutti** i componenti  
- un menu per provarli uno alla volta  


Assolutamente sì, Raffaele — possiamo creare **modelli Pydantic** per rappresentare i componenti AG‑UI, così invece di scrivere JSON a mano puoi costruire oggetti Python tipizzati, comodi da validare e da riutilizzare.

Qui sotto ti preparo:

- una **base class** per tutti i componenti AG‑UI  
- modelli Pydantic per **text**, **buttons**, **list**, **card**, **form**, **select**, **grid**, **table**, **actions**, **checkbox**  
- un **renderer** che converte automaticamente i modelli in JSON AG‑UI  
- esempi di utilizzo

Tutto pronto da copiare nel tuo progetto FastAPI.

---

# 🟦 1. Base class AG‑UI

```python
from pydantic import BaseModel
from typing import List, Optional, Any


class AGUIBase(BaseModel):
    type: str = "component"
    component: str

    def to_json(self) -> dict:
        return self.dict()
```

---

# 🟩 2. Componenti AG‑UI in Pydantic

## ✔ Text

```python
class AGUIText(BaseModel):
    type: str = "text"
    text: str
```

---

## ✔ Buttons

```python
class AGUIButton(BaseModel):
    label: str
    value: str

class AGUIButtons(AGUIBase):
    component: str = "buttons"
    props: dict
```

Helper:

```python
def Buttons(buttons: List[AGUIButton], title: Optional[str] = None):
    return AGUIButtons(
        props={
            "title": title,
            "buttons": [b.dict() for b in buttons]
        }
    )
```

---

## ✔ List

```python
class AGUIList(AGUIBase):
    component: str = "list"
    props: dict
```

Helper:

```python
def ListComponent(title: str, items: List[str]):
    return AGUIList(
        props={"title": title, "items": items}
    )
```

---

## ✔ Card

```python
class AGUICardAction(BaseModel):
    label: str
    value: str

class AGUICard(AGUIBase):
    component: str = "card"
    props: dict
```

Helper:

```python
def Card(title: str, subtitle: str, content: str, actions: List[AGUICardAction]):
    return AGUICard(
        props={
            "title": title,
            "subtitle": subtitle,
            "content": content,
            "actions": [a.dict() for a in actions]
        }
    )
```

---

## ✔ Select

```python
class AGUISelectOption(BaseModel):
    label: str
    value: str

class AGUISelect(AGUIBase):
    component: str = "select"
    props: dict
```

Helper:

```python
def Select(label: str, options: List[AGUISelectOption]):
    return AGUISelect(
        props={
            "label": label,
            "options": [o.dict() for o in options]
        }
    )
```

---

## ✔ Form (input, number, checkbox)

```python
class AGUIFormField(BaseModel):
    id: str
    label: str
    type: str
    placeholder: Optional[str] = None
    options: Optional[List[dict]] = None

class AGUIFormSubmit(BaseModel):
    label: str
    value: str

class AGUIForm(AGUIBase):
    component: str = "form"
    props: dict
```

Helper:

```python
def Form(title: str, fields: List[AGUIFormField], submit: AGUIFormSubmit):
    return AGUIForm(
        props={
            "title": title,
            "fields": [f.dict() for f in fields],
            "submit": submit.dict()
        }
    )
```

---

## ✔ Grid

```python
class AGUIGridItem(BaseModel):
    title: str
    content: str

class AGUIGrid(AGUIBase):
    component: str = "grid"
    props: dict
```

Helper:

```python
def Grid(columns: int, items: List[AGUIGridItem]):
    return AGUIGrid(
        props={
            "columns": columns,
            "items": [i.dict() for i in items]
        }
    )
```

---

## ✔ Table

```python
class AGUITableColumn(BaseModel):
    label: str
    id: str

class AGUITable(AGUIBase):
    component: str = "table"
    props: dict
```

Helper:

```python
def Table(columns: List[AGUITableColumn], rows: List[dict]):
    return AGUITable(
        props={
            "columns": [c.dict() for c in columns],
            "rows": rows
        }
    )
```

---

## ✔ Actions

```python
class AGUIAction(BaseModel):
    id: str
    label: str

class AGUIActions(AGUIBase):
    component: str = "actions"
    actions: List[AGUIAction]
```

Helper:

```python
def Actions(actions: List[AGUIAction]):
    return AGUIActions(actions=actions)
```

---

# 🟦 3. Esempio di utilizzo nel tuo server FastAPI

```python
@app.post("/agent/event")
async def agent_event(request: Request):
    data = await request.json()
    value = data.get("value")

    if value == "lista":
        component = ListComponent("Lista di esempio", ["Uno", "Due", "Tre"])

    elif value == "card":
        component = Card(
            "Titolo card",
            "Sottotitolo",
            "Contenuto della card",
            [AGUICardAction(label="OK", value="ok")]
        )

    elif value == "form":
        component = Form(
            "Inserisci dati",
            [
                AGUIFormField(id="nome", label="Nome", type="text"),
                AGUIFormField(id="eta", label="Età", type="number")
            ],
            AGUIFormSubmit(label="Invia", value="submit_form")
        )

    else:
        component = AGUIText(text="Componente non riconosciuto")

    await event_queue.put(component.to_json())
    return {"status": "ok"}
```

---

# 🟩 4. Vantaggi del modello Pydantic

- ✔ niente JSON scritto a mano  
- ✔ validazione automatica  
- ✔ autocompletamento in IDE  
- ✔ componenti riutilizzabili  
- ✔ codice più pulito e leggibile  
- ✔ facile estendere con nuovi componenti  

---

# 🔥 Vuoi che ti generi anche:

- un **modulo Python completo** `agui.py` con tutti i componenti già pronti?  
- un **builder fluente** tipo:

```python
Buttons()
  .title("Scegli")
  .add("Uno", "uno")
  .add("Due", "due")
```

- oppure un **factory dinamico** che crea componenti AG‑UI da un LLM?

Sì, Raffaele — ti preparo **un modulo Python completo `agui.py`**, elegante, tipizzato, riutilizzabile, che contiene **tutti i componenti AG‑UI** già pronti come classi Pydantic + builder helper.

Il risultato è un file unico che puoi importare nel tuo server FastAPI:

```python
from agui import Text, Buttons, Button, ListComponent, Card, CardAction, Form, FormField, FormSubmit, Select, SelectOption, Grid, GridItem, Table, TableColumn, Actions, Action
```

e poi generare componenti AG‑UI così:

```python
await event_queue.put(
    Buttons([
        Button("Uno", "uno"),
        Button("Due", "due")
    ]).to_json()
)
```

---

# 📁 **agui.py — modulo completo AG‑UI**

```python
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# ============================================================
# BASE
# ============================================================

class AGUIBase(BaseModel):
    type: str = "component"
    component: str

    def to_json(self) -> Dict[str, Any]:
        return self.dict()


# ============================================================
# TEXT
# ============================================================

class Text(BaseModel):
    type: str = "text"
    text: str

    def to_json(self):
        return self.dict()


# ============================================================
# BUTTONS
# ============================================================

class Button(BaseModel):
    label: str
    value: str

class Buttons(AGUIBase):
    component: str = "buttons"
    props: Dict[str, Any]

    @staticmethod
    def create(buttons: List[Button], title: Optional[str] = None):
        return Buttons(
            props={
                "title": title,
                "buttons": [b.dict() for b in buttons]
            }
        )


# ============================================================
# LIST
# ============================================================

class ListComponent(AGUIBase):
    component: str = "list"
    props: Dict[str, Any]

    @staticmethod
    def create(title: str, items: List[str]):
        return ListComponent(
            props={"title": title, "items": items}
        )


# ============================================================
# CARD
# ============================================================

class CardAction(BaseModel):
    label: str
    value: str

class Card(AGUIBase):
    component: str = "card"
    props: Dict[str, Any]

    @staticmethod
    def create(title: str, subtitle: str, content: str, actions: List[CardAction]):
        return Card(
            props={
                "title": title,
                "subtitle": subtitle,
                "content": content,
                "actions": [a.dict() for a in actions]
            }
        )


# ============================================================
# SELECT
# ============================================================

class SelectOption(BaseModel):
    label: str
    value: str

class Select(AGUIBase):
    component: str = "select"
    props: Dict[str, Any]

    @staticmethod
    def create(label: str, options: List[SelectOption]):
        return Select(
            props={
                "label": label,
                "options": [o.dict() for o in options]
            }
        )


# ============================================================
# FORM (input, number, checkbox)
# ============================================================

class FormField(BaseModel):
    id: str
    label: str
    type: str
    placeholder: Optional[str] = None
    options: Optional[List[Dict[str, str]]] = None

class FormSubmit(BaseModel):
    label: str
    value: str

class Form(AGUIBase):
    component: str = "form"
    props: Dict[str, Any]

    @staticmethod
    def create(title: str, fields: List[FormField], submit: FormSubmit):
        return Form(
            props={
                "title": title,
                "fields": [f.dict() for f in fields],
                "submit": submit.dict()
            }
        )


# ============================================================
# GRID
# ============================================================

class GridItem(BaseModel):
    title: str
    content: str

class Grid(AGUIBase):
    component: str = "grid"
    props: Dict[str, Any]

    @staticmethod
    def create(columns: int, items: List[GridItem]):
        return Grid(
            props={
                "columns": columns,
                "items": [i.dict() for i in items]
            }
        )


# ============================================================
# TABLE
# ============================================================

class TableColumn(BaseModel):
    label: str
    id: str

class Table(AGUIBase):
    component: str = "table"
    props: Dict[str, Any]

    @staticmethod
    def create(columns: List[TableColumn], rows: List[Dict[str, Any]]):
        return Table(
            props={
                "columns": [c.dict() for c in columns],
                "rows": rows
            }
        )


# ============================================================
# ACTIONS
# ============================================================

class Action(BaseModel):
    id: str
    label: str

class Actions(AGUIBase):
    component: str = "actions"
    actions: List[Action]

    @staticmethod
    def create(actions: List[Action]):
        return Actions(actions=actions)
```

---

# 🚀 **Esempi di utilizzo nel tuo server FastAPI**

### ✔ Bottoni

```python
from agui import Buttons, Button

await event_queue.put(
    Buttons.create([
        Button(label="Uno", value="uno"),
        Button(label="Due", value="due")
    ]).to_json()
)
```

### ✔ Lista

```python
from agui import ListComponent

await event_queue.put(
    ListComponent.create("Lista di esempio", ["A", "B", "C"]).to_json()
)
```

### ✔ Card

```python
from agui import Card, CardAction

await event_queue.put(
    Card.create(
        "Titolo",
        "Sottotitolo",
        "Contenuto della card",
        [CardAction(label="OK", value="ok")]
    ).to_json()
)
```

### ✔ Form con checkbox

```python
from agui import Form, FormField, FormSubmit

await event_queue.put(
    Form.create(
        "Seleziona",
        [
            FormField(
                id="scelte",
                label="Opzioni",
                type="checkbox",
                options=[
                    {"label": "Uno", "value": "uno"},
                    {"label": "Due", "value": "due"}
                ]
            )
        ],
        FormSubmit(label="Invia", value="submit_checkbox")
    ).to_json()
)
```

---

# 🎉 Vuoi che aggiunga anche:

- un **builder fluente** tipo:

```python
ButtonsBuilder().title("Scegli").add("Uno", "uno").add("Due", "due").build()
```

- un **factory dinamico** per generare componenti AG‑UI da un LLM?
- un **sistema di routing** per gestire stati conversazionali complessi?



Sì, Raffaele — avviare il **client React AG‑UI** è semplice.  
Hai già tutto il progetto: ora ti spiego **esattamente** cosa fare, passo‑passo, senza dare nulla per scontato.

---

## 🚀 **1. Entra nella cartella del progetto**

Se hai chiamato la cartella:

```
agui-client-react/
```

allora:

```
cd agui-client-react
```

---

## 🚀 **2. Installa le dipendenze**

Serve **Node.js ≥ 18**.

Poi:

```
npm install
```

Questo installa:

- React  
- Vite  
- @agui/react (renderer ufficiale AG‑UI)  
- tutte le dipendenze del progetto  

---

## 🚀 **3. Avvia il client React**

```
npm run dev
```

Vite ti risponderà con qualcosa tipo:

```
  VITE v5.0.0  ready in 300ms

  ➜  Local:   http://localhost:5173/
```

Apri il browser su:

👉 **http://localhost:5173**

---

## 🚀 **4. Assicurati che il server FastAPI sia attivo**

Il client React si collega via SSE a:

```
http://localhost:8000/agent/events
```

Quindi devi avere il server avviato:

```
uvicorn server:app --reload
```

---

## 🎉 **5. Cosa vedrai nel client React**

- Un pannello con:
  - **Test automatico** (invia tutti i componenti AG‑UI)
  - **Test singolo componente** (dropdown)
- Una sezione **Eventi ricevuti** con tutto il JSON AG‑UI
- Una sezione **Rendering AG‑UI** con i componenti reali:
  - Card  
  - Buttons  
  - List  
  - Table  
  - Grid  
  - Modal  
  - Wizard  
  - ecc.

Tutto renderizzato tramite:

**`<AGUIRenderer event={currentComponent} />`**

che è il renderer ufficiale AG‑UI.

---

## 🧠 Vuoi anche:

- avvio in modalità produzione  
- versione TypeScript  
- versione Next.js  
- integrazione con un LLM reale  

Dimmi tu cosa vuoi aggiungere.