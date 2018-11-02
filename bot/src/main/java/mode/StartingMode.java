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
    private final static String jobIdEnv = "jobid";

    private void writeStartingMessage() {
        try {
            StartingMessage startingNote = new StartingMessage();
            startingNote.setJobId(jobId);
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
        jobId = System.getenv(jobIdEnv);
    }

    @Override
    public void start() {
        writeStartingMessage();
    }
}
