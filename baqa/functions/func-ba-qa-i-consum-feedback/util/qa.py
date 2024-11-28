from io import StringIO
from datetime import timezone 
import datetime
import pandas as pd
import util.prompts as prompts
import util.json_repair as json_repair
import numpy as np
import logging
import asyncio
import os

# [{"role": "system", "content": message_prompt},
#             {"role": "user", "content": question}]

async def async_chat(message_list, async_client, seed = None):
    if len(message_list) == 0:
        return ''
    response = await async_client.chat.completions.create(
        model=os.environ['openai_deployment_name'],
        messages=message_list,
        seed = seed,
    )
    return response.choices[0].message.content

async def wait_for_chat(message_lists, async_client, seed):
    # resps = []
    # for message_list in message_lists:
    #     print(message_list)
    #     if len(message_list) > 0:
    #         res = await asyncio.gather(*(async_chat(message_list, async_client, seed)))
    #     else:
    #         res = ''
    #     resps.append(res)
    resps = await asyncio.gather(*(async_chat(message_list, async_client, seed) for message_list in message_lists))
    return resps

def async_run(coro, *args, **kwargs):
    """Azure uses already asyncio.run and it cannot be nested, so if run in Azure, we take their event loop"""
    # try:
    #     loop = asyncio.get_running_loop()
    # except RuntimeError:
    if coro == '':
        return ''
    return asyncio.run(coro, *args, **kwargs)
    # else:
    #     return loop.run_until_complete(coro(*args, **kwargs))

def validate_story_detail_prompt(req_text, enabler):
    if enabler == True:
        messages = [{"role": "system", "content": prompts.enabler_story_val_sys}, 
                        {"role": "user","content": prompts.enabler_story_val_user.format(story=req_text)}
                    ]
    else:
        messages = [{"role": "system", "content": prompts.user_story_val_sys}, 
                        {"role": "user","content": prompts.user_story_val_user.format(story=req_text)}
                    ]
    return messages


def validate_story_detail(response, always_suggest = False):
    suggestions = ''
    try:
        response_json = json_repair.loads(response)
        # logging.info(response_json)
        score = float(response_json['Overall Score'])
        logging.info('AI COE BA-QA-i : BA-i Validation Score - ' + str(score))
    except:
        return suggestions

    if score < 8 or always_suggest == True:
        suggestions = ''.join(['\n\u2022 ' + sug for sug in response_json['Suggestions']])
        suggestions = 'Consider updating your story to follow INVEST principles:\n' + suggestions
    else:
        suggestions = 'Your story contains a good level of detail and is clear to understand.'
    # logging.info(suggestions)
    return suggestions


def validate_user_story_syntax_prompts(req_text, enabler):
    message_set = [[ {"role": "system","content": prompts.requirement_syntax_validation_sys},
                    {"role": "user","content": prompts.syntax_user.format(story=req_text)}
                ]]
    if enabler == False:
        messages = [ {"role": "system","content": prompts.requirement_syntax_rewrite_sys},
                            {"role": "user","content": prompts.syntax_user.format(story=req_text)}
                        ]
    else:
        messages = []
    message_set.append(messages)
    return message_set


def validate_user_story_syntax(responses, req_text, enabler):


    response = responses[0]
    
    rewrite_story = ''

    if (response.startswith('No') and enabler == False) or ( ('as a' not in req_text.lower() or 'so that' not in req_text.lower()) and enabler == False):

        rewrite_story = responses[1]
        try:
            rewrite_story = json_repair.loads(rewrite_story)['UpdatedStory']
        except:
            return ''

    if rewrite_story != '' and enabler == False:
        rewrite_story = 'Consider using the preferred user story format below: ' + '\n\n' + rewrite_story
    elif response.startswith('Yes') and enabler == True:
        rewrite_story = 'Are you working on a user story? If not, it might be easier to use the enabler story format: In order to (business value), the (technical user), needs to (technical task).'
    elif response.startswith('Yes') and enabler == False:
        rewrite_story = 'Your story is written in the appropriate format: As a (who/user role), I want to (verb/goal), so that (why/benefit).'
    else:
        rewrite_story = ''

    return rewrite_story

def validate_enabler_story_syntax_prompts(req_text, enabler):
    message_set = [[ {"role": "system","content": prompts.enabler_syntax_validation_sys},
                    {"role": "user","content": prompts.syntax_user.format(story=req_text)}
                ]]
    if enabler == True:
        messages = [ {"role": "system","content": prompts.enabler_syntax_rewrite_sys},
                        {"role": "user","content": prompts.syntax_user.format(story=req_text)}
                    ]
    else:
        messages = []
    message_set.append(messages)
    return message_set


def validate_enabler_story_syntax(responses, enabler):

    response = responses[0]

    rewrite_story = ''

    if response.startswith('No') and enabler == True:

        rewrite_story = responses[1]
        try:
            rewrite_story = json_repair.loads(rewrite_story)['UpdatedStory']
        except:
            return ''

    if rewrite_story != '' and enabler == True:
        rewrite_story = 'Consider using the preferred enabler story format below: ' + '\n\n' + rewrite_story
    elif response.startswith('Yes') and enabler == False:
        rewrite_story = 'Are you working on an enabler story? If not, consider rewriting in the user story format: As a (who/user role), I want to (verb/goal), so that (why/benefit).'
    elif response.startswith('Yes') and enabler == True:
        rewrite_story = 'Your story is written in the appropriate format: In order to (business value), the (technical user), needs to (technical task).'
    else:
        rewrite_story = ''
    
    return rewrite_story


def combine_syntax_responses(syntax_check_response_user, syntax_check_response_enabler):
    if ('Consider using the preferred' in syntax_check_response_user) and ('Are you working on' in syntax_check_response_enabler):
        syntax_check_response_enabler = syntax_check_response_enabler.split(':')[0] + ':' + ':'.join(syntax_check_response_user.split(':')[-1:])
        syntax_check_response_user = ''

    elif ('Consider using the preferred' in syntax_check_response_enabler) and ('Are you working on' in syntax_check_response_user):
        syntax_check_response_user = syntax_check_response_user.split(':')[0] + ':' + ':'.join(syntax_check_response_enabler.split(':')[-1:])
        syntax_check_response_enabler = ''

    logging.info('AI COE BA-QA-i : BA-i Syntax Validation - ' + syntax_check_response_user)
    logging.info('AI COE BA-QA-i : BA-i Enabler Syntax Validation - ' + syntax_check_response_enabler)

    return syntax_check_response_user, syntax_check_response_enabler


def validate_enabler_type_prompt(req_text, enabler_type):
    messages = [ {"role": "system","content": prompts.enabler_type_sys},
                        {"role": "user","content": prompts.enabler_type_user.format(story=req_text, enabler_type=enabler_type)}
                    ]
    return messages

def validate_enabler_type(validate_type_response):
    
    logging.info('AI COE BA-QA-i : BA-i Enabler Type Validation - ' + validate_type_response)
    if 'No change' in validate_type_response:
        return ''
    else:
        return validate_type_response

def validate_strong_persona_prompts(req_text):
    messages = [ {"role": "system","content": prompts.persona_val_sys},
                        {"role": "user","content": req_text}
                    ]
    return messages

def validate_strong_persona(response, req_text, client, seed):

    if response.startswith('Weak'):
        response = client.call_chat(messages = [ {"role": "system","content": prompts.persona_val_sys},
                        {"role": "user","content": req_text},
                        {"role" : "assistant" , "content" : response},
                        {"role" : "user", "content" : "Respond with a very brief, one sentence suggestion of how and why to improve the persona. Include the existing persona somewhere in your response."}
                    ], seed = seed)
    else:
        response = ''
    logging.info('AI COE BA-QA-i : BA-i Persona Validation - ' + response)
    return response

def get_ac_prompt(req_text, enabler, enabler_type, enabler_list_format):
    if enabler == True:
        system = prompts.gherkin_sys_enabler if enabler_list_format == False else prompts.list_sys
        user = prompts.ba_enabler_story.format(story = req_text, enabler_type = enabler_type)
    else:
        system = prompts.gherkin_sys_user
        user = prompts.ba_user_story.format(story = req_text)
    messages = [{"role": "system", "content": system},
                {"role": "user","content": user}
            ]
    return messages

def get_bai_response(req_text, enabler, enabler_type, enabler_list_format, client, async_client, seed):
    
    req_text = req_text.replace('#validate', '')
    detail_check_prompt = validate_story_detail_prompt(req_text, enabler)
    syntax_check_response_user_prompts = validate_user_story_syntax_prompts(req_text, enabler)
    syntax_check_response_enabler_prompts = validate_enabler_story_syntax_prompts(req_text, enabler)
    ac_prompt = get_ac_prompt(req_text, enabler, enabler_type, enabler_list_format)
    prompt_set = [detail_check_prompt]
    prompt_set.extend(syntax_check_response_user_prompts)
    prompt_set.extend(syntax_check_response_enabler_prompts)
    prompt_set.append(ac_prompt)
    if enabler == True:
        enabler_type_prompt = validate_enabler_type_prompt(req_text, enabler_type)
        prompt_set.append(enabler_type_prompt)
        # enabler_type_response = validate_enabler_type(req_text, enabler_type, client, seed)
    else:
        persona_check_prompt = validate_strong_persona_prompts(req_text)
        prompt_set.append(persona_check_prompt)
        # persona_check_response = validate_strong_persona(req_text, client, seed)
    
    responses = async_run(wait_for_chat(prompt_set, async_client, seed)) 

    detail_check_response = validate_story_detail(responses[0])
    syntax_check_response_user = validate_user_story_syntax(responses[1:3], req_text, enabler)
    syntax_check_response_enabler = validate_enabler_story_syntax(responses[4:5], enabler)
    syntax_check_response_user, syntax_check_response_enabler = combine_syntax_responses(syntax_check_response_user, syntax_check_response_enabler)
    enabler_type_response = ''
    persona_check_response = ''
    if enabler == True:
        enabler_type_response = validate_enabler_type(responses[-1])
    else:
        persona_check_response = validate_strong_persona(responses[-1], req_text, client, seed)
    
    ac_response = responses[5]

    # guardrail_response = [detail_check_response, enabler_type_response, persona_check_response, syntax_check_response_user, syntax_check_response_enabler]
    # guardrail_response = [r for r in guardrail_response if r != '']
    # guardrail_response = '\n\n~|~|~|~\n\n'.join(guardrail_response)
    # guardrail_response = guardrail_response.replace('\n\n\n\n', '\n\n')

    response_dict = {
        'content' : ac_response,
        'suggestions' : '\n\n'.join([r for r in [detail_check_response, enabler_type_response, persona_check_response] if r != '']),
        'revisions' : '\n\n'.join([r for r in [syntax_check_response_user, syntax_check_response_enabler] if r != '']),
        'acceptance_criteria' : ac_response
    }

    return response_dict

# def get_testable_ac(req_text, enabler, enabler_type, enabler_list_format, client, seed):

#     # if '#validate' in req_text:
#     logging.info('AI COE BA-QA-i : BA-i Validation Requested')
#     req_text = req_text.replace('#validate', '')
#     detail_check_response = validate_story_detail(req_text, client, enabler, seed)
#     syntax_check_response_user = validate_user_story_syntax(req_text, client, enabler, seed)
#     syntax_check_response_enabler = validate_enabler_story_syntax(req_text, client, enabler, seed)
#     syntax_check_response_user, syntax_check_response_enabler = combine_syntax_responses(syntax_check_response_user, syntax_check_response_enabler)
#     enabler_type_response = ''
#     persona_check_response = ''
#     if enabler == True:
#         enabler_type_response = validate_enabler_type(req_text, enabler_type, client, seed)
#     else:
#         persona_check_response = validate_strong_persona(req_text, client, seed)
#     guardrail_response = [detail_check_response, enabler_type_response, persona_check_response, syntax_check_response_user, syntax_check_response_enabler]
#     guardrail_response = [r for r in guardrail_response if r != '']
#     guardrail_response = '\n\n~|~|~|~\n\n'.join(guardrail_response)
#     #If there is a suggestion
#     guardrail_response = guardrail_response.replace('\n\n\n\n', '\n\n')
    
#     if enabler == True:
#         system = prompts.gherkin_sys_enabler if enabler_list_format == False else prompts.list_sys
#         user = prompts.ba_enabler_story.format(story = req_text, enabler_type = enabler_type)
#     else:
#         system = prompts.gherkin_sys_user
#         user = prompts.ba_user_story.format(story = req_text)

#     chat_response = client.call_chat(messages=[{"role": "system", "content": system},
#                                                 {"role": "user","content": user}
#                                             ], seed = seed)

#     return chat_response




def format_qtest_template(table_response, qtest_fields):

    req_table = pd.read_csv(
        StringIO(table_response), 
        sep='|'
    )

    if len(req_table.columns) < 5:
        req_table = pd.read_csv(
            StringIO(table_response), 
            sep='|',
            header = 1
        )

    req_table.columns = [i.strip() for i in req_table.columns]
    req_table = req_table[[col for col in req_table.columns if 'Unnamed' not in col]]
    
    req_table = req_table.replace('<br>',', ', regex=True)
    req_table = req_table.replace('%%%','|', regex=True)
    
    req_table[req_table.select_dtypes('object').columns] = req_table.select_dtypes('object').apply(lambda x: x.str.strip())
    
    for null_placeholder in ['N/A', '---', '']:
        req_table = req_table.replace(null_placeholder, np.nan)

    req_table['Test Case Name'] = req_table['Test Case Name'].fillna(method = 'ffill')

    req_table.columns = ['Test Case Name', 'Description', 'Precondition', 'Test Step #', 'Test Step Description', 'Test Step Expected Result']

    req_table = req_table[req_table['Test Step #'].str.replace('-', '').str.replace(' ', '').str.len() > 0]
    req_table['Test Step #'] = req_table.groupby('Test Case Name')['Test Step #'].transform(lambda x: pd.factorize(x)[0] + 1).astype(str)

    req_table.loc[req_table['Test Case Name'].duplicated(), 'Test Case Name'] = np.nan

    req_table['Type'] = qtest_fields.get('type', 'Manual')
    req_table['Status'] = qtest_fields.get('status', 'New')

    req_table['Priority'] = qtest_fields.get('priority', 'Medium')
    req_table['Assigned To'] = qtest_fields.get('assigned_to', np.nan)
    req_table['Automation Progress'] = qtest_fields.get('automation_progress', 'No')

    req_table['Requirements'] = qtest_fields.get('requirements', np.nan)

    req_table.loc[req_table['Test Case Name'].isna(), 
                ['Description', 'Precondition', 'Type', 'Status',
                'Priority', 'Assigned To', 
                'Automation Progress', 'Requirements']] = np.nan
    
    test_case_count = req_table['Test Case Name'].dropna().nunique()

    logging.info('AI COE BA-QA-i : QA-i Requirement IDs - ' + str(qtest_fields.get('requirements', '')))

    logging.info('AI COE BA-QA-i : QA-i Test Cases Generated - ' + str(test_case_count))
    
    logging.info('AI COE BA-QA-i : QA-i Total Test Steps Generated - ' + str(len(req_table)))

    return req_table, test_case_count


def retry(times):
    """
        Retry Decorator
        Retries the wrapped function/method `times` times if the exceptions listed
        in ``exceptions`` are thrown
        :param times: The number of times to repeat the wrapped function/method
        :type times: Int
        :param Exceptions: Lists of exceptions that trigger a retry attempt
        :type Exceptions: Tuple of Exceptions
    """
    def decorator(func):
        def newfn(*args, **kwargs):
            attempt = 0
            while attempt < times:
                try:
                    return func(*args, **kwargs)
                except:
                    attempt += 1
                    logging.warning(f'Attempt {str(attempt)} failed. Retrying.')
            return func(*args, **kwargs)
        return newfn
    return decorator


@retry(times=3)
def test_cases_to_table(test_case_response, qtest_fields, client):

    table_response = client.call_chat([
                            {"role": "system", "content": test_case_response},
                            {"role": "user", "content": prompts.spreadsheet}
                            ], seed = None)
    req_table, test_case_count = format_qtest_template(table_response, qtest_fields)

    return req_table, test_case_count


def get_test_case_csv(reqs, qtest, qtest_fields, client, seed = 1):
    
    try:

        reqs = reqs.replace('#teststeps', '').replace('REQ:', '')

        reqs = reqs.replace('|', '%%%')

        reformat_reqs = client.call_chat([{"role": "system", "content": prompts.test_case_sys}, 
                                        {"role": "user","content": prompts.gherkin_reformat.format(requirements_input = reqs)}
                                    ], seed = seed)
        test_case_response = client.call_chat([{"role": "system", "content": prompts.test_case_sys}, 
                                            {"role": "user","content": prompts.test_cases.format(requirements_input = reformat_reqs)}
                                        ], seed = seed)
        if qtest == False:
            test_case_csv_string = pd.DataFrame({'A': [1, 2], 'B': [3, 4]}).to_csv(index=False)
            test_case_count = ''
            return test_case_csv_string, test_case_response, test_case_count

        req_table, test_case_count = test_cases_to_table(test_case_response, qtest_fields, client)

        test_case_csv_string = req_table.to_csv(index = False)
        test_case_csv_string_pipe = req_table.to_csv(index = False, sep = '|')    
    except:
        test_case_csv_string = pd.DataFrame({'A': [1, 2], 'B': [3, 4]}).to_csv(index=False)
        test_case_csv_string_pipe = pd.DataFrame({'A': [1, 2], 'B': [3, 4]}).to_csv(index=False, sep = '|')

    return test_case_csv_string, test_case_csv_string_pipe, test_case_response, test_case_count


