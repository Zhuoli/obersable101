#!/usr/bin/env python3
import json
import sys
import oci
from oci.object_storage import ObjectStorageClient
from oci.config import from_file
from oci.auth import signers

def get_object_storage_client():
    # Try to load the Oracle Cloud Infrastructure configuration
    try:
        config = from_file()  # Assumes you have a config file at ~/.oci/config
        return ObjectStorageClient(config)
    except Exception as config_error:
        print(f"Config file authentication failed: {str(config_error)}")
        print("Attempting instance principal authentication...")

    # If config fails, try instance principal authentication
    try:
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        return ObjectStorageClient(config={}, signer=signer)
    except Exception as ip_error:
        sys.stderr.write(f"Error creating instance principal signer: {str(ip_error)}\n")
        sys.exit(1)

# Initialize the Object Storage client
object_storage = get_object_storage_client()

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