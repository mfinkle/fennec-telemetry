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

  try:
    j = json.loads(value)

    uptime = 0
    if "simpleMeasurements" in j:
      uptime = j["simpleMeasurements"]["uptime"]

    core = safe_key([submission_date, appUpdateChannel])

    # The structure of this json object is designated in
    # toolkit/components/telemetry/TelemetryPing.jsm#assemblePayloadWithMeasurements
    if not "UIMeasurements" in j:
      return

    # This will be an array of events and sessions, specified by the 'type' key in each item.
    ui = j["UIMeasurements"]

    # Creat a short sequence of events to include as part of the key
    sequence = ""
    
    # Process at most 5 events
    num = 0
    if len(ui) > 0:
      for event in ui:
        if num >= 5:
          break

        if event["type"] == "event":
          num += 1
          if sequence != "":
            sequence += "|"
          sequence += str(event["action"]) + ":" + str(event["method"])
          if "extras" in event:
            sequence += ":" + str(event["extras"])

    if num > 0:
      cx.write(core + "," + sequence, 1)

  except Exception, e:
    cx.write(safe_key(["ERROR", str(e), traceback.format_exc()] + dimensions), [1,0])

def setup_reduce(cx):
    cx.field_separator = ","

def reduce(key, value, cx):
  if key.startswith("ERROR"):
    for error in value:
      cx.write(key, error)
  else:
    cx.write(key, str(sum(value)))
