import json

def map(key, dimensions, value, map_context):
  try:
    j = json.loads(value)
    # The structure of this json object is designated in
    # toolkit/components/telemetry/TelemetryPing.jsm#assemblePayloadWithMeasurements
    if not "UIMeasurements" in j:
      return

    # This will be an array of events and sessions, specified by the 'type' key in each item.
    ui = j["UIMeasurements"]
    if len(ui) > 0:
      sessions = {}

      # Process each load URL event
      for event in ui:
        if event["type"] == "event" and "loadurl." in event["action"]:
          add_to_sessions(sessions, event["method"], concat_sessions(event["sessions"]))

      # Write the count for each loadurl situation
      for name, value in sessions.iteritems():
        if value > 0:
          map_context.write(name, value)

  except Exception, e:
    map_context.write("JSON PARSE ERROR:", str(e))

def reduce(key, value, reduce_context):
  if key == "JSON PARSE ERROR:":
    for error in value:
      reduce_context.write(key, error)
  else:
    value_all = sum(value)
    reduce_context.write(key, value_all)

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
    listing += sanitize_session(session)
    listing += " > "
  return listing

def add_to_sessions(sessions, method, session):
  identifer = method + " | " + session
  if not identifer in sessions:
    sessions[identifer] = 0
  sessions[identifer] += 1
