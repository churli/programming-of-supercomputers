package settings;

public class Settings {
    private String startingFolder;
    private String finalFolder;
    private long chatId;
    private int updateTime;

    public int getUpdateTime() {
        return updateTime;
    }

    public void setUpdateTime(int updateTime) {
        this.updateTime = updateTime;
    }

    public String getStartingFolder() {
        return startingFolder;
    }

    public void setStartingFolder(String startingFolder) {
        this.startingFolder = startingFolder;
    }

    public String getFinalFolder() {
        return finalFolder;
    }

    public void setFinalFolder(String finalFolder) {
        this.finalFolder = finalFolder;
    }

    public long getChatId() {
        return chatId;
    }

    public void setChatId(long chatId) {
        this.chatId = chatId;
    }
}
