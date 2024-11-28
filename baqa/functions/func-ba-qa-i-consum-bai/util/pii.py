import os
# import tiktoken
from azure.identity import ClientSecretCredential
import requests
from typing import List, Dict
import json

# from dotenv import load_dotenv
# load_dotenv('testing.env')

def get_pii_token():

    credential = ClientSecretCredential(tenant_id=os.getenv('pii_tenant_id'), 
                                        client_id=os.getenv('pii_client_id'), 
                                        client_secret=os.getenv('pii_client_secret'))
    
    jwt = credential.get_token(os.getenv('pii_credential_scope'))
    token = jwt.token

    return token

# Function to process messages for PII
def process_pii(text, token: str) -> List[Dict]:

    # Prepare request body for PII recognition
    body = { "kind": "PiiEntityRecognition",
            "parameters": {
                "modelVersion": "latest",
                "piiCategories": [
                "Person",
                "PhoneNumber",
                "Organization",
                "Address",
                "Email",
                "IPAddress",
                "ABARoutingNumber",
                "SWIFTCode",
                "CreditCardNumber",
                "InternationalBankingAccountNumber",
                "USSocialSecurityNumber",
                "USDriversLicenseNumber",
                "USUKPassportNumber",
                "USIndividualTaxpayerIdentification",
                "USBankAccountNumber"
                ]
            },
            "analysisInput": {
                "documents": [
                {
                    "language": "en",
                    "id": "1",
                    "text": text
                }
                ]
            }
        }
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # Send request to the PII recognition service
    response = requests.post(url = os.getenv('pii_endpoint'), headers=headers, data=json.dumps(body))

    return dict(response.json()).get("results", {}).get("documents", [])

def remove_pii(text):

  token = get_pii_token()
  pii_documents = process_pii(text, token)
  redacted_text = [doc['redactedText'] for doc in pii_documents][0]

  return redacted_text

# Function to redact sensitive information based on PII analysis
# def redact_pii(original_text, pii_doc: List[Dict]) -> List[Dict]:
#     entities = pii_doc.get("entities", [])
#     # redacted_text = pii_doc["redactedText"]
#     masked_text = original_text
#     for entity in entities:
#         confidence_score = entity.get("confidenceScore", 0)
#         category = entity.get("category", "")
#         text = entity.get("text", "")

#         if category in ["Person",
#         "PhoneNumber",
#         "Organization",
#         "Address",
#         "Email",
#         "IPAddress",
#         "ABARoutingNumber",
#         "SWIFTCode",
#         "CreditCardNumber",
#         "InternationalBankingAccountNumber",
#         "USSocialSecurityNumber",
#         "USDriversLicenseNumber",
#         "USUKPassportNumber",
#         "USIndividualTaxpayerIdentification",
#         "USBankAccountNumber"]:
#             masked_text = masked_text.replace(text, '*' * len(text))

#     return masked_text


# {
#   "type": "Foreach",
#   "foreach": "@outputs('Parse_PII_Removal')?['body']?['results']?['documents']",
#   "actions": {
#     "Set_Redacted_Text": {
#       "type": "SetVariable",
#       "inputs": {
#         "name": "RedactedText",
#         "value": "@concat(items('Each_Document')?['redactedText'], '    ')"
#       }
#     },
#     "Each_Entities": {
#       "type": "Foreach",
#       "foreach": "@items('Each_Document')?['entities']",
#       "actions": {
#         "Set_Left_Entities": {
#           "type": "SetVariable",
#           "inputs": {
#             "name": "LeftEntities",
#             "value": "@concat(\r\n  substring(variables('RedactedText'), 0, items('Each_Entities')?['offset']),\r\n  items('Each_Entities')?['text']\r\n)"
#           }
#         },
#         "Set_Offset_Length": {
#           "type": "SetVariable",
#           "inputs": {
#             "name": "EntitiesLength",
#             "value": "@add(items('Each_Entities')?['offset'], items('Each_Entities')?['length'])"
#           }
#         },
#         "Set_Right_Entities": {
#           "type": "SetVariable",
#           "inputs": {
#             "name": "RightEntities",
#             "value": "@substring(variables('RedactedText'), variables('EntitiesLength'), variables('RightRedactedLength'))"
#           }
#         },
#         "Update_Redacted": {
#           "type": "SetVariable",
#           "inputs": {
#             "name": "RedactedText",
#             "value": "@concat(variables('LeftEntities'), variables('RightEntities'))"
#           },
#           "runAfter": {
#             "Set_Right_Entities": [
#               "Succeeded"
#             ]
#           }
#         },
#         "Set_Right_Length": {
#           "type": "SetVariable",
#           "inputs": {
#             "name": "RightRedactedLength",
#             "value": "@if(equals(sub(variables('RedactedLength'), variables('EntitiesLength')), 0), 1, sub(variables('RedactedLength'), variables('EntitiesLength')))"
#           }
#         },
#         "Set_Redacted_Length": {
#           "type": "SetVariable",
#           "inputs": {
#             "name": "RedactedLength",
#             "value": "@length(variables('RedactedText'))"
#           }
#         }

