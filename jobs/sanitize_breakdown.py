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
      count = 0

      # Process each sanitize event
      for event in ui:
        if event["type"] == "event" and "sanitize." in event["action"]:
          count += 1

      # Write the count for each action
      map_context.write("sanitize", count)

  except Exception, e:
    map_context.write("JSON PARSE ERROR:", str(e))

def reduce(key, value, reduce_context):
  if key == "JSON PARSE ERROR:":
    for error in value:
      reduce_context.write(key, error)
  else:
    value_all = sum(value)
    reduce_context.write(key, value_all)
