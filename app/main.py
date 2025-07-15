from fastapi import FastAPI, Depends, HTTPException, Header, Response, status
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Tuple
import os
import json
import uuid
from datetime import datetime
from json import JSONDecodeError
import boto3
import logging
import requests
from botocore.exceptions import ClientError

from app.contact_reason_mapping import CONTACT_REASON_MAPPING
from app.hardcoded_field_mappings import get_field_info_by_api_name

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Environment variables
API_KEY = os.getenv("API_KEY", "default_api_key")
WEBHOOK_ID = os.getenv("WEBHOOK_ID", "createConversation")
DOMAIN_ID = os.getenv("DOMAIN_ID")
DOMAIN_CUSTOMER_PROFILE_ID = os.getenv("DOMAIN_CUSTOMER_PROFILE_ID")
TEMPLATE_CASE_ID = os.getenv("TEMPLATE_CASE_ID")
CONNECT_PROFILE_ARN = os.getenv("CONNECT_PROFILE_ARN")
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME")
AWS_REGION = os.getenv("AWS_REGION_NAME")
SECRET_NAME_ARN = os.getenv("SECRET_NAME")
SECRET_NAME = SECRET_NAME_ARN.split(":")[-1] if SECRET_NAME_ARN else None
RAPPI_MICROSERVICES_BASE_URL = os.getenv("RAPPI_MICROSERVICES_BASE_URL")
RAPPI_GET_TOKEN_URL = f"{RAPPI_MICROSERVICES_BASE_URL}/lupe/core/api/auth0/login-client" if RAPPI_MICROSERVICES_BASE_URL else None

# Initialize AWS clients
if AWS_REGION:
    client_cases = boto3.client("connectcases", region_name=AWS_REGION)
    client_customer_profiles = boto3.client("customer-profiles", region_name=AWS_REGION)
else:
    # For local development without AWS credentials
    logger.warning("AWS_REGION_NAME not set, using mock AWS clients")
    from unittest.mock import MagicMock
    client_cases = MagicMock()
    client_customer_profiles = MagicMock()

# Custom exception for missing parameters
class MissingConversationParametersError(Exception):
    pass

# Pydantic models
class CustomFields(BaseModel):
    order_id: Optional[str] = None
    user_lang: Optional[str] = None
    chat_id: Optional[str] = None
    chat_type: Optional[str] = None
    payment_method: Optional[str] = None
    type_vertical: Optional[str] = None
    created_at: Optional[str] = None
    place_at: Optional[str] = None
    store_type_store: Optional[str] = None
    store_id: Optional[str] = None
    store_type: Optional[str] = None
    order_debt: Optional[str] = None
    order_has_debt: Optional[str] = None
    storekeeper_id: Optional[str] = None
    language: Optional[str] = None
    country: Optional[str] = None
    last_order_canceled_by_fraud: Optional[str] = None
    loyalty_program: Optional[str] = None
    store_name: Optional[str] = None
    churn: Optional[str] = None
    look_alike_score: Optional[str] = None
    rfm_segment: Optional[str] = None
    finance_user_type: Optional[str] = None
    is_prime: Optional[str] = None
    total_debt: Optional[str] = None
    type_category_hc: Optional[str] = None
    tipoYCategoriaRtsTree: Optional[str] = None
    conversation_lang: Optional[str] = None

class ConversationModel(BaseModel):
    subject: str = Field(..., description="Subject of the conversation")
    sentAt: str = Field(..., description="When the conversation was sent")
    channel: str = Field(..., description="Communication channel")
    articleId: Optional[str] = None
    externalId: Optional[str] = None
    customFields: Optional[CustomFields] = None

class CustomerModel(BaseModel):
    id: str = Field(..., description="Customer's ID")
    name: str = Field(..., description="Customer's name")
    phone: Optional[str] = None
    email: Optional[str] = None
    externalId: Optional[str] = None
    userBlocked: Optional[bool] = None
    loyalty: Optional[str] = None
    country: Optional[str] = None
    rfmSegment: Optional[str] = None
    customerType: Optional[str] = None

class WebhookRequest(BaseModel):
    customer: CustomerModel
    conversation: ConversationModel

# Field mapping is now handled in the hardcoded_field_mappings.py module

# Função para verificar o token de autorização
async def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    if token != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return token

@app.post("/v1/hooks/web/{webhook_id}", status_code=201)
async def webhook_handler(
    webhook_id: str,
    request: WebhookRequest,
    token: str = Depends(verify_token)
):
    # Verify webhook_id
    if webhook_id != WEBHOOK_ID:
        raise HTTPException(status_code=404, detail="Webhook not found")
    
    try:
        # Process customer information
        user_id, name, last_name, phone, email, external_id, user_blocked, loyalty, country, rfm_segment = get_customer_info(request)
        
        if not user_id:
            raise HTTPException(
                status_code=400, 
                detail="Error: Missing required parameter: user_id"
            )
            
        # Get conversation subject and validate required fields
        subject = get_conversation_info(request)
        
        # Check if customer profile exists
        exist_customer_profile, profile_id = search_customer_profile(rappi_id=user_id)
        
        if exist_customer_profile == "Error":
            # Return error response from search_customer_profile
            return profile_id
        
        # Create customer profile if it doesn't exist
        if not exist_customer_profile:
            logger.info(f"User with Rappi Id: {user_id} does not exist. Creating in Customer Profile in Amazon Connect.")
            profile_id = create_customer_profile(
                user_id=user_id,
                name=name,
                last_name=last_name,
                phone=phone,
                email=email,
                external_id=external_id,
                user_blocked=user_blocked,
                loyalty=loyalty,
                country=country,
                rfm_segment=rfm_segment,
            )
            
            add_key(profile_id=profile_id, contact_id=user_id, key_name="RappiId")
            customer_event = {"is_new": True, "customer": request.customer.dict()}
        else:
            customer_event = {"is_new": False, "customer": request.customer.dict()}
        
        # Process case information
        case_info_unstructure = get_case_info(request)
        case_info_kustomer_structure = get_case_kustomer_structure(case_info_unstructure)
        case_info_kustomer_structure = add_author_type(request.customer.dict(), case_info_kustomer_structure)
        
        # Map fields to IDs
        case_info = get_fileds_id(case_info_unstructure)
        
        # Create case
        case_id = create_case(subject, profile_id, case_info, user_id)
        
        # Send conversation ID to Rappi
        status_code, response_text = post_conversation_id_to_rappi_mock(
            request.conversation.dict(), case_id
        )
        
        if status_code in [200, 202]:
            logger.info(f"case_id {case_id}")
            logger.info(f"profile_id {profile_id}")
            # Stream event code commented out as per original
            # stream_event(
            #    case_id,
            #    subject,
            #    profile_id,
            #    case_info_kustomer_structure,
            #    request.conversation.dict(),
            #    customer_event,
            # )
            return {"conversation": {"id": str(case_id)}}
        else:
            logger.error(f"Error sending conversation id to Rappi: {response_text}")
            return {"conversation": {"id": str(case_id)}}
            
    except MissingConversationParametersError as e:
        logger.error(f"Error: Missing conversation parameters: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Error: Missing required parameter: {e}"
        )
    except client_customer_profiles.exceptions.ResourceNotFoundException as e:
        error_dict = e.__dict__
        if "is not defined in the domain" in error_dict["response"]["Error"]["Message"] and "KeyName" in error_dict["response"]["Error"]["Message"]:
            logger.error(f"Error finding Rappi user in Customer Profiles: {e}")
            raise HTTPException(
                status_code=404,
                detail="Key Name not found. Please check and try again."
            )
        if "is not found in account" in error_dict["response"]["Error"]["Message"] and "DomainName" in error_dict["response"]["Error"]["Message"]:
            logger.error(f"Error finding Rappi user in Customer Profiles: {e}")
            raise HTTPException(
                status_code=404,
                detail="DomainName not found. Please check and try again."
            )
        raise HTTPException(
            status_code=404,
            detail="Resource not found. Please check and try again."
        )
    except client_customer_profiles.exceptions.BadRequestException as e:
        error_dict = e.__dict__
        if "Member must satisfy constraint: [Member must have length less than or equal to 255, Member must have length greater than or equal to 1" in error_dict["response"]["Error"]["Message"]:
            logger.error(f"Error finding Rappi user in Customer Profiles: {e}")
            raise HTTPException(
                status_code=400,
                detail="Parameters must be between 1 and 255 characters. Please check and try again."
            )
        raise HTTPException(
            status_code=400,
            detail="Bad request. Please check and try again."
        )
    except Exception as e:
        logger.error(f"Unexpected error creating conversation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating the conversation: {str(e)}"
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Helper functions
def get_case_info(request: WebhookRequest) -> Dict:
    """Extract case information from the conversation custom fields."""
    conversation_info = request.conversation
    case_info = conversation_info.customFields.dict() if conversation_info.customFields else {}
    return case_info

def get_conversation_info(request: WebhookRequest) -> str:
    """Extract and validate conversation information."""
    conversation_info = request.conversation
    
    subject = conversation_info.subject
    sent_at = conversation_info.sentAt
    channel = conversation_info.channel
    
    if not sent_at:
        raise MissingConversationParametersError("sentAt")
    if not channel:
        raise MissingConversationParametersError("channel")
    if not subject:
        raise MissingConversationParametersError("subject")
    
    return subject

def get_customer_info(request: WebhookRequest) -> Tuple:
    """Extract customer information from the request."""
    customer_info = request.customer
    
    user_id = customer_info.id
    
    if not user_id:
        logger.error("user_id not found in the request")
        return None, None, None, None, None, None, None, None, None, None
    
    name_parts = customer_info.name.split(" ")
    last_name = name_parts[-1]
    name = " ".join(map(str, name_parts[:-1]))
    
    phone = customer_info.phone
    
    if not phone:
        phone = "0000000000"
    
    email = customer_info.email
    external_id = customer_info.externalId
    user_blocked = customer_info.userBlocked
    loyalty = customer_info.loyalty
    country = customer_info.country
    rfm_segment = customer_info.rfmSegment
    
    return (
        user_id,
        name,
        last_name,
        phone,
        email,
        external_id,
        user_blocked,
        loyalty,
        country,
        rfm_segment,
    )

def search_customer_profile(rappi_id: str) -> Tuple:
    """Search for a customer profile by Rappi ID."""
    try:
        response = client_customer_profiles.search_profiles(
            DomainName=DOMAIN_CUSTOMER_PROFILE_ID, 
            KeyName="RappiId", 
            Values=[rappi_id]
        )
    except client_customer_profiles.exceptions.ResourceNotFoundException as e:
        raise
    except client_customer_profiles.exceptions.BadRequestException as e:
        raise
        
    logger.info(f"Response search_customer_profile: {response}")
    if response.get("Items"):
        return True, response["Items"][0].get("ProfileId")
    else:
        return False, None

def create_customer_profile(
    user_id: str,
    name: str,
    last_name: str,
    phone: str,
    email: str,
    external_id: str,
    user_blocked: bool,
    loyalty: str,
    country: str,
    rfm_segment: str,
) -> Any:
    """Create a customer profile in Amazon Connect."""
    try:
        response = client_customer_profiles.create_profile(
            DomainName=DOMAIN_CUSTOMER_PROFILE_ID,
            FirstName=name,
            LastName=last_name,
            MobilePhoneNumber=phone,
            EmailAddress=email,
            Attributes={
                "RappiId": user_id,
                "ExternalId": external_id or "",
                "UserBlocked": str(user_blocked) if user_blocked is not None else "",
                "Loyalty": loyalty or "",
                "Country": country or "",
                "Rfm": rfm_segment or "",
            },
        )
    except client_customer_profiles.exceptions.BadRequestException as e:
        error_dict = e.__dict__
        raise HTTPException(
            status_code=400,
            detail="Bad request. Please check and try again."
        )
    except client_customer_profiles.exceptions.ResourceNotFoundException as e:
        error_dict = e.__dict__
        raise HTTPException(
            status_code=404,
            detail="Resource not found. Please check and try again."
        )
    
    logger.info(f"Response customer profile creation: {response}")
    
    if response["ResponseMetadata"].get("HTTPStatusCode") == 200:
        return response["ProfileId"]
    else:
        return None

def add_key(profile_id: str, contact_id: str, key_name: str) -> None:
    """Add a key to a customer profile."""
    arr_contact = [contact_id]
    response = client_customer_profiles.add_profile_key(
        ProfileId=profile_id,
        KeyName=key_name,
        Values=arr_contact,
        DomainName=DOMAIN_CUSTOMER_PROFILE_ID,
    )
    logger.info(f"Response add key: {response}")

def create_case(title: str, profile_id: str, case_info: Dict, user_id: str) -> str:
    """Create a case in Amazon Connect Cases."""
    random_client_token = str(uuid.uuid4())
    
    fields = [
        {"id": "title", "value": {"stringValue": title}},
        {
            "id": "customer_id",
            "value": {"stringValue": f"{CONNECT_PROFILE_ARN}{profile_id}"},
        },
    ]
    
    for field in case_info:
        value = "" if case_info[field].get("value") is None else case_info[field].get("value")
        new_field = {
            "id": str(field),
            "value": {case_info[field].get("type"): value},
        }
        fields.append(new_field)
    
    
    # Create the payload for creating a case
    create_case_payload = {
        "clientToken": random_client_token,
        "domainId": DOMAIN_ID,
        "fields": fields,
        "templateId": TEMPLATE_CASE_ID
    }
    
    # If DOMAIN_ID is not defined, just print the payload and return a mock case ID
    if not DOMAIN_ID:
        logger.info("DOMAIN_ID not defined, printing payload instead of creating case:")
        logger.info(json.dumps(create_case_payload, indent=2))
        return f"mock-case-{uuid.uuid4()}"
        
    # Otherwise, create the case normally
    response = client_cases.create_case(**create_case_payload)
    logger.info(f"Create case response: {response}")
    return response["caseId"]

def get_fileds_id(case_info_map: Dict) -> Dict:
    """Map case info fields to their hardcoded field IDs."""
    case_info_id_map = {}
    
    for current_field in case_info_map:
        field = get_field_info_by_api_name(None, current_field)
        if field:
            value = (
                str(case_info_map[current_field])
                if field["field_type"] == "stringValue"
                else case_info_map[current_field]
            )
            
            if current_field == 'type_category_hc' and value in CONTACT_REASON_MAPPING:
                value = CONTACT_REASON_MAPPING[value]
            
            case_info_id_map[field["field_id"]] = {
                "value": value,
                "type": field["field_type"],
            }
    
    return case_info_id_map

def post_conversation_id_to_rappi(conversation: Dict, conversation_id: str) -> Tuple:
    """Send conversation ID to Rappi."""
    secrets = json.loads(get_secrets())
    token_payload = json.dumps(
        {
            "grant_type": "client_credentials",
            "audience": "https://lupe.rappi.com",
            "client_secret": secrets["RAPPI_CLIENT_SECRET"],
            "client_id": secrets["RAPPI_CLIENT_ID"],
        }
    )
    headers = {"Content-Type": "application/json"}
    response = requests.request(
        "POST", RAPPI_GET_TOKEN_URL, headers=headers, data=token_payload
    )
    logger.info(f"Token request payload: {token_payload}")
    logger.info(f"Token response status: {response.status_code}")
    
    if response.status_code in [200, 202]:
        token = json.loads(response.text)["token_data"]["token"]
    else:
        logger.error(f"Error generating Rappi token to send conversation ID: {response.text}")
        return response.status_code, response.text
    
    logger.info(f"Token response: {response.text}")
    
    try:
        if conversation.get("customFields") and conversation["customFields"].get("country"):
            country = conversation["customFields"]["country"]
            post_url = f'{RAPPI_MICROSERVICES_BASE_URL}/api/rappi-kustomer/country/{country}/conversation/ticketId'
            
            headers = {
                "Content-Type": "application/json",
                "Auth_token": f"Bearer {token}"
            }
            
            chat_id = conversation.get("customFields", {}).get("chat_id", "")
            
            post_conversation_id_payload = json.dumps(
                {
                    "_id": conversation.get("externalId", ""),
                    "ticketId": conversation_id,
                    "chatId": chat_id,
                }
            )
            
            logger.info(f"Conversation ID payload: {post_conversation_id_payload}")
            post_response = requests.request(
                "POST", post_url, headers=headers, data=post_conversation_id_payload
            )
            
            if post_response.status_code in [200, 202]:
                logger.info(f"Conversation ID {conversation_id} sent successfully to Rappi")
                return post_response.status_code, post_response.text
            else:
                logger.error(f"Error sending conversation ID {conversation_id} to Rappi: {post_response.text}")
                return post_response.status_code, post_response.text
        else:
            logger.error("Missing country in customFields, cannot send conversation ID to Rappi")
            return 400, "Missing country in customFields"
    except Exception as e:
        logger.error(f"Error sending conversation ID to Rappi: {e}")
        raise e
    
def post_conversation_id_to_rappi_mock(conversation: Dict, conversation_id: str) -> Tuple:
    """Mock sending conversation ID to Rappi."""
    # Simulate a successful response
    mock_response_text = json.dumps({
        "message": "Conversation ID sent successfully",
        "conversation_id": conversation_id,
        "country": conversation.get("customFields", {}).get("country", "mock-country"),
        "chatId": conversation.get("customFields", {}).get("chat_id", "mock-chat-id"),
        "_id": conversation.get("externalId", "mock-external-id")
    })
    logger.info(f"[MOCK] Conversation ID payload: {mock_response_text}")
    return 200, mock_response_text

def get_secrets() -> str:
    """Get secrets from AWS Secrets Manager."""
    if not SECRET_NAME:
        logger.error("SECRET_NAME environment variable not set")
        return "{\"RAPPI_CLIENT_SECRET\":\"mock-secret\", \"RAPPI_CLIENT_ID\":\"mock-id\"}"
        
    if not AWS_REGION:
        logger.error("AWS_REGION_NAME environment variable not set")
        return "{\"RAPPI_CLIENT_SECRET\":\"mock-secret\", \"RAPPI_CLIENT_ID\":\"mock-id\"}"
        
    secret_name = SECRET_NAME[: SECRET_NAME.rfind("-")]
    region_name = AWS_REGION
    
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)
    
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        logger.error(f"Error retrieving secret: {e}")
        # Return mock secrets for development
        return "{\"RAPPI_CLIENT_SECRET\":\"mock-secret\", \"RAPPI_CLIENT_ID\":\"mock-id\"}"
    
    # Decrypts secret using the associated KMS key
    secret = get_secret_value_response["SecretString"]
    return secret

def get_case_kustomer_structure(case_info: Dict) -> Dict:
    """Convert case info to Kustomer structure using hardcoded mappings."""
    case_info_kustomer = {}
    
    for key, value in case_info.items():
        field_info = get_field_info_by_api_name(None, key)
        if field_info and "field_name_kustomer" in field_info:
            kustomer_field_name = field_info["field_name_kustomer"]
            case_info_kustomer[kustomer_field_name] = value
    
    logger.info(f"Kustomer data for event: {case_info_kustomer}")
    return case_info_kustomer

def add_author_type(customer: Dict, case_info_kustomer_structure: Dict) -> Dict:
    """Add author type to Kustomer structure."""
    if customer.get("customerType"):
        case_info_kustomer_structure["authorTypeStr"] = customer.get("customerType")
    return case_info_kustomer_structure

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)