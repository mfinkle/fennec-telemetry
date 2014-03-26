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
    map_context.write("event_count", len(ui))

  except Exception, e:
    map_context.write("JSON PARSE ERROR:", e)

def reduce(key, value, reduce_context):
  if key == "JSON PARSE ERROR:":
    for i in set(value):
      reduce_context.write(key, i)
  reduce_context.write(key, sum(value))
