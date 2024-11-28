import azure.functions as func
import logging
from util.helper import get_openai_client
from util.qa import get_test_case_csv
import json
from datetime import timezone 
import datetime
import pandas as pd
import re

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logging.info('AI COE BA-QA-i : QA-i Triggered Requirement function.')

        body = req.get_json()
        qtest_fields = body.get('qtest_fields', {})
        requirement_input = body.get('chat_history')
        req_text = requirement_input[-1]['content']

        if '~debug~debug~debug~'in req_text:
            raise Exception("Exception triggered by debugging.")

        # logging.info('AI COE BA-QA-i : QA-i Input - ' + req_text)

        # logging.info(json.dumps(body))

        client, async_client = get_openai_client('2023-12-01-preview')
        
        seed = None if "#random" in req_text else 1
        req_text = req_text.replace('#random', '')
                
        try:
            test_case_csv_string, test_case_response, test_case_count = get_test_case_csv(req_text, qtest_fields, client, seed)
        except:
            test_case_csv_string, test_case_response, test_case_count = (pd.DataFrame({'A': [1, 2], 'B': [3, 4]}).to_csv(index=False), '', 0)

        dt = datetime.datetime.now(timezone.utc) 
        utc = dt.replace(tzinfo=timezone.utc)
        file_date = datetime.datetime.now().strftime('%Y_%m_%d')

        response = {}
        response['metadata'] = {'tokens_remaining' : 123}

        response['response'] = {'role' : 'system', 
                                'content' : 'Here is your Test Cases & Test Steps spreadsheet. Make sure to verify the information & fill in any additional required fields.',
                                'type' : 'testcase',
                                'resources' : [
                                    {
                                        'type' : 'csv',
                                        'body' : test_case_csv_string,
                                        'filename' : f'{file_date}.csv',
                                        'friendly_body' : test_case_response,
                                        'test_case_count' : test_case_count
                                    }
                                ],
                                'timestamp' : str(utc) 
                                }
        
        # logging.info(json.dumps(response))
        #Need to test the logging of this
        #logging.info('AI COE BA-QA-i : BA-i Request Response - ' + test_case_csv_string)
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
