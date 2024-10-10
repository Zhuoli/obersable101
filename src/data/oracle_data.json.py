#!/usr/bin/env python3
import json
import sys
import oci
from oci.object_storage import ObjectStorageClient
from oci.config import from_file

# Load the Oracle Cloud Infrastructure configuration
config = from_file()  # Assumes you have a config file at ~/.oci/config

# Initialize the Object Storage client
object_storage = ObjectStorageClient(config)

# Set your Oracle Cloud Object Storage details
namespace = "your_namespace"
bucket_name = "your_bucket_name"
object_name = "your_data.json"

try:
    # Get the object
    response = object_storage.get_object(namespace, bucket_name, object_name)
    
    # Read the data
    data = json.loads(response.data.content.decode('utf-8'))

    # Output the JSON data to stdout
    json.dump(data, sys.stdout, indent=2)

except Exception as e:
    sys.stderr.write(f"Error: {str(e)}\n")
    sys.exit(1)