#!/usr/bin/env python3

# Read a csv file and convert it into the submission format

# Temporary cli format: ./csv2submission.py filename.csv filename.sub.txt

import csv
from sys import argv

csvFile = argv[1]
outFile = argv[2]

results = [] # List of dictionaries

# Reading CSV data
with open(csvFile) as f:
    reader = csv.DictReader(f)
    for row in reader:
        cur = {}
        cur['node'] = 1
        cur['total_tasks'] = row['NumProc']
        cur['time'] = row['ElapsedTimeSec']
        results.append(cur)

with open(outFile, 'w') as f:
    for id,cur in enumerate(results):
        f.write("Test: %d\n" %(id+1))
        f.write("node = %s\n" %(cur['node']))
        f.write("total_tasks = %s\n" %(cur['total_tasks']))
        f.write("time = %s\n" %(cur['time']))
        f.write("\n")

#eof
