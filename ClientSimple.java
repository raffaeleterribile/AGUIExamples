import okhttp3.*;
import java.io.IOException;

public class ClientSimple {

    static final String EVENTS_URL = "http://localhost:8000/agent/events";
    static final String RUN_URL = "http://localhost:8000/agent/run";
    static final String EVENT_URL = "http://localhost:8000/agent/event";

    public static void main(String[] args) throws Exception {
        OkHttpClient client = new OkHttpClient();

        // Thread per ascoltare eventi SSE
        new Thread(() -> {
            Request req = new Request.Builder().url(EVENTS_URL).build();
            try (Response res = client.newCall(req).execute()) {
                var source = res.body().source();
                while (!source.exhausted()) {
                    String line = source.readUtf8Line();
                    if (line != null && line.startsWith("data:")) {
                        System.out.println("EVENTO: " + line.substring(5).trim());
                    }
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }).start();

        // Invio messaggio iniziale
        RequestBody body = RequestBody.create(
            "{\"message\":\"Ciao agente!\"}",
            MediaType.parse("application/json")
        );
        client.newCall(new Request.Builder().url(RUN_URL).post(body).build()).execute();

        // Simula click dopo 3 secondi
        Thread.sleep(3000);
        RequestBody ev = RequestBody.create(
            "{\"event\":\"action\",\"value\":\"uno\"}",
            MediaType.parse("application/json")
        );
        client.newCall(new Request.Builder().url(EVENT_URL).post(ev).build()).execute();

        Thread.sleep(10000);
    }
}
