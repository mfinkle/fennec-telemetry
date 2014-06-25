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
      homesessions = []
      homepanels = {}

      # Process each home session
      for event in ui:
        if event["type"] == "session" and "home." in event["name"]:
          homesessions.append(event)

      # Process each homepanel session, looking for the nearest home session
      for event in ui:
        if event["type"] == "session" and "homepanel." in event["name"]:
          for session in homesessions:
            if session["start"] - 100 <= event["start"] and event["start"] <= session["start"] + 100:
              add_to_homepanels(homepanels, event["name"])

      # Write the total time per specific panel
      for name, value in homepanels.iteritems():
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

def add_to_homepanels(homepanels, name):
  name = name.split(":", 1)[1]
  if "4becc86b-41eb-429a-a042-88fe8b5a094e" in name:
    name = "top_sites"
  if "7f6d419a-cd6c-4e34-b26f-f68b1b551907" in name:
    name = "bookmarks"
  if "20f4549a-64ad-4c32-93e4-1dcef792733b" in name:
    name = "reading_list"
  if "f134bf20-11f7-4867-ab8b-e8e705d7fbe8" in name:
    name = "history"

  if not name in homepanels:
    homepanels[name] = 0
  homepanels[name] += 1
