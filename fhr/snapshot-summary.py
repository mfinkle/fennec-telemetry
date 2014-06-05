import os

# delimiter for data file
CTRL_A = chr(1)

# hold the summary so we can write it out later
snapshots = {}

# control the number for rows to analyze
rows = 0

with open("search_counts.may2014") as inFile:
  for line in inFile:
    #rows += 1
    #if rows > 100:
      #break
    values = line.split(CTRL_A)
    if len(values) < 13:
      # let's see why this line does not have enough values
      print "bad line: " + line.replace(CTRL_A, " | ")
      continue

    # update snapshots
    snapshots[values[0]] = 1

# dump out the snapshot summary
with open("snapshot-summary.txt", "w") as outFile:
  keys = snapshots.viewkeys()
  for key in keys:
    print key
    outFile.write(key + "\n")
