import com.launchdarkly.eventsource.EventHandler;
import com.launchdarkly.eventsource.EventSource;
import okhttp3.*;
import java.net.URI;
import java.time.Duration;
import java.util.List;
import java.util.Scanner;

public class ClientAGUI {

    private static final String EVENTS_URL = "http://localhost:8000/agent/events";
    private static final String RUN_URL = "http://localhost:8000/agent/run";
    private static final String EVENT_URL = "http://localhost:8000/agent/event";

    private static final OkHttpClient client = new OkHttpClient();

    private static final List<String> COMPONENTS = List.of(
            "text", "buttons", "actions", "card", "list", "select",
            "form", "checkbox", "grid", "table", "image", "modal",
            "progress", "input", "file", "wizard"
    );

    public static void main(String[] args) throws Exception {

        // Avvio listener SSE
        startEventListener();

        // Invio messaggio iniziale
        sendRunMessage();

        Thread.sleep(1000);

        Scanner scanner = new Scanner(System.in);
        System.out.println("\nVuoi eseguire il test automatico di tutti i componenti AG-UI? (s/n): ");
        String answer = scanner.nextLine().trim().toLowerCase();

        if (answer.equals("s")) {
            runAllTests();
        } else {
            runSingleTests(scanner);
        }

        System.out.println("\nAttendo eventuali eventi finali...");
        Thread.sleep(5000);
    }

    // ============================================================
    // SSE LISTENER
    // ============================================================

    private static void startEventListener() {
        EventHandler handler = new EventHandler() {
            @Override
            public void onOpen() {
                System.out.println("Connessione SSE aperta.");
            }

            @Override
            public void onClosed() {
                System.out.println("Connessione SSE chiusa.");
            }

            @Override
            public void onMessage(String event, MessageEvent messageEvent) {
                System.out.println("\n=== EVENTO RICEVUTO ===");
                System.out.println(messageEvent.getData());
            }

            @Override
            public void onComment(String comment) {}

            @Override
            public void onError(Throwable t) {
                System.out.println("Errore SSE: " + t.getMessage());
            }
        };

        EventSource.Builder builder = new EventSource.Builder(handler, URI.create(EVENTS_URL));
        EventSource eventSource = builder
                .reconnectTime(Duration.ofSeconds(2))
                .build();

        eventSource.start();
    }

    // ============================================================
    // INVIO RICHIESTE
    // ============================================================

    private static void sendRunMessage() throws Exception {
        RequestBody body = RequestBody.create(
                "{\"message\":\"Ciao agente!\"}",
                MediaType.parse("application/json")
        );

        Request request = new Request.Builder()
                .url(RUN_URL)
                .post(body)
                .build();

        client.newCall(request).execute().close();
    }

    private static void sendEvent(String value) throws Exception {
        String json = String.format("{\"event\":\"action\",\"value\":\"%s\"}", value);

        RequestBody body = RequestBody.create(
                json,
                MediaType.parse("application/json")
        );

        Request request = new Request.Builder()
                .url(EVENT_URL)
                .post(body)
                .build();

        client.newCall(request).execute().close();
    }

    // ============================================================
    // TEST AUTOMATICO
    // ============================================================

    private static void runAllTests() throws Exception {
        System.out.println("\n>>> Avvio test automatico di tutti i componenti AG-UI...");

        for (String c : COMPONENTS) {
            System.out.println("\n>>> Test componente: " + c);
            sendEvent(c);
            Thread.sleep(1500);
        }
    }

    // ============================================================
    // TEST MANUALE
    // ============================================================

    private static void runSingleTests(Scanner scanner) throws Exception {
        while (true) {
            System.out.println("\n=== MENU COMPONENTI AG-UI ===");
            for (int i = 0; i < COMPONENTS.size(); i++) {
                System.out.println((i + 1) + ". " + COMPONENTS.get(i));
            }
            System.out.println((COMPONENTS.size() + 1) + ". Esci");

            System.out.print("\nSeleziona un numero: ");
            String choiceStr = scanner.nextLine().trim();

            if (!choiceStr.matches("\\d+")) {
                System.out.println("Scelta non valida.");
                continue;
            }

            int choice = Integer.parseInt(choiceStr);

            if (choice == COMPONENTS.size() + 1) {
                System.out.println("Uscita dal programma.");
                return;
            }

            if (choice >= 1 && choice <= COMPONENTS.size()) {
                String component = COMPONENTS.get(choice - 1);
                System.out.println("\n>>> Test componente: " + component);
                sendEvent(component);
                Thread.sleep(1500);
            } else {
                System.out.println("Scelta non valida.");
            }
        }
    }
}
