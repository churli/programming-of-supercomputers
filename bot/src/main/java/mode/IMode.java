package mode;

import settings.Settings;

public interface IMode {
    void init(Settings settings);
    void start();
}
