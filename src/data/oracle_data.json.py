#!/usr/bin/env python3
import json
import sys
import oci
from oci.object_storage import ObjectStorageClient
from oci.config import from_file
from oci.identity import IdentityClient
from oci.exceptions import ServiceError

def get_oci_client():
    """
    Initialize and return an OCI client, using the local config file if available,
    otherwise falling back to instance principal authentication.
    """
    try:
        # Attempt to load the Oracle Cloud Infrastructure configuration from ~/.oci/config
        config = from_file(profile_name="DEFAULT")
        print("Authenticated using config file.")
        
        token_file = config['security_token_file']
        with open(token_file, 'r') as f:
            token = f.read().strip()
        private_key = oci.signer.load_private_key_from_file(config['key_file'])
        signer = oci.auth.signers.SecurityTokenSigner(token, private_key) 
        client = oci.identity.IdentityClient({'region': config['region']}, signer=signer)
        
        return client, config
    
    except Exception as config_error:
        print(f"Config file authentication failed: {str(config_error)}")
        print("Attempting instance principal authentication...")
        
        try:
            # Attempt to use instance principal authentication
            signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
            client = oci.identity.IdentityClient(config={}, signer=signer)
            config = {'region': signer.region}  # We need to create a minimal config for consistency
            print("Authenticated using instance principal.")
            return client, config
        
        except Exception as ip_error:
            sys.stderr.write(f"Instance principal authentication failed: {str(ip_error)}\n")
            sys.exit(1)

def verify_authentication(identity_client,config):
    """
    Verify the authentication by listing available regions in OCI.
    This ensures that the client is authenticated and has the necessary permissions.
    """
    try:
        # List regions to verify that authentication is successful
        response = identity_client.list_region_subscriptions(config['tenancy'])
        print(f"Authentication verified successfully. Available regions: {response.data}")
    except ServiceError as se:
        sys.stderr.write(f"Authentication verification failed: {str(se)}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Unexpected error during authentication verification: {str(e)}\n")
        sys.exit(1)

# Initialize the Object Storage client and configuration
identity_client, config = get_oci_client()

# Verify the authentication before proceeding with the object retrieval
verify_authentication(identity_client, config)

# Create an Object Storage client using the same authentication
object_storage = ObjectStorageClient(config, signer=identity_client.base_client.signer)

# Set your Oracle Cloud Object Storage details
namespace = "axwknapzxq9r"
bucket_name = "zhuoli-test-oct10-2024"
object_name = "cities.csv"

try:
    # Get the object
    response = object_storage.get_object(namespace, bucket_name, object_name)
    
    # Read the data
    content = response.data.content.decode('utf-8')
    
    # Check if the content is JSON
    try:
        data = json.loads(content)
        # Output the JSON data to stdout
        json.dump(data, sys.stdout, indent=2)
    except json.JSONDecodeError:
        # If it's not JSON, just print the content as is
        print(content)

except ServiceError as se:
    sys.stderr.write(f"Error retrieving object: {str(se)}\n")
    sys.exit(1)
except Exception as e:
    sys.stderr.write(f"Unexpected error: {str(e)}\n")
    sys.exit(1)