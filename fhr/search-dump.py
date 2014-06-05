import os

# delimiter for data file
CTRL_A = chr(1)

# control the number for rows to dump
rows = 0

with open("search_counts.may2014") as inFile:
  outFile = open("search-dump.txt", "w")
  for line in inFile:
    rows += 1
    if rows > 100:
      break

    values = line.split(CTRL_A)
    outFile.write(line)

