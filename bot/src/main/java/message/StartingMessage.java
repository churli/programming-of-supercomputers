package message;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;

public class StartingMessage {
    private Date startingTime;
    private String jobId;

    public String getJobId() {
        return jobId;
    }

    public void setJobId(String jobId) {
        this.jobId = jobId;
    }

    public StartingMessage() {
        Calendar cal = Calendar.getInstance();
        startingTime = cal.getTime();
    }

    public Date getStartingTime() {
        return startingTime;
    }
    public void setStartingTime(Date startingTime) {
        this.startingTime = startingTime;
    }
}
