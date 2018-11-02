package bot;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpPost;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.StringEntity;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClientBuilder;
import org.telegram.telegrambots.bots.TelegramLongPollingBot;
import org.telegram.telegrambots.meta.api.methods.send.SendMessage;
import org.telegram.telegrambots.meta.api.objects.Update;
import org.telegram.telegrambots.meta.exceptions.TelegramApiException;

import java.io.*;



public class Bot extends TelegramLongPollingBot {

    private static String botTocken = "456016067:AAGb6DJILBE3nvE_qFoKP7CK5SwaShV_RlQ";
    private static String userName = "just bot";

    private long chatId = 113856118;

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
        execute(new SendMessage(new Long(chatId), text));
    }
    public void sendMessageHttp() throws IOException {
        String urlString = "https://api.telegram.org/bot%s/sendMessage";

        String apiToken = "my_bot_api_token";
        String text = "Hello world!";
//        String message = "{\"text\":\"Hello world!\",\"chat_id\":113856118} ";
        Message message = new Message(chatId, text);
        urlString = String.format(urlString, botTocken);
        ObjectMapper objectMapper = new ObjectMapper();
        String payload = objectMapper.writeValueAsString(message);
        StringEntity entity = new StringEntity(payload,
                ContentType.APPLICATION_JSON);

        CloseableHttpClient httpClient = HttpClientBuilder.create().build();
        HttpPost request = new HttpPost(urlString);
        request.setEntity(entity);
        System.out.println(payload);
        CloseableHttpResponse response = httpClient.execute(request);
        System.out.println(response.getStatusLine().getStatusCode());
    }

    public void setChatId(long chatId) {
        this.chatId = chatId;
    }
}
