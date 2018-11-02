package bot;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.http.HttpResponse;
import org.apache.http.client.HttpClient;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.config.Registry;
import org.apache.http.config.RegistryBuilder;
import org.apache.http.conn.socket.ConnectionSocketFactory;
import org.apache.http.conn.socket.PlainConnectionSocketFactory;
import org.apache.http.conn.ssl.NoopHostnameVerifier;
import org.apache.http.conn.ssl.SSLConnectionSocketFactory;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClientBuilder;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.impl.conn.PoolingHttpClientConnectionManager;
import org.telegram.telegrambots.bots.TelegramLongPollingBot;
import org.telegram.telegrambots.meta.api.methods.send.SendMessage;
import org.telegram.telegrambots.meta.api.objects.Update;
import org.telegram.telegrambots.meta.exceptions.TelegramApiException;

import javax.net.ssl.SSLContext;
import java.io.*;
import java.security.NoSuchAlgorithmException;


public class Bot extends TelegramLongPollingBot {

    private static String botTocken = "456016067:AAGb6DJILBE3nvE_qFoKP7CK5SwaShV_RlQ";
    private static String userName = "just bot";
    private String telegramApi;
    private long chatId;

    public long getChatId() {
        return chatId;
    }

    public String getTelegramApi() {
        return telegramApi;
    }

    public void setTelegramApi(String telegramApi) {
        this.telegramApi = telegramApi;
    }

    @Override
    public void onUpdateReceived(Update update) {
    }

    @Override
    public String getBotUsername() {
        return userName;
    }

    @Override
    public String getBotToken() {
        return botTocken;
    }

    public void sendSuccess() throws TelegramApiException {
        execute(new SendMessage(new Long(chatId), "Hello"));
    }

    public void sendMessage(String text) throws TelegramApiException {
//        execute(new SendMessage(new Long(chatId), text));
        try {
            sendMessageHttp(text);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    public void sendMessageHttp(String text) throws IOException {
        String urlString = "%s/bot%s/sendMessage";

        String apiToken = "my_bot_api_token";
//        String message = "{\"text\":\"Hello world!\",\"chat_id\":113856118} ";
        Message message = new Message(chatId, text);
        urlString = String.format(urlString, telegramApi, botTocken);
        ObjectMapper objectMapper = new ObjectMapper();
        String payload = objectMapper.writeValueAsString(message);
        StringEntity entity = new StringEntity(payload,
                ContentType.APPLICATION_JSON);
        final SSLConnectionSocketFactory sslsf;
        try {
            sslsf = new SSLConnectionSocketFactory(SSLContext.getDefault(),
                    NoopHostnameVerifier.INSTANCE);
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException(e);
        }

        final Registry<ConnectionSocketFactory> registry = RegistryBuilder.<ConnectionSocketFactory>create()
                .register("http", new PlainConnectionSocketFactory())
                .register("https", sslsf)
                .build();

        final PoolingHttpClientConnectionManager cm = new PoolingHttpClientConnectionManager(registry);
        cm.setMaxTotal(100);
        HttpClient httpClient = HttpClients.custom()
                .setSSLSocketFactory(sslsf)
                .setConnectionManager(cm)
                .build();
        HttpPost request = new HttpPost(urlString);
        request.setEntity(entity);
        System.out.println(payload);
        HttpResponse response = httpClient.execute(request);
        System.out.println(response.getStatusLine().getStatusCode());
    }

    public void setChatId(long chatId) {
        this.chatId = chatId;
    }
}
