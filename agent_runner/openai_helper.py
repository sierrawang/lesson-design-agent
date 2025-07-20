from openai import OpenAI
import json
import random
import os

# Return an OpenAI client
def get_openai_client(logger=None):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    keys_filename = os.path.join(current_dir, 'openai_keys.json')
    with open(keys_filename) as f:
        keys = json.load(f)
        
        # Choose a random key from the provided keys
        rand_key = random.choice(keys)
        if logger:
            logger.info(f"Using API key: {rand_key['org']}")

        return OpenAI(api_key=rand_key['api_key'])

# Call the GPT chat completions API with the given model and messages
def call_gpt(client, model, messages):
    try:
        openai_response = client.chat.completions.create(
            model=model, 
            messages=messages 
            # max_tokens=1000 
        )
        return openai_response.choices[0].message.content, openai_response.usage.prompt_tokens, openai_response.usage.completion_tokens
    
    except Exception as e:
        print(f"Error calling GPT: {e}")
        return None