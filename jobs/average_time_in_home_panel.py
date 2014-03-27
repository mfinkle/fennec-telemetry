import json

def map(key, dimensions, value, map_context):
  try:
    j = json.loads(value)
    # The structure of this json object is designated in
    # toolkit/components/telemetry/TelemetryPing.jsm#assemblePayloadWithMeasurements
    if not 'UIMeasurements' in j:
      return
    # This will be an array of events and sessions, specified by the 'type' key in each item.
    ui = j['UIMeasurements']
    if len(ui) > 0:
      total = 0
      homepanels = {}

      # Process each homepanel session, recording the total time spent in each
      for event in ui:
        if event['type'] == 'session' and 'homepanel' in event['name']:
          time = event['end'] - event['start']
          add_to_homepanels(homepanels, event['name'], time)
          total += time

      # Write the total time per specific panel
      for name, value in homepanels.iteritems():
        if value > 0:
          map_context.write("average time in " + name, value)

      # Write the total time in panels (Hub)
      map_context.write("average time in homepanels (secs)", total)

  except Exception, e:
    map_context.write("JSON PARSE ERROR:", str(e))

def reduce(key, value, reduce_context):
  if key == "JSON PARSE ERROR:":
    for error in value:
      reduce_context.write(key, error)
  else:
    # Calculate the average
    reduce_context.write(key, sum(value) / len(value))

def add_to_homepanels(homepanels, name, time):
  if not name in homepanels:
    homepanels[name] = 0
  homepanels[name] += time
