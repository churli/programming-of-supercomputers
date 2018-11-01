# programming-of-supercomputers
Reports and data for the course Programming of Supercomputers at TUM (WiSe18).

## How to add material to the repository
Please DO NOT add output files to the repository! To make sure you are not doing that by mistake, you can simply run a `make clean` (more info below!) from within a report subfolder, in this way all output will be deleted.

## How to start a new report
If you have to start worksheet number, let's say, `1`, just run the following command (within the repo base folder):
```
./init-new-report.sh 1
```
This will copy and initalize everything properly into folder `Report_WS1`.

Then add the new folder to git with:
```
git add Report_WS1<number>
```

## How to write the report
Once the report is initialized (still assuming WS1), go into its folder `cd Report_WS1` and edit the `report_WS1.tex` file.

## How to compile the report
Within the report's folder, just hit:
```
make
```
Output will be placed into the `Out/` subfolder.

## How to auto-compile every time I save the source file
Within the report's folder, just run:
```
make autocompile
```
This will wait for changes in all the various `.tex` source files and recompile as soon as one is detected. So every time you save some changes, the PDF will be automatically updated.

WARNING: This requires the `evince` PDF reader to be installed.

## How to clean all output
In case you want to clean all compilation output:
```
make clean
```

Enjoy! :)

