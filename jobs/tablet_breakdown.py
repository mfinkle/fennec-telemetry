import json

def map(key, dimensions, value, map_context):
  try:
    j = json.loads(value)
    # The structure of this json object is designated in
    # toolkit/components/telemetry/TelemetryPing.jsm#assemblePayloadWithMeasurements
    if not "info" in j:
      return

    # This will be an array of events and sessions, specified by the 'type' key in each item.
    info = j["info"]
    if "tablet" in info:
      if info["tablet"]:
        map_context.write("tablet", 1)
      else:
        map_context.write("non-tablet", 1)

  except Exception, e:
    map_context.write("JSON PARSE ERROR:", str(e))

def reduce(key, value, reduce_context):
  if key == "JSON PARSE ERROR:":
    for error in value:
      reduce_context.write(key, error)
  else:
    value_all = sum(value)
    reduce_context.write(key, value_all)
