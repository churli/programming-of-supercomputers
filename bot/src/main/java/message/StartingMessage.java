package message;

import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;

public class StartingMessage extends Message {
    private String executable = "";
    private String jobName = "";

    public String getJobName() {
        return jobName;
    }

    public void setJobName(String jobName) {
        this.jobName = jobName;
    }

    private static final String executableCommand = "executable";
    private static final String jobNameCommand = "job_name";
    private static final String jobNameEnv = "LOADL_JOB_NAME";
    private static final String executableEnv = "LOADL_HOSTFILE";


    public String getExecutable() {
        return executable;
    }

    public void setExecutable(String executable) {
        this.executable = executable;
    }

    public String getJobId() {
        return jobId;
    }

    public void setJobId(String jobId) {
        this.jobId = jobId;
    }

    public void init() {
        super.init();
        jobName = System.getenv(jobNameEnv);
        executable = System.getenv(executableEnv);
//        try {
//            executable = runShell(new String[] {executableCommand});
//            jobName = runShell(new String[] {jobNameCommand});
//        } catch (IOException | InterruptedException e) {
//            e.printStackTrace();
//        }
    }
    public StartingMessage() {

    }

    public Date getStartingTime() {
        return date;
    }

    public void setStartingTime(Date startingTime) {
        setDate(startingTime);
    }
}
