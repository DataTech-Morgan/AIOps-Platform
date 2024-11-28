import azure.functions as func
import logging
from util.helper import get_openai_client
import json
from datetime import timezone 
import datetime
import azure.functions as func
import logging
from util.qa import get_bai_response
import pandas as pd
import re

logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logging.info('AI COE BA-QA-i : BA-i Triggered Requirement function.')

        body = req.get_json()
        requirement_input = body.get('chat_history')
        req_text = requirement_input[-1]['content']

        story_type = body.get('enabler', False)
        logging.info('AI COE BA-QA-i : BA-i Enabler - ' + str(story_type))
        enabler_type = body.get('enabler_type', '')
        logging.info('AI COE BA-QA-i : BA-i Enabler Type - ' + str(enabler_type))
        enabler_list_format = body.get('enabler_list_format', False)
        logging.info('AI COE BA-QA-i : BA-i Enabler List Format - ' + str(enabler_list_format))

        if '~debug~debug~debug~'in req_text:
            raise Exception("Exception triggered by debugging.")

        # logging.info('AI COE BA-QA-i : BA-i Input - ' + req_text)
        # logging.info(json.dumps(body))

        client, async_client = get_openai_client('2023-12-01-preview')
        
        seed = None if "#random" in req_text else 1
        req_text = req_text.replace('#random', '')
        
        chat_response = get_bai_response(req_text, 
                                        story_type, 
                                        enabler_type,
                                        enabler_list_format,
                                        client,
                                        async_client, 
                                        seed
                                        )
        
        # logging.info('AI COE BA-QA-i : BA-i Response - ' + chat_response)

        dt = datetime.datetime.now(timezone.utc) 
        utc = dt.replace(tzinfo=timezone.utc)

        response = {}
        response['metadata'] = {'tokens_remaining' : 123}

        response['response'] = {'role' : 'system', 
                                'type' : 'testcase',
                                'resources' : [],
                                'timestamp' : str(utc) 
                                } | chat_response
        
        # logging.info(json.dumps(response))

        return func.HttpResponse(json.dumps(response), status_code=200, mimetype = 'application/json')
            
    except Exception as e:
        logging.exception(f"An error occurred: {str(e)}")
        response = {}
        dt = datetime.datetime.now(timezone.utc) 
        utc = dt.replace(tzinfo=timezone.utc)
        response['metadata'] = {'tokens_remaining' : 123}

        response['response'] = {'role' : 'system', 
                                'content' : f"Please contact support and provide the following details.\n\nAn error occurred: {str(e)}",
                                'type' : 'testcase',
                                'resources' : [],
                                'timestamp' : str(utc) 
                                }
        logging.info(json.dumps(response))
        return func.HttpResponse(json.dumps(response), status_code=500, mimetype = 'application/json')