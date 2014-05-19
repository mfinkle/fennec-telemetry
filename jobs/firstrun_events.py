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
      events = {}

      # Process each event with a firstrun session
      for event in ui:
        if event["type"] == "event":
          for session in event["sessions"]:
            if "firstrun." in session:
              add_to_events(events, event)

      # Write the total time per specific panel
      for name, value in events.iteritems():
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

def add_to_events(events, event):
  method = "<none>"
  if event["method"]:
    method = event["method"]
  extras = "<none>"
  if "extras" in event and event["extras"]:
    extras = event["extras"]
  identifier = event["action"] + ", " + method + ", " + extras
  if not identifier in events:
    events[identifier] = 0
  events[identifier] += 1
