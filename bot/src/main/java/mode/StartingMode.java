package mode;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import settings.Settings;
import message.StartingMessage;

import java.io.File;
import java.io.IOException;

public class StartingMode implements IMode {
    private String filePrefix;
    private String jobId;

    private void writeStartingMessage() {
        try {
            StartingMessage startingNote = new StartingMessage();
            startingNote.init();
            jobId = startingNote.getJobId();
            ObjectMapper mapper = new ObjectMapper(new YAMLFactory());
            String fileName = Naming.getStartingName(filePrefix, jobId);
            mapper.writeValue(new File(fileName), startingNote);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    @Override
    public void init(Settings settings) {
        filePrefix = settings.getStartingFolder();
    }

    @Override
    public void start() {
        writeStartingMessage();
    }
}
