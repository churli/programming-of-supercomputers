package mode;

public class ModeFactory {
    public IMode createMode(String mode) {
        switch (mode) {
            case "starting":
                return new StartingMode();
            case "finishing":
                return new FinishingMode();
            case "run":
                return new RunningMode();
        }
        return null;
    }
}
