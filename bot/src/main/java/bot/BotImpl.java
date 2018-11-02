package bot;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import message.FinishingMessage;
import message.StartingMessage;
import org.telegram.telegrambots.meta.exceptions.TelegramApiException;
import report.FinalReport;

import java.io.File;
import java.io.IOException;

public class BotImpl extends Bot {
    final private static String startingMessageTemplate = "Job %s started";

    public BotImpl() {
    }

    public void sendStartMessage(StartingMessage startingMessage) {
        String message = String.format(startingMessageTemplate, startingMessage.getJobId());
        try {
            sendMessage(message);

        } catch (TelegramApiException e) {
            e.printStackTrace();
        }
    }

    public void sendFinalReport(StartingMessage startingMessage, FinishingMessage finishingMessage
    ) {
        FinalReport report = new FinalReport();
        ObjectMapper mapper = new ObjectMapper(new YAMLFactory());

        try {
            report.init(startingMessage, finishingMessage);
            String text = mapper.writeValueAsString(report);
            sendMessage(text);
        } catch (IOException e) {
            e.printStackTrace();
        } catch (TelegramApiException e) {
            e.printStackTrace();
        }


    }
}
