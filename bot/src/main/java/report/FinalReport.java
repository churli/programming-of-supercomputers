package report;

import com.fasterxml.jackson.annotation.JsonPropertyOrder;
import message.FinishingMessage;
import message.StartingMessage;
import org.apache.commons.lang3.time.DurationFormatUtils;


@JsonPropertyOrder({"jobId", "executionTime"})
public class FinalReport {

    private String executionTime ="";
    private String jobId = "";
    private String executable = "";
    private String jobName = "";

    public String getJobId() {
        return jobId;
    }

    public void setJobId(String jobId) {
        this.jobId = jobId;
    }

    public String getExecutionTime() {
        return executionTime;
    }

    public String getExecutable() {
        return executable;
    }

    public void setExecutable(String executable) {
        this.executable = executable;
    }

    public String getJobName() {
        return jobName;
    }

    public void setJobName(String jobName) {
        this.jobName = jobName;
    }

    public void setExecutionTime(String executionTime) {
        this.executionTime = executionTime;
    }

    public String getStatus() {
        return "finished";
    }

    public void init(StartingMessage startingMessage, FinishingMessage finishingMessage) {
        if (!startingMessage.getJobId().equals(finishingMessage.getJobId())) {
            return;
        }
        long finalTime = finishingMessage.getFinishingTime().getTime();
        long startingTime = startingMessage.getStartingTime().getTime();
        long difference = finalTime - startingTime;
        executionTime = DurationFormatUtils.formatDuration(difference, "mm:ss");
        jobId = startingMessage.getJobId();
        executable = startingMessage.getExecutable();
        jobName = startingMessage.getJobName();
    }
}
