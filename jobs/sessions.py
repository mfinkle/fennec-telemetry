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

    tablet = 0
    if "info" in j:
      info = j["info"]
      if "tablet" in info:
        if info["tablet"]:
          tablet = 1

    core = safe_key([submission_date, appVersion, appUpdateChannel, tablet])

    # The structure of this json object is designated in
    # toolkit/components/telemetry/TelemetryPing.jsm#assemblePayloadWithMeasurements
    if not "UIMeasurements" in j:
      return

    # This will be an array of events and sessions, specified by the 'type' key in each item.
    ui = j["UIMeasurements"]
    if len(ui) > 0:
      sessions = {}

      # Process each session, recording the count and duration spent in each
      for event in ui:
        if event["type"] == "session":
          add_to_sessions(core, sessions, event)

      # Write the total count and duration per panel
      for name, value in sessions.iteritems():
        cx.write(name, value)

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
    for session in value:
      counts.append(session["count"])
      if session["count"] > 0:
        durations.append(session["duration"] / session["count"])
      else:
        durations.append(0)

    #cx.write(",".join([key, str(sum(counts))]), str(sum(durations)))
    cx.write(key, str(sum(counts)))

def add_to_sessions(key, sessions, event):
  name = str(event["name"])

  # ignore "home.1" as it's not very useful and should be removed
  if "home.1" == name:
    return

  # rename the built-in panels to friendly names
  if "4becc86b-41eb-429a-a042-88fe8b5a094e" in name:
    name = "top_sites"
  elif "7f6d419a-cd6c-4e34-b26f-f68b1b551907" in name:
    name = "bookmarks"
  elif "20f4549a-64ad-4c32-93e4-1dcef792733b" in name:
    name = "reading_list"
  elif "f134bf20-11f7-4867-ab8b-e8e705d7fbe8" in name:
    name = "history"
  elif "5c2601a5-eedc-4477-b297-ce4cef52adf8" in name:
    name = "recent_tabs"
  elif "72429afd-8d8b-43d8-9189-14b779c563d0" in name:
    name = "remote_tabs"

  # cleanup some renamed data
  if "homepanel.1:home-feeds-" in name:
    name = "homepanel.1:home-feeds"
  elif "homepanel.1:{" in name:
    name = "homepanel.1:home-feeds"
  elif "urlbar.1:" in name:
    name = "urlbar.1"
  elif "frecency.1:" in name:
    name = "frecency.1"

  duration = (event["end"] - event["start"]) / 1000 # convert milliseconds to seconds

  identifier = key + "," + name
  if not identifier in sessions:
    sessions[identifier] = { "duration": 0, "count": 0 }
  session = sessions[identifier]
  session["duration"] += duration
  session["count"] += 1
  sessions[identifier] = session
