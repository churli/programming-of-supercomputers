package message;

import java.util.Calendar;
import java.util.Date;

public class FinishingMessage {
    private Date finishingTime;
    private String jobId;

    public String getJobId() {
        return jobId;
    }

    public void setJobId(String jobId) {
        this.jobId = jobId;
    }
    public FinishingMessage() {
        Calendar cal = Calendar.getInstance();
        finishingTime = cal.getTime();
    }

    public Date getFinishingTime() {
        return finishingTime;
    }
    public void setFinishingTime(Date finishingTime) {
        this.finishingTime = finishingTime;
    }

}
