import os
from datetime import datetime
from datetime import timedelta

# delimiter for data file
CTRL_A = chr(1)

# used to filter out out of bounds data
minDate = datetime(2013, 5, 23)
delta = timedelta(days=2)

# hold the summary so we can write it out later
engines = {}

# control the number for rows to analyze
rows = 0

# each snapshot is a full copy of the FHR data so we need to limit to a desired
# snapshot
activeSnapshot = "2014-05-26"

with open("search_counts.may2014") as inFile:
  for line in inFile:
    #rows += 1
    #if rows > 100:
      #break
    #line = line.replace(CTRL_A, ",")
    #values = line.split(",")
    values = line.split(CTRL_A)
    if len(values) < 13:
      # let's see why this line does not have enough values
      print "bad line: " + line.replace(CTRL_A, " | ")
      continue

    # only use the desired snapshot
    if activeSnapshot <> values[0]:
      continue

    # parse the dates quickly since we know the format is fixed
    searchDate = datetime(int(values[2][0:4]), int(values[2][5:7]), int(values[2][8:10]))
    snapshotDate = datetime(int(values[0][0:4]), int(values[0][5:7]), int(values[0][8:10]))

    # filter out of bound data
    if searchDate < minDate or searchDate > snapshotDate + delta:
      continue

    # grab the search counts
    count = values[13]

    # normalize the 'other' engines a little
    engine = values[10]
    if engine.find("other-") == 0:
      if engine.find("DuckDuckGo") != -1:
        engine = "other-duckduckgo"
      else:
        engine = "other"

    # create a comma delimited code to make it easy to import and post-process
    # group by year-month, first-day-of-month and engine
    code = searchDate.strftime("%Y-%m") + "-01," + engine

    # update the count
    engines[code] = engines.get(code, 0) + int(count)

# dump out the engine summary
with open("engine-summary.txt", "w") as outFile:
  keys = engines.viewkeys()
  for key in keys:
    print key
    outFile.write(key + "," + str(engines[key]) + "\n")
