import os
import json
from dotenv import dotenv_values

env_file_path = 'BA-QA-I\consum.env'

# Load environment variables from the .env file
env_vars = dict(dotenv_values(env_file_path))
config = [{'name' : key, 'value' : val, 'slotSetting' : False} for key, val in env_vars.items()]

# Specify the path where you want to save the JSON file
json_file_path = 'BA-QA-I\consum_env.json'

# Write the JSON data to the JSON file
with open(json_file_path, 'w+') as f:
    json.dump(config, f, indent = 4)
