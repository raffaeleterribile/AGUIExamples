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
