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
      total_count = 0
      total_time = 0

      # Process each reader session, recording the total time spent in each
      for event in ui:
        if event["type"] == "session" and "reader." in event["name"]:
          time = event["end"] - event["start"]
          print "time: " + str(time)
          total_time += (time / 1000) # convert milliseconds to seconds
          total_count += 1

      # Write the total time and count for reader sessions
      map_context.write("session_duration", total_time)
      map_context.write("session_count", total_count)

  except Exception, e:
    map_context.write("JSON PARSE ERROR:", str(e))

def reduce(key, value, reduce_context):
  if key == "JSON PARSE ERROR:":
    for error in value:
      reduce_context.write(key, error)
  else:
    if key == "session_duration":
      value_secs = sum(value)
      # Calculate the average
      reduce_context.write(key, value_secs / len(value))
    else:
      value_all = sum(value)
      reduce_context.write(key, value_all)
