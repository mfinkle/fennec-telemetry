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
    version = "n/a"
    arch = "n/a"
    memsize = 0
    device = ""
    manufacturer = ""
    hardware = ""
    
    if "info" in j:
      info = j["info"]
      if "tablet" in info:
        if info["tablet"]:
          tablet = 1
      if "version" in info:
        version = info["version"]
      if "arch" in info:
        arch = info["arch"]
      if "memsize" in info:
        memsize = info["memsize"]
      if "device" in info:
        device = info["device"]

    core = safe_key([submission_date, appVersion, appUpdateChannel, tablet, version, arch, memsize, device])

    cx.write(core, 1)

  except Exception, e:
    cx.write(safe_key(["ERROR", str(e), traceback.format_exc()] + dimensions), [1,0])

def setup_reduce(cx):
    cx.field_separator = ","

def reduce(key, value, cx):
  if key.startswith("ERROR") == False:
    value_all = sum(value)
    cx.write(key, value_all)
