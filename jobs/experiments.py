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
    locale = "n/a"
    if "info" in j:
      info = j["info"]
      if "tablet" in info:
        if info["tablet"]:
          tablet = 1
      if "locale" in info:
        locale = info["locale"]

    core = safe_key([submission_date, appVersion, appUpdateChannel, locale, tablet])

    # The structure of this json object is designated in
    # toolkit/components/telemetry/TelemetryPing.jsm#assemblePayloadWithMeasurements
    if not "UIMeasurements" in j:
      return

    # This will be an array of events and sessions, specified by the 'type' key in each item.
    ui = j["UIMeasurements"]
    if len(ui) > 0:
      events = {}

      # Process each event
      for event in ui:
        if event["type"] == "event":
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
  action = ""
  if event["action"] is not None:
    action = str(event["action"])

  method = ""
  if event["method"] is not None:
    method = str(event["method"])

  extras = ""
  if "extras" in event and event["extras"] is not None:
    extras = str(event["extras"])
    # Anonymize some private tab actions
    if action == "action.1":
      if extras == "new_private_tab":
        extras = "new_tab"
      elif extras == "home_open_private_tab":
        extras = "home_open_new_tab"
      elif extras == "web_open_private_tab":
        extras = "web_open_new_tab"
      elif extras == "close_private_tabs":
        extras = "close_all_tabs"

  # Cleanup setdefault.1 data to match new format
  if action == "setdefault.1":
    action = "panel.setdefault.1"
    method = "dialog"

  # Cleanup save.1 data to match new format
  if action == "save.1":
    if method == "button" and extras.startswith("firstrun-import-dialog-"):
      action = "action.1"
    elif method == "button" and extras == "reader":
      extras = "reading_list"
    elif method == "pageaction" and extras == "reader":
      extras = "reading_list"

  # Cleanup homescreen data to match new format
  if action == "search.1" and method == "homescreen" and extras == "history":
    method = "suggestion"
  elif action == "action.1" and method == "homescreen" and extras == "hint-private-browsing":
    method = "panel"

  # Use friendly names for panel events
  if action.startswith("panel."):
    if "4becc86b-41eb-429a-a042-88fe8b5a094e" in extras:
      extras = "top_sites"
    elif "7f6d419a-cd6c-4e34-b26f-f68b1b551907" in extras:
      extras = "bookmarks"
    elif "20f4549a-64ad-4c32-93e4-1dcef792733b" in extras:
      extras = "reading_list"
    elif "f134bf20-11f7-4867-ab8b-e8e705d7fbe8" in extras:
      extras = "history"
    elif "5c2601a5-eedc-4477-b297-ce4cef52adf8" in extras:
      extras = "recent_tabs"
    elif "72429afd-8d8b-43d8-9189-14b779c563d0" in extras:
      extras = "remote_tabs"

  for session in event["sessions"]:
    if "experiment." in session:
      identifier = "{0},{1},{2},{3},{4}".format(key, session, action, method, extras)
      if not identifier in events:
        events[identifier] = 0
      events[identifier] += 1
