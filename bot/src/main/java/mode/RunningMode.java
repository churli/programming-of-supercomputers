package mode;

import bot.BotImpl;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import message.FinishingMessage;
import message.StartingMessage;
import settings.Settings;

import java.io.File;
import java.io.IOException;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

public class RunningMode implements IMode {
    private BotImpl bot;
    private int updateTimer;
    private String startingFolder;
    private String finishingFolder;
    private Set<String> startedJobs;
    private Set<String> finishedJobs;

    private Set<String> getFilesFromFolder(String folderPath) {
        File folder = new File(folderPath);
        File[] files = folder.listFiles();
        HashSet<String> result = new HashSet<>();
        for (File file : files) {
            result.add(file.getAbsolutePath());
        }
        return result;
    }

    @Override
    public void init(Settings settings) {
        bot = new BotImpl(settings.getTelegramApi());
        bot.setChatId(settings.getChatId());
        updateTimer = settings.getUpdateTime();
        startingFolder = settings.getStartingFolder();
        finishingFolder = settings.getFinalFolder();
        startedJobs = getFilesFromFolder(startingFolder);
        finishedJobs = getFilesFromFolder(finishingFolder);
    }

    public void run() throws InterruptedException, IOException {
        while (true) {
            TimeUnit.SECONDS.sleep(updateTimer);
            Set<String> newStarted = getFilesFromFolder(startingFolder);
            Set<String> updateSet = new HashSet<>(newStarted);
            newStarted.removeAll(startedJobs);
            ObjectMapper mapper = new ObjectMapper(new YAMLFactory());

            for (String newStartedPath : newStarted) {
                StartingMessage message = mapper.readValue(new File(newStartedPath), StartingMessage.class);
                bot.sendStartMessage(message);
            }
            startedJobs = updateSet;

            Set<String> newFinishedJobs = getFilesFromFolder(finishingFolder);
            updateSet = new HashSet<>(newFinishedJobs);
            newFinishedJobs.removeAll(finishedJobs);
            for (String newFinishedPath : newFinishedJobs) {
                String jobId = Naming.getIdFromPath(newFinishedPath);
                FinishingMessage finishingMessage = mapper.readValue(new File(newFinishedPath), FinishingMessage.class);

                String newStartedPath = Naming.getStartingName(startingFolder, jobId);
                try {
                    StartingMessage message = mapper.readValue(new File(newStartedPath), StartingMessage.class);
                    bot.sendFinalReport(message, finishingMessage);
                } catch (IOException startingExc) {

                }
            }
            finishedJobs = updateSet;

        }
    }

    @Override
    public void start() {
        try {
            run();
        } catch (InterruptedException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
