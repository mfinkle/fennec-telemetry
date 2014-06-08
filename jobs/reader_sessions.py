# -*- coding: utf-8 -*-

import csv
import io
import simplejson as json
import traceback
from string import maketrans

# Make sure the keys come out csv-friendly - all on one line, and surrounded by
# double-quotes, and with any double-quotes inside doubled up per usual.
eol_trans_table = maketrans("\r\n", "  ")
def safe_key(pieces):
  output = io.BytesIO()
  writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
  writer.writerow(pieces)
  # remove the trailing EOL chars:
  return unicode(output.getvalue().strip().translate(eol_trans_table))

def map(key, dimensions, value, cx):
  [reason, appName, appUpdateChannel, appVersion, appBuildID, submission_date] = dimensions
  core = safe_key([submission_date, appVersion, appUpdateChannel])

  try:
    j = json.loads(value)
    # The structure of this json object is designated in
    # toolkit/components/telemetry/TelemetryPing.jsm#assemblePayloadWithMeasurements
    if not "UIMeasurements" in j:
      return

    # This will be an array of events and sessions, specified by the 'type' key in each item.
    ui = j["UIMeasurements"]
    if len(ui) > 0:
      total_count = 0
      total_time = 0

      # Process each reader session, recording the total time spent in each
      for event in ui:
        if event["type"] == "session" and "reader." in event["name"]:
          time = event["end"] - event["start"]
          print "time: " + str(time)
          total_time += (time / 1000) # convert milliseconds to seconds
          total_count += 1

      # Write the total time and count for reader sessions
      cx.write(core, [total_time, total_count])

  except Exception, e:
    cx.write(safe_key(["ERROR", str(e), traceback.format_exc()] + dimensions), [1,0])

def setup_reduce(cx):
    cx.field_separator = ","

def reduce(key, value, cx):
  counts = []
  durations = []

  if key.startswith("ERROR"):
    for error in value:
      cx.write(key, error)
  else:
    for duration, count in value:
      counts.append(count)
      if count > 0:
        durations.append(duration / count)
      else:
        durations.append(0)

    cx.write(",".join([key, str(len(value)), str(sum(counts))]), str(sum(durations)))
