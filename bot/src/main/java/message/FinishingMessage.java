package message;

import java.util.Calendar;
import java.util.Date;

public class FinishingMessage extends Message{

    public String getJobId() {
        return jobId;
    }

    public void setJobId(String jobId) {
        this.jobId = jobId;
    }
    public FinishingMessage() {

    }
    public void init() {
        super.init();
    }

    public Date getFinishingTime() {
        return date;
    }
    public void setFinishingTime(Date finishingTime) {
        setDate(finishingTime);
    }

}
