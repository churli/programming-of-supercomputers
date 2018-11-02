package bot;

import com.fasterxml.jackson.annotation.JsonProperty;

public class Message {
    private String text;
    private long chatId;
    public Message(long chatId, String text) {
        this.text = text;
        this.chatId = chatId;
    }
    @JsonProperty("chat_id")
    public long getChatId() {
        return  chatId;
    }
    public String getText() {
        return text;
    }
}
