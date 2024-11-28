import os
# import tiktoken
from openai import AzureOpenAI, AsyncAzureOpenAI
from azure.identity import ClientSecretCredential
from util.text_processing import *

def call_chat(self, messages, seed = None, temperature = 1):
    response = self.chat.completions.create(
                model=os.environ['openai_deployment_name'],
                messages=messages,
                seed=seed
                )
    message_response = response.choices[0].message.content
    return message_response

def get_openai_client(api_version = "2023-12-01-preview"):

    credential = ClientSecretCredential(tenant_id=os.getenv('openai_tenant_id'), 
                                        client_id=os.getenv('openai_client_id'), 
                                        client_secret=os.getenv('openai_client_secret'))
    
    jwt = credential.get_token("api://{}".format(os.getenv('openai_credential_scope')))
    token = jwt.token
    AzureOpenAI.call_chat = call_chat
    client = AzureOpenAI(
        api_key = token,  
        api_version=api_version,
        azure_endpoint = os.getenv('openai_api_base'),
        )
    jwt = credential.get_token("api://{}".format(os.environ['openai_credential_scope']))
    token = jwt.token
    async_client = AsyncAzureOpenAI(
        api_key = token,
        api_version="2023-12-01-preview",
        azure_endpoint = os.environ['openai_api_base'],
        default_headers = {}
        )
    return client, async_client

# def count_tokens(string: str, encoding_name: str = 'cl100k_base') -> int:
#     encoding = tiktoken.get_encoding(encoding_name)
#     num_tokens = len(encoding.encode(string))
#     return num_tokens