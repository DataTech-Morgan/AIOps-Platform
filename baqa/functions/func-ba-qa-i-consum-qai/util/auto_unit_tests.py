# imports needed to run the code in this notebook
# import ast  # used for detecting whether generated Python code is valid
import os
from openai import AzureOpenAI
from azure.identity import ClientSecretCredential
from util.text_processing import *
import json
from util.helper import get_openai_client
import time

def detect_language(code_to_test, client):
        # Step 0: Detect language.
    language_messages = [
        {
            "role": "system",
            "content": "You are a bot that can detect what programming language is being used given a short snippet of code. You give one word responses, only with the name of the programming language.",
        }, 
        {
            "role": "user",
            "content": f"""
```
{code_to_test[:500]}
```""",
        }
    ]

    language_used = client.call_chat(
        messages=language_messages,
        temperature=client.temperature)

    return language_used



def explain_code(code_to_test, user_story, client):
    # create a markdown-formatted message that asks GPT to explain the function, formatted as a bullet list
    explain_system_message = {
        "role": "system",
        "content": f"You are a world-class developer with an eagle eye for unintended bugs and edge cases, and business understanding. You carefully explain code with great detail and accuracy, and have the ability to map code back to business requirements. You organize your explanations in markdown-formatted, bulleted lists."
    }

    explain_user_message = {
        "role": "user",
        "content": f"""Please explain the following code. Review what each element of the code is doing precisely and what the author's intentions may have been. Please use the User Story corresponding to the code to understand what the code is doing precisely and its intent. Organize your explanation as a markdown-formatted, bulleted list.

```
User story:
{user_story}
```

```code
{code_to_test}
```"""
    }

    explain_messages = [explain_system_message, explain_user_message]

    explanation = client.call_chat(
        messages=explain_messages,
        temperature=client.temperature)

    explain_assistant_message = {"role": "assistant", "content": explanation}
    explain_message_set = [explain_system_message, explain_user_message, explain_assistant_message]

    return explain_message_set



def create_test_plan(explain_message_set, unit_test_framework = None, client = None):
    # Asks GPT to plan out cases the units tests should cover, formatted as a bullet list
    unit_test_framework_msg = ''
    if unit_test_framework is not None:     
        unit_test_framework_msg = f'\n    - Take advantage of the features of `{unit_test_framework}` to make the tests easy to write and maintain'
    
    plan_user_message = {
        "role": "user",
        "content": f"""A good unit test suite should aim to:
    - Test the code's behavior for a wide range of possible inputs
    - Test edge cases that the author may not have foreseen{unit_test_framework_msg}
    - Be easy to read and understand, with clean code and descriptive names
    - Be deterministic, so that the tests always pass or fail in the same way

To help unit test the code above, list diverse scenarios that the code should be able to handle (and under each scenario, include a few examples as sub-bullets). Please number the scenarios.""",
    }
    plan_messages = explain_message_set + [plan_user_message]

    plan = client.call_chat(
        messages=plan_messages,
        temperature=client.temperature)
    plan_message_set = [plan_user_message, {"role": "assistant", "content": plan}]

    return plan_message_set, plan



# Step 3: Generate the unit test
def generate_unit_test_code(execute_system_message, execute_user_message, explain_message_set, plan_message_set, client):
    # create a markdown-formatted prompt that asks GPT to complete a unit test

    short_explain_user_msg = {
        "role": "user",
        "content": f"""Please explain my following code. Review what each element of the code is doing precisely and what the author's intentions may have been. Please use the User Story corresponding to the code to understand what the code is doing precisely and its intent. Organize your explanation as a markdown-formatted, bulleted list."""
    }

    execute_messages = [execute_system_message] + [short_explain_user_msg, explain_message_set[-1]] + plan_message_set + [execute_user_message]

    execution = client.call_chat(
        messages=execute_messages,
        temperature=client.temperature)
    print(execution)
    # can check the output for errors with ast/another openai call
    # code = execution.split("```")[-1].split("```")[0].strip()
    code = execution.strip()
    
    # return the unit test as a string
    return code


# Uses a multi-step prompt to write unit tests
def create_unit_tests(
    client,
    code_to_test: str,  # Python function to test, as a string
    unit_test_framework: str = None,  # unit testing package; use the name as it appears in the import statement
    requirements: str = None,
    temperature: float = 0.4  # temperature = 0 can sometimes get stuck in repetitive loops, so we use 0.4
) -> str:
    """Returns a unit test for a given code, using a 3-step GPT prompt."""
    client.temperature = temperature

    # # Step 0: Detect language.
    # language_used = detect_language(code_to_test, client)
    # language_used = language_used.lower()
    # Step 1: Generate an explanation of the function (No AC/requirements available?)
    explain_message_set = explain_code(code_to_test, requirements, client)

    # Step 2: Generate a plan to write a unit test
    plan_message_set, test_plan = create_test_plan(explain_message_set, unit_test_framework, client)

    package_comment = ""
    if unit_test_framework == "pytest":
        package_comment = "# below, each test case is represented by a tuple passed to the @pytest.mark.parametrize decorator"
    
    execute_system_message = {
        "role": "system",
        "content": f"You are a world-class developer with an eagle eye for unintended bugs and edge cases. You write careful, accurate unit tests. When asked to reply only with code, you write all of your code in a single block.",
    }

    execute_user_message =  {
            "role": "user",
            "content": f"""Using the same language, write a suite of unit tests for the code below, following the cases above. 
Here is the code to test:
```
{code_to_test}
```

Include helpful comments to explain each line. Reply only with code, formatted as follows:
```<insert language name here>
# packages
{{insert other packages and imports as needed}} 

# unit tests
{package_comment}
{{insert unit test code here}}
```""",
        }

    if unit_test_framework is not None:
        execute_user_message = {
            "role": "user",
            "content": f"""Using the `{unit_test_framework}` package, write a suite of unit tests for the code below, following the cases above. 
Here is the code to test:
```
{code_to_test}
```

Include helpful comments to explain each line. Reply only with code, formatted as follows:
```<insert language name here>
# packages
# use/import {unit_test_framework} for our unit tests
{{insert other packages and imports as needed}}

# unit tests with {unit_test_framework}
{package_comment}
{{insert unit test code here}}
```""",
        }
    
    code = generate_unit_test_code(execute_system_message, execute_user_message, explain_message_set, plan_message_set, client)

    return code, test_plan


