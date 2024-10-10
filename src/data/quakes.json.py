#!/usr/bin/env python3
import json
import sys
import urllib.request

# Fetch GeoJSON from the USGS
url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
with urllib.request.urlopen(url) as response:
    if response.getcode() != 200:
        sys.stderr.write(f"Failed to fetch data: HTTP {response.getcode()}\n")
        sys.exit(1)
    
    data = json.loads(response.read().decode())

# Output the JSON data to stdout
json.dump(data, sys.stdout, indent=2)