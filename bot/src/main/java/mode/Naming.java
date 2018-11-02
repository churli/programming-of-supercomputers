package mode;

public class Naming {
    private final static String finishingMessageFileFormat = ".fnsh";
    private final static String startingMessageFileFormat = ".strt";
    private final static String jobIdDelim = "____";

    public static String getStartingName(String prefix, String jobId) {
        return prefix + jobIdDelim + jobId + startingMessageFileFormat;
    }
    public static String getFinishingName(String prefix, String jobId) {
        return prefix + jobIdDelim + jobId + finishingMessageFileFormat;
    }
    public static String getIdFromPath(String path){
        int start = path.indexOf(jobIdDelim);
        return path.substring(start + jobIdDelim.length(), path.length() - finishingMessageFileFormat.length());
    }

}
