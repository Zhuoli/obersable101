#!/usr/bin/env python3
import json
import sys
import oci
from oci.object_storage import ObjectStorageClient
from oci.config import from_file
from oci.identity import IdentityClient

def get_object_storage_client():
    """
    Initialize and return an Object Storage client, trying config file first and then
    falling back to instance principal authentication if config is not available.
    """
    try:
        # Attempt to load the Oracle Cloud Infrastructure configuration from ~/.oci/config
        config = from_file(profile_name="default")  # Assumes you have a config file at ~/.oci/config
        print("Authenticated using config file.")
        return ObjectStorageClient(config), config
    except Exception as config_error:
        print(f"Config file authentication failed: {str(config_error)}")
        print("Attempting instance principal authentication...")

    # Try to authenticate using instance principal if config file authentication fails
    try:
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        print("Authenticated using instance principal.")
        return ObjectStorageClient(config={}, signer=signer), {}
    except Exception as ip_error:
        sys.stderr.write(f"Error creating instance principal signer: {str(ip_error)}\n")
        sys.exit(1)
        
def verify_authentication(identity_client):
    """
    Verify the authentication by retrieving the user's own details using the IdentityClient.
    This ensures that the client is authenticated and has the necessary permissions.
    """
    try:
        # Get user details to verify that authentication is successful
        user = identity_client.get_user(identity_client.config["user"]).data
        print(f"Authentication verified successfully for user: {user.description} (OCID: {user.id})")
    except Exception as auth_error:
        sys.stderr.write(f"Authentication verification failed: {str(auth_error)}\n")
        sys.exit(1)

# Initialize the Object Storage client and configuration
object_storage, config = get_object_storage_client()

# Initialize the Identity client for authentication verification
identity_client = IdentityClient(config) if config else IdentityClient(signer=object_storage.base_client.signer)

# Verify the authentication before proceeding with the object retrieval
verify_authentication(identity_client)


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