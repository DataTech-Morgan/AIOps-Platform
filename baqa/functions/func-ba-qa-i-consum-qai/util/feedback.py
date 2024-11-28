import uuid
import hashlib
# from azure.cosmos import CosmosClient
import os

def id_from_string(val: str):
    hex_string = hashlib.md5(val.encode("UTF-8")).hexdigest()
    return str(uuid.UUID(hex=hex_string))

# def connect_to_cosmos(credential):

#     cosmos_client = CosmosClient(url=os.environ['cosmos_url'], credential=credential)
#     cosmos_db = cosmos_client.get_database_client(os.environ['cosmos_dbname'])

#     return cosmos_db