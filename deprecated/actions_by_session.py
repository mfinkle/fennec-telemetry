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
      actions = {}

      # Process each action event
      for event in ui:
        if event["type"] == "event" and "action." in event["action"]:
          add_to_actions(core, actions, event["extras"], event["method"], concat_sessions(event["sessions"]))

      # Write the count for each action
      for name, value in actions.iteritems():
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

def sanitize_session(session):
  if "4becc86b-41eb-429a-a042-88fe8b5a094e" in session:
    return "top_sites"
  if "7f6d419a-cd6c-4e34-b26f-f68b1b551907" in session:
    return "bookmarks"
  if "20f4549a-64ad-4c32-93e4-1dcef792733b" in session:
    return "reading_list"
  if "f134bf20-11f7-4867-ab8b-e8e705d7fbe8" in session:
    return "history"
  return session

def concat_sessions(sessions):
  listing = ""
  for session in sessions:
    # Skip the "home" wrapper session
    if "home." in session:
      continue
    if listing != "":
      listing += " > "
    listing += sanitize_session(session)
  return listing

def add_to_actions(key, actions, action, method, sessions):
  identifer = key + "," + str(action) + "," + str(method) + "," + sessions
  if not identifer in actions:
    actions[identifer] = 0
  actions[identifer] += 1
