package message;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.Arrays;
import java.util.Calendar;
import java.util.Date;

public abstract class Message {
    String jobId = "";
    Date date;

    private static final String jobIdCommand = "jobid";
    private static final String jobIdEnv = "LOADL_STEP_ID";

    protected void initDate() {
        Calendar cal = Calendar.getInstance();
        date = cal.getTime();
    }

    void setDate(Date date) {
        this.date = date;
    }


    public void init() {
        initDate();
        initJobIdEnv();
    }
    protected void initJobIdEnv() {
        jobId = System.getenv(jobIdEnv);
    }

    protected void initJobId() {
        try {
            jobId = runShell(new String[]{jobIdCommand});
        } catch (IOException e) {
            e.printStackTrace();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }

    String runShell(String[] shellCommand) throws IOException, InterruptedException {

        System.out.println("Executing " + Arrays.toString(shellCommand));
        ProcessBuilder pb = new ProcessBuilder(shellCommand);
        Process process = pb.start();
        BufferedReader reader =
                new BufferedReader(new InputStreamReader(process.getInputStream()));
        StringBuilder builder = new StringBuilder();
        String line = null;
        while ((line = reader.readLine()) != null) {
            builder.append(line);
            builder.append(System.getProperty("line.separator"));
        }
        process.waitFor();

        String result = builder.toString();
        return result;
    }
}
