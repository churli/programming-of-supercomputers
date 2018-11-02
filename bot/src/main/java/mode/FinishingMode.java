package mode;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import message.FinishingMessage;
import settings.Settings;

import java.io.File;
import java.io.IOException;

public class FinishingMode implements IMode {
    private String filePrefix;
    private String jobId;
    private final static String jobIdEnv = "jobid";
    private void writeFinishingMessage() {
        try {
            FinishingMessage finishingNote = new FinishingMessage();
            finishingNote.setJobId(jobId);
            ObjectMapper mapper = new ObjectMapper(new YAMLFactory());
            String fileName = Naming.getFinishingName(filePrefix, jobId);
            mapper.writeValue(new File(fileName),finishingNote);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
    @Override
    public void init(Settings settings) {
        filePrefix = settings.getFinalFolder();
        jobId = System.getenv(jobIdEnv);
    }

    @Override
    public void start() {
        writeFinishingMessage();
    }
}
