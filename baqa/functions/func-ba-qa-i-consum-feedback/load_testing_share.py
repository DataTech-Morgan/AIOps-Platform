import json
from azure.identity import ClientSecretCredential
import random
import pandas as pd
import numpy as np
import os
import time
import asyncio
import aiohttp

# Environment variables for tenant_id, client_id, client_secret, scope, and apim_url to authenticate to the APIM endpoint you are testing.
# apim_url is the base url.
from dotenv import load_dotenv
load_dotenv('testing.env')

# Set default_endpoint to the endpoint you want to test.
    # ex. apim_url is https://apim-to-dev-aiml-a.jmfamily.com/jma/v1.0/functionapp/ and endpoint is requirementsBai. 
default_endpoint = ''

def get_token():

    credential = ClientSecretCredential(tenant_id=os.environ['tenant_id'],
                                    client_id=os.environ['client_id'],
                                    client_secret=os.environ['client_secret'])
    jwt = credential.get_token(os.environ['scope'])
    token = jwt.token
    
    return token

stories = ['''As a NC System, when document of any type is received from TMNA, the document will be persisted, if the distCd is present and match 91041, (Mandatory) 

As a NC System, when document of any type is received from TMNA, the document will be ignored, if the distCd is present and not match 91041,

As a NC System, when document of any type is received from TMNA, the document will be ignored, if the distCd is not present and IgnoreMissingDistCodeDocs = true (Default = True) 

As a NC System, when document of any type is received from TMNA, the document will be persisted, if the distCd is not present and IgnoreMissingDistCodeDocs = false ''',
'''Perform analysis to come up with the requirements needed to restructure the way eWorkOrder handles authorization.

Currently authorization is managed by roles which are hard coded within the mobile app to specfic features.
For example, Supervisor role can access features:  A,C,D,E but Driver can only access A and E (just fake examples).

Confirm the new requirements by documenting the new requirements along with what needs to happen to make such a transition.  Some questions to ask would be:

Should we redefine roles to be per feature?
Should we keep the existing roles but make them dynamic such that the feature assignment of a role is based on a database collection? 
We can consider other roles beyond just access to a feature, such as FeatureA_Readonly and/or FeatureA_DriveOnly
Once the implementation is restructured, how do we deal with placing users into the new roles?  Is there an automated way (script in which ITSAccess can come up with?)

Database collection approach:

Imagine this is a record in the database.  At any given time we could add or remove tokens from the below.  For example, imagine we want to disable work order printing for this role, we would just remove the token VehiclePrintWorkOrderButton from below.  The mobile app could refresh the rules either between login sessions or every time a user comes back into the app from background to foreground.

"set_eworkorder_arrival_users":[
                    "RailArrivalsView"
                    "ShipArrivalsView"
                    "VehicleDriveButtonProd"
                    "VehiclePrintWorkOrderButton"
                    "FindVehicleView"
                ]
''',
'''In order to prevent pre-payment cancellations from being sent to NetSuite
the team
needs to prevent Vendor Invoices with a negative amount and an INVOICETYPE of "VendorAdvance" from being sent to Netsuite

Prepayments are sent to NetSuite as a Vendor Invoice.  Those work correctly.  
When one of those prepayments need to be cancelled, it will first be cancelled in NetSuite.  
Then, the prepayemnt will be cancelled in D365.  This will create a negative vendor invoice and will be sent out of D365.
Since this prepayment has already been cancelled in NetSuite, we do NOT want the D365 record sent to NetSuite.  

Prevent the following vendor Invoice type from going to NetSuite
 - INVOICETYPE = VendorAdvance
  - Amount is negative 

This story was created in response to Defect 401104''',
'''As an eWO service advocate , I want to restrict user access to eWO web functions based on the AD group to app token configuration so that users will be presented with menu options that he is configured to use '''
]

request_template = {
  "chat_history": [
    {
      "role": "user",
      "content": "As a parts analyst, I need item velocity code rules added for p-coded parts So that the P-Coded parts are not removed from stocking during item eligibility updates in the P&F system. #validate",
      "resources": []
    }
  ],
  "enabler" : False,
  "enabler_type": "Spike"
}

def generate_random_requests(request_template, stories, num_users):
    request_bodies = []
    for i in range(0, num_users):
        #############################################################
        request_body = request_template.copy()
        request_body['chat_history'][0]['content'] = random.sample(stories, 1)[0]
        request_body['enabler'] = random.sample([True, False ], 1)[0]
        request_body['user'] = i
        #############################################################
        request_bodies.append(request_body)
    return request_bodies

async def async_request(session, request_body, token, endpoint):
    print(f'''User: {str(request_body['user'])}''')
    start = time.time()
    async with session.post(url = os.environ['apim_url'] + endpoint,
                                    data = json.dumps(request_body),
                                    headers={'Authorization': f'Bearer {token}'}) as response:
          data = await response.json()
          end = time.time()
          r_time = end - start
          return data, r_time

async def concurrent_users_requests(request_body_sets, token, sleep_seconds, endpoint = default_endpoint):
    async with aiohttp.ClientSession() as session:
        res_lists = []
        for request_body_set in request_body_sets:
            res = await asyncio.gather(*(async_request(session, request_body, token, endpoint) for request_body in request_body_set))
            res_lists.append(res)
            time.sleep(sleep_seconds)
        return res_lists

def async_run(coro, *args, **kwargs):
    return asyncio.run(coro, *args, **kwargs)

########## Parameters of your load test
num_users = 4 # Concurrent users
num_requests = 15 # How many total requests end user will send
sleep_seconds = 5 # How long will each user wait before they send another request, after they receive a response back
####################

token = get_token()
request_body_sets = [generate_random_requests(request_template = request_template, stories = stories, num_users = num_users) for _ in range(0, num_requests)]

start = time.time()
responses = async_run(concurrent_users_requests(request_body_sets, token, sleep_seconds)) 
end = time.time()

test_len = end - start
test_len

times = []
contents = []
for reqnum in responses:
    for user in reqnum:
        response_time = user[1]
        response_data = user[0]['response']
        msg = response_data['content']
        times.append(response_time)
        contents.append(msg)

from statistics import mean, median
print(mean(times))
print(median(times))

print(len(contents))
# Checking for a specific error mentioned in the response
print(len([c for c in contents if 'rate limit' in c.lower()]))