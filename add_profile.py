import boto3
import logging
import uuid
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# First, create an object type that includes RappiId

client_customer_profiles = boto3.client("customer-profiles", region_name='us-east-1')

def create_rappi_object_type():
    try:
        response = client_customer_profiles.put_profile_object_type(
            DomainName='dfx5-connect-rappi-customer-profiles-domain-dev',
            ObjectTypeName="RappiUser",
            Description="Rappi user profile object",
            Fields={
                "RappiId": {
                    "Source": "RappiId",
                    "Target": "_profile.Attributes.RappiId",
                    "ContentType": "STRING"
                }
            },
            Keys={
                "RappiId": [
                    {
                        "FieldNames": ["RappiId"],
                        "StandardIdentifiers": ["UNIQUE"]  # Changed from PROFILE to UNIQUE
                    }
                ]
            }
        )
        logger.info(f"Created object type: {response}")
    except Exception as e:
        logger.error(f"Error creating object type: {e}")

def add_rappi_to_profile(profile_id: str, rappi_id: str) -> None:
    """Add Rappi ID as a profile attribute."""
    try:
        response = client_customer_profiles.update_profile(
            DomainName='dfx5-connect-rappi-customer-profiles-domain-dev',
            ProfileId=profile_id,
            Attributes={
                "RappiId": rappi_id
            }
        )
        logger.info(f"Updated profile with RappiId: {response}")
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        
        
def create_profile_with_rappi_id(rappi_id: str) -> str:
    """Create a new profile with Rappi ID."""
    try:
        response = client_customer_profiles.create_profile(
            DomainName='dfx5-connect-rappi-customer-profiles-domain-dev',
            Attributes={
                "RappiId": rappi_id
            },
        )
        logger.info(f"Created profile with ID {response.get('ProfileId', 'No ProfileId')} and RappiId {rappi_id}")
        return response.get('ProfileId', 'No ProfileId')
    except Exception as e:
        logger.error(f"Error creating profile: {e}")
        return None

#add_rappi_to_profile("8ccbaf1bedd0495ca24595fe045b2289", "12345")


response = client_customer_profiles.add_profile_key(
    ProfileId='8ccbaf1bedd0495ca24595fe045b2289',
    KeyName='RappiId',
    Values=[
        '12345',
    ],
    DomainName='dfx5-connect-rappi-customer-profiles-domain-dev'
)
print("✅ Added RappiId to profile successfully")
print(response)