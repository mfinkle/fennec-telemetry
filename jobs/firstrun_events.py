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
      events = {}

      # Process each event with a firstrun session
      for event in ui:
        if event["type"] == "event":
          for session in event["sessions"]:
            if "firstrun." in session:
              add_to_events(core, events, event)

      # Write the total time per specific panel
      for name, value in events.iteritems():
        if value > 0:
          cx.write(name, value)

  except Exception, e:
    cx.write(safe_key(["ERROR", str(e), traceback.format_exc()] + dimensions), [1,0])

def setup_reduce(cx):
    cx.field_separator = ","

def reduce(key, value, cx):
  if key.startswith("ERROR"):
    for error in value:
      cx.write(key, error)
  else:
    value_all = sum(value)
    cx.write(key, value_all)

def add_to_events(key, events, event):
  method = "<none>"
  if event["method"]:
    method = event["method"]
  extras = "<none>"
  if "extras" in event and event["extras"]:
    extras = event["extras"]
  identifier = key + "," + event["action"] + "," + method + "," + extras
  if not identifier in events:
    events[identifier] = 0
  events[identifier] += 1
