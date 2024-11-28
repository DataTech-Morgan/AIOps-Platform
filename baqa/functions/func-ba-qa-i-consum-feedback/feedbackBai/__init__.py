import azure.functions as func
import logging
from util.feedback import *
import json
from datetime import timezone 
import datetime
import pandas as pd

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logging.info('Python trigger function processed a request.')

        request_body = req.get_json()
        chat_history = request_body.get('chat_history')
        tool = request_body.get('tool', '')
        other_req_fields = request_body
        other_req_fields.pop('chat_history')

        user_msgs = [chat for chat in chat_history if chat['role'] == 'user']

        convo_hash = id_from_string(' '.join([chat['content'] for chat in chat_history]))
        init_input_hash = id_from_string(user_msgs[0]['content'])

        dt = datetime.datetime.now(timezone.utc) 
        utc = str(dt.replace(tzinfo=timezone.utc))

        to_log = []

        for i in range(0, len(chat_history)):
            chat = chat_history[i]
            if (chat.get('thumb_feedback') is not None) and (chat.get('thumb_feedback') != ''):
                feedback = chat['thumb_feedback']
                try:
                    prev_message = chat_history[i - 1]
                    assert prev_message['role'] == 'user'
                    prev_input_hash = id_from_string(prev_message['content'])
                except:
                    prev_message = {}
                    prev_input_hash = None

                feedback_data = {
                                    # 'chat_history' : chat_history,
                                    'tool' : tool,
                                    'conversation_id' : convo_hash,
                                    'init_input_id' : init_input_hash, 
                                    'prev_input_id' : prev_input_hash,
                                    'thumb_feedback' : feedback,
                                    # 'output_message' : chat,
                                    # 'input_message' : prev_message,
                                    'timestamp' : utc} 
                feedback_data = feedback_data | other_req_fields

                to_log.append(feedback_data)
        
        [logging.info(json.dumps(feedback)) for feedback in to_log]

        return func.HttpResponse(body = None, status_code=200, mimetype = 'application/json')

    except Exception as e:
        logging.exception(f"An error occurred: {str(e)}")
        return func.HttpResponse(
            body = None, status_code=500
        )
