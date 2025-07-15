import boto3
import logging
import os

# Configure logging
logger = logging.getLogger(__name__)

# Get AWS region from environment variables
AWS_REGION = os.getenv("AWS_REGION_NAME")

def get_field_id(field_name, table_name):
    """
    Retrieves an item by field_name
    """
    # Use region from environment variable if available
    if AWS_REGION:
        dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    else:
        logger.warning("AWS_REGION_NAME not set, DynamoDB operations may fail")
        dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    
    try:
        response = table.get_item(Key={"field_name": field_name})
    except Exception as e:
        logger.error(f"Error getting item from DynamoDB: {e}")
        return None
    
    if "Item" in response:
        return response["Item"]
    else:
        return None

def get_all_data_from_table(table_name):
    """
    Scans and returns all data from a table
    """
    # Use region from environment variable if available
    if AWS_REGION:
        dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    else:
        logger.warning("AWS_REGION_NAME not set, DynamoDB operations may fail")
        dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    
    try:
        response = table.scan()
        return response.get("Items", [])
    except Exception as e:
        logger.error(f"Error scanning DynamoDB table: {e}")
        return []

def get_field_info_by_id(table_name, field_id):
    """
    Queries field info using a secondary index on field_id
    """
    # Use region from environment variable if available
    if AWS_REGION:
        dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    else:
        logger.warning("AWS_REGION_NAME not set, DynamoDB operations may fail")
        dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    
    try:
        response = table.query(
            IndexName="field_id-index",
            KeyConditionExpression=boto3.dynamodb.conditions.Key("field_id").eq(field_id)
        )
        
        items = response.get("Items", [])
        if items:
            return items[0]
        return None
    except Exception as e:
        logger.error(f"Error querying DynamoDB table by field_id: {e}")
        return None

def get_field_info_by_api_name(table_name, field_name_api):
    """
    Queries field info using a secondary index on field_name_api
    """
    # Use region from environment variable if available
    if AWS_REGION:
        dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
    else:
        logger.warning("AWS_REGION_NAME not set, DynamoDB operations may fail")
        dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)
    
    try:
        response = table.query(
            IndexName="field_name_api-index",
            KeyConditionExpression=boto3.dynamodb.conditions.Key("field_name_api").eq(field_name_api)
        )
        
        items = response.get("Items", [])
        if items:
            return items[0]
        return None
    except Exception as e:
        logger.error(f"Error querying DynamoDB table by field_name_api: {e}")
        return None