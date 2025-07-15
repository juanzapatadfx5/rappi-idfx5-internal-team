"""
Hardcoded field mappings to replace DynamoDB queries.
This module contains dictionaries with hardcoded field mappings for the create-conversation service.
"""

# Maps API field names to their corresponding database field IDs, types, and Kustomer field names
"""FIELD_MAPPINGS = {
    "order_id": {
        "field_id": "b7c23a97-0986-41f1-89e8-1e0f0790fab1",
        "field_type": "stringValue",
        "field_name_kustomer": "orderIdStr"
    },
    "user_lang": {
        "field_id": "c8d24a98-1086-42f2-89e9-2e1f1791fac2",
        "field_type": "stringValue",
        "field_name_kustomer": "languageStr"
    },
    "chat_id": {
        "field_id": "d9e25a99-2087-43f3-89f9-3e2f2792fad3",
        "field_type": "stringValue",
        "field_name_kustomer": "chatIdStr"
    },
    "chat_type": {
        "field_id": "e0f26a00-3088-44f4-90f0-4e3f3793fae4",
        "field_type": "stringValue",
        "field_name_kustomer": "chatTypeStr"
    },
    "payment_method": {
        "field_id": "f1g27a01-4089-45f5-91f1-5e4f4794faf5",
        "field_type": "stringValue",
        "field_name_kustomer": "paymentMethodStr"
    },
    "type_vertical": {
        "field_id": "g2h28a02-5090-46f6-92f2-6e5f5795fag6",
        "field_type": "stringValue",
        "field_name_kustomer": "typeVerticalStr"
    },
    "created_at": {
        "field_id": "h3i29a03-6091-47f7-93f3-7e6f6796fah7",
        "field_type": "stringValue",
        "field_name_kustomer": "createdAtStr"
    },
    "place_at": {
        "field_id": "i4j30a04-7092-48f8-94f4-8e7f7797fai8",
        "field_type": "stringValue",
        "field_name_kustomer": "placeAtStr"
    },
    "store_type_store": {
        "field_id": "j5k31a05-8093-49f9-95f5-9e8f8798faj9",
        "field_type": "stringValue",
        "field_name_kustomer": "storeTypeStoreStr"
    },
    "store_id": {
        "field_id": "k6l32a06-9094-50f0-96f6-0e9f9799fak0",
        "field_type": "stringValue",
        "field_name_kustomer": "storeIdStr"
    },
    "store_type": {
        "field_id": "l7m33a07-0095-51f1-97f7-1e0f0800fal1",
        "field_type": "stringValue",
        "field_name_kustomer": "storeTypeStr"
    },
    "order_debt": {
        "field_id": "m8n34a08-1096-52f2-98f8-2e1f1801fam2",
        "field_type": "stringValue",
        "field_name_kustomer": "orderDebtStr"
    },
    "order_has_debt": {
        "field_id": "n9o35a09-2097-53f3-99f9-3e2f2802fan3",
        "field_type": "stringValue",
        "field_name_kustomer": "orderHasDebtStr"
    },
    "storekeeper_id": {
        "field_id": "o0p36a10-3098-54f4-00f0-4e3f3803fao4",
        "field_type": "stringValue",
        "field_name_kustomer": "storekeeperIdStr"
    },
    "language": {
        "field_id": "p1q37a11-4099-55f5-01f1-5e4f4804fap5",
        "field_type": "stringValue",
        "field_name_kustomer": "languageStr"
    },
    "country": {
        "field_id": "q2r38a12-5000-56f6-02f2-6e5f5805faq6",
        "field_type": "stringValue",
        "field_name_kustomer": "countryStr"
    },
    "last_order_canceled_by_fraud": {
        "field_id": "r3s39a13-6001-57f7-03f3-7e6f6806far7",
        "field_type": "stringValue",
        "field_name_kustomer": "lastOrderCanceledByFraudStr"
    },
    "loyalty_program": {
        "field_id": "s4t40a14-7002-58f8-04f4-8e7f7807fas8",
        "field_type": "stringValue",
        "field_name_kustomer": "loyaltyProgramStr"
    },
    "store_name": {
        "field_id": "t5u41a15-8003-59f9-05f5-9e8f8808fat9",
        "field_type": "stringValue",
        "field_name_kustomer": "storeNameStr"
    },
    "churn": {
        "field_id": "u6v42a16-9004-60f0-06f6-0e9f9809fau0",
        "field_type": "stringValue",
        "field_name_kustomer": "churnStr"
    },
    "look_alike_score": {
        "field_id": "v7w43a17-0005-61f1-07f7-1e0f0810fav1",
        "field_type": "stringValue",
        "field_name_kustomer": "lookAlikeScoreStr"
    },
    "rfm_segment": {
        "field_id": "w8x44a18-1006-62f2-08f8-2e1f1811faw2",
        "field_type": "stringValue",
        "field_name_kustomer": "rfmSegmentStr"
    },
    "finance_user_type": {
        "field_id": "x9y45a19-2007-63f3-09f9-3e2f2812fax3",
        "field_type": "stringValue",
        "field_name_kustomer": "financeUserTypeStr"
    },
    "is_prime": {
        "field_id": "y0z46a20-3008-64f4-10f0-4e3f3813fay4",
        "field_type": "stringValue",
        "field_name_kustomer": "isPrimeStr"
    },
    "total_debt": {
        "field_id": "z1a47a21-4009-65f5-11f1-5e4f4814faz5",
        "field_type": "stringValue",
        "field_name_kustomer": "totalDebtStr"
    },
    "type_category_hc": {
        "field_id": "a2b48a22-5010-66f6-12f2-6e5f5815faa6",
        "field_type": "stringValue",
        "field_name_kustomer": "contactReasonStr"
    },
    "tipoYCategoriaRtsTree": {
        "field_id": "b3c49a23-6011-67f7-13f3-7e6f6816fab7",
        "field_type": "stringValue",
        "field_name_kustomer": "tipoYCategoriaRtsTreeStr"
    },
    "conversation_lang": {
        "field_id": "c4d50a24-7012-68f8-14f4-8e7f7817fac8",
        "field_type": "stringValue",
        "field_name_kustomer": "conversationLangStr"
    }
}
"""
FIELD_MAPPINGS = {}
# Simplified function to replace get_field_info_by_api_name from DynamoDB
def get_field_info_by_api_name(table_name, field_name_api):
    """
    Returns field information based on the API field name.
    This is a hardcoded replacement for the DynamoDB query.
    
    Args:
        table_name: Ignored since we're using hardcoded values
        field_name_api: The API field name to look up
        
    Returns:
        Dict containing field information or None if not found
    """
    return FIELD_MAPPINGS.get(field_name_api)