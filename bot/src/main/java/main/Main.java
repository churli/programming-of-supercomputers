package main;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import mode.IMode;
import mode.ModeFactory;
import org.apache.commons.cli.*;
import settings.Settings;

import java.io.File;
import java.io.IOException;

public class Main {

    private CommandLineParser parser;
    HelpFormatter formatter;
    Options options;
    Settings settings;
    String mode;

    public Main() {
        options = new Options();

        Option settings = new Option("s", "settings", true, "yaml settings file");
        settings.setRequired(true);
        options.addOption(settings);

        Option mode = new Option("m", "mode", true, "running mode");
        mode.setRequired(true);
        options.addOption(mode);

        parser = new DefaultParser();
        formatter = new HelpFormatter();
    }

    public void parseArgs(String[] args) throws IOException {
        CommandLine cmd = null;

        try {
            cmd = parser.parse(options, args);
        } catch (ParseException e) {
            System.out.println(e.getMessage());
            formatter.printHelp("utility-name", options);
            System.exit(1);
        }

        String settingsFilePath = cmd.getOptionValue("settings");
        ObjectMapper mapper = new ObjectMapper(new YAMLFactory());
        settings = mapper.readValue(new File(settingsFilePath), Settings.class);
        mode = cmd.getOptionValue("mode");
    }

    private void runBot() {
        ModeFactory factory = new ModeFactory();
        IMode runningMode = factory.createMode(mode);
        runningMode.init(settings);
        runningMode.start();
    }

    public static void main(String[] args) {
        try {
            Main main = new Main();
            main.parseArgs(args);
            main.runBot();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
