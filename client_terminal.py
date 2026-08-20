import requests
import sseclient
import threading
import time
import json

EVENTS_URL = "http://localhost:8000/agent/events"
RUN_URL = "http://localhost:8000/agent/run"
EVENT_URL = "http://localhost:8000/agent/event"

# Tutti i componenti AG-UI disponibili
COMPONENTS = [
    "text", "buttons", "actions", "card", "list", "select",
    "form", "checkbox", "grid", "table", "image", "modal",
    "progress", "input", "file", "wizard"
]

def listen_events():
    messages = sseclient.SSEClient(EVENTS_URL)
    for msg in messages:
        if msg.data:
            print("\n=== EVENTO RICEVUTO ===")
            print(msg.data)

def send_event(value):
    requests.post(EVENT_URL, json={"event": "action", "value": value})

def run_all_tests():
    print("\n>>> Avvio test automatico di tutti i componenti AG-UI...")
    for c in COMPONENTS:
        print(f"\n>>> Test componente: {c}")
        send_event(c)
        time.sleep(1.5)

def run_single_test():
    while True:
        print("\n=== MENU COMPONENTI AG-UI ===")
        for i, c in enumerate(COMPONENTS, start=1):
            print(f"{i}. {c}")
        print(f"{len(COMPONENTS)+1}. Esci")

        choice = input("\nSeleziona un numero: ").strip()

        if not choice.isdigit():
            print("Scelta non valida.")
            continue

        choice = int(choice)

        if choice == len(COMPONENTS) + 1:
            print("Uscita dal programma.")
            return

        if 1 <= choice <= len(COMPONENTS):
            component = COMPONENTS[choice - 1]
            print(f"\n>>> Test componente: {component}")
            send_event(component)
            time.sleep(1.5)
        else:
            print("Scelta non valida.")

def main():
    # Thread per ascoltare eventi
    listening_thread = threading.Thread(target=listen_events, daemon=True)
    listening_thread.start()

    # Invio messaggio iniziale
    requests.post(RUN_URL, json={"message": "Ciao agente!"})

    time.sleep(1)

    print("\nVuoi eseguire il test automatico di tutti i componenti AG-UI?")
    answer = input("(s/n): ").strip().lower()

    if answer == "s":
        run_all_tests()
    else:
        run_single_test()

    print("\nAttendo eventuali eventi finali...")
    time.sleep(5)

if __name__ == "__main__":
    main()
